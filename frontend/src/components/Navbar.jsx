import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

// Barra superior consistente en todas las pantallas autenticadas.
// Sigue el patron visual de Taveron: logo a la izquierda, navegacion al centro
// y boton tipo pill (blanco) a la derecha.
export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="text-xl font-extrabold tracking-tight text-ink-900">
          wallet<span className="text-brand-500">.</span>
        </Link>

        <nav className="hidden items-center gap-8 text-sm font-semibold text-slate-700 md:flex">
          <Link className="hover:text-brand-500" to="/methods">Metodos de pago</Link>
          <Link className="hover:text-brand-500" to="/profile">Perfil</Link>
        </nav>

        <div className="flex items-center gap-3">
          {user && (
            <span className="hidden text-sm text-slate-500 md:inline">
              {user.full_name}
            </span>
          )}
          <button type="button" onClick={handleLogout} className="btn-secondary">
            Cerrar sesion
          </button>
        </div>
      </div>
    </header>
  )
}
