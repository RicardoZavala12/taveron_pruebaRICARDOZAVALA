import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Alert from '../components/Alert'
import { useAuth } from '../context/AuthContext'

// Pantalla de registro. Validaciones del cliente intencionalmente blandas:
// la validacion estricta corre en el backend para evitar duplicidad de logica.
export default function RegisterPage() {
  const { register, loading } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', full_name: '', password: '' })
  const [error, setError] = useState('')

  const update = (field) => (event) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }))

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await register(form)
      navigate('/methods', { replace: true })
    } catch (err) {
      const message = err?.response?.data?.detail || 'No fue posible registrar la cuenta'
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
            Crea tu cuenta en menos de un minuto.
          </h1>
          <p className="mt-4 max-w-md text-white/80">
            Tus datos sensibles se cifran antes de tocar la base. Tu wallet,
            tu informacion.
          </p>
        </div>
        <p className="text-sm text-white/60">Wallet segura de metodos de pago</p>
      </aside>

      <section className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <h2 className="text-3xl font-extrabold tracking-tight">Crear cuenta</h2>
          <p className="mt-2 text-slate-500">
            Solo necesitamos un correo y una contrasena segura.
          </p>

          <form onSubmit={submit} className="mt-8 space-y-4">
            <div>
              <label className="label" htmlFor="full_name">Nombre completo</label>
              <input
                id="full_name"
                type="text"
                className="input"
                required
                minLength={2}
                value={form.full_name}
                onChange={update('full_name')}
              />
            </div>
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
                autoComplete="new-password"
                required
                minLength={8}
                value={form.password}
                onChange={update('password')}
              />
              <p className="mt-1 text-xs text-slate-500">
                Minimo 8 caracteres, debe incluir al menos una letra y un numero.
              </p>
            </div>

            <Alert kind="error">{error}</Alert>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Creando cuenta...' : 'Crear cuenta'}
            </button>
          </form>

          <p className="mt-6 text-sm text-slate-500">
            Ya tienes una cuenta?{' '}
            <Link to="/login" className="font-semibold text-brand-600 hover:underline">
              Inicia sesion
            </Link>
          </p>
        </div>
      </section>
    </div>
  )
}
