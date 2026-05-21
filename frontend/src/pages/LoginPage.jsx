import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Alert from '../components/Alert'
import { useAuth } from '../context/AuthContext'

// Pantalla de inicio de sesion.
// Fondo a dos columnas: el hero con gradiente (lado de marca) y el formulario
// en una tarjeta blanca con bordes redondeados.
export default function LoginPage() {
  const { login, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const update = (field) => (event) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }))

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await login(form)
      const target = location.state?.from || '/methods'
      navigate(target, { replace: true })
    } catch (err) {
      const message = err?.response?.data?.detail || 'No fue posible iniciar sesion'
      setError(message)
    }
  }

  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      <aside className="relative hidden flex-col justify-between bg-hero p-12 text-white lg:flex">
        <Link to="/" className="text-2xl font-extrabold">
          wallet<span className="text-aqua-400">.</span>
        </Link>
        <div>
          <h1 className="text-4xl font-extrabold leading-tight">
            Administra tus metodos de pago con confianza.
          </h1>
          <p className="mt-4 max-w-md text-white/80">
            Guarda tarjetas, cuentas y CLABE en un solo lugar. Cifrado en reposo
            y trazabilidad de cada operacion relevante.
          </p>
        </div>
        <p className="text-sm text-white/60">Wallet segura de metodos de pago</p>
      </aside>

      <section className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <h2 className="text-3xl font-extrabold tracking-tight">Iniciar sesion</h2>
          <p className="mt-2 text-slate-500">
            Ingresa tus credenciales para acceder a tu wallet.
          </p>

          <form onSubmit={submit} className="mt-8 space-y-4">
            <div>
              <label className="label" htmlFor="email">Correo electronico</label>
              <input
                id="email"
                type="email"
                className="input"
                autoComplete="email"
                required
                value={form.email}
                onChange={update('email')}
              />
            </div>
            <div>
              <label className="label" htmlFor="password">Contrasena</label>
              <input
                id="password"
                type="password"
                className="input"
                autoComplete="current-password"
                required
                value={form.password}
                onChange={update('password')}
              />
            </div>

            <Alert kind="error">{error}</Alert>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>

          <p className="mt-6 text-sm text-slate-500">
            No tienes cuenta?{' '}
            <Link to="/register" className="font-semibold text-brand-600 hover:underline">
              Registrate
            </Link>
          </p>
        </div>
      </section>
    </div>
  )
}
