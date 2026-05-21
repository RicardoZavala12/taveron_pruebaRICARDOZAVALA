import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

// Envoltura que bloquea el acceso a rutas privadas sin token.
// Recuerda la ruta intentada para regresar a ella despues del login.
export default function ProtectedRoute({ children }) {
  const { token } = useAuth()
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return children
}
