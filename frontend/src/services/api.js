import axios from 'axios'

// Cliente HTTP central. La URL base proviene de la variable VITE_API_URL
// definida en el .env del frontend (o inyectada por docker-compose).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// Antes de cada peticion se anexa el token guardado, si existe.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('wallet_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Si el backend responde 401 se limpia la sesion local y se manda a /login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('wallet_token')
      localStorage.removeItem('wallet_user')
      if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api

// Funciones de conveniencia agrupadas por modulo
export const authApi = {
  register: (payload) => api.post('/auth/register', payload),
  login: (payload) => api.post('/auth/login', payload),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/users/me'),
  changePassword: (payload) => api.put('/users/me/password', payload),
}

export const paymentMethodsApi = {
  list: (params = {}) => api.get('/payment-methods', { params }),
  create: (payload) => api.post('/payment-methods', payload),
  detail: (id) => api.get(`/payment-methods/${id}`),
  deactivate: (id) => api.patch(`/payment-methods/${id}/deactivate`),
  remove: (id) => api.delete(`/payment-methods/${id}`),
}
