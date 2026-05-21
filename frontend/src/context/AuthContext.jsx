import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authApi } from '../services/api'

// El contexto expone el usuario, el token y las funciones de login/logout/register.
// La persistencia es en localStorage para que el refresh no rompa la sesion.
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('wallet_user')
    return raw ? JSON.parse(raw) : null
  })
  const [token, setToken] = useState(() => localStorage.getItem('wallet_token'))
  const [loading, setLoading] = useState(false)

  // Persistencia automatica del usuario
  useEffect(() => {
    if (user) {
      localStorage.setItem('wallet_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('wallet_user')
    }
  }, [user])

  useEffect(() => {
    if (token) {
      localStorage.setItem('wallet_token', token)
    } else {
      localStorage.removeItem('wallet_token')
    }
  }, [token])

  const login = useCallback(async (credentials) => {
    setLoading(true)
    try {
      const { data } = await authApi.login(credentials)
      setToken(data.access_token)
      setUser(data.user)
      return data.user
    } finally {
      setLoading(false)
    }
  }, [])

  const register = useCallback(async (payload) => {
    setLoading(true)
    try {
      await authApi.register(payload)
      // Tras registrar se hace login automatico para mejorar la UX.
      return await login({ email: payload.email, password: payload.password })
    } finally {
      setLoading(false)
    }
  }, [login])

  const logout = useCallback(async () => {
    try {
      if (token) {
        await authApi.logout()
      }
    } catch {
      // No bloquea el logout local si el backend no respondio.
    } finally {
      setToken(null)
      setUser(null)
    }
  }, [token])

  const refreshProfile = useCallback(async () => {
    if (!token) return null
    const { data } = await authApi.me()
    setUser(data)
    return data
  }, [token])

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout, refreshProfile }),
    [user, token, loading, login, register, logout, refreshProfile],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider')
  }
  return ctx
}
