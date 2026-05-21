import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import MethodsListPage from './pages/MethodsListPage'
import NewMethodPage from './pages/NewMethodPage'
import MethodDetailPage from './pages/MethodDetailPage'

// Router central. Las rutas privadas se envuelven con ProtectedRoute para
// redirigir a /login cuando no hay token.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/methods" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/methods"
        element={
          <ProtectedRoute>
            <MethodsListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/methods/new"
        element={
          <ProtectedRoute>
            <NewMethodPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/methods/:id"
        element={
          <ProtectedRoute>
            <MethodDetailPage />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/methods" replace />} />
    </Routes>
  )
}
