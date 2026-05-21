import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import PasswordChangeForm from '../components/PasswordChangeForm'
import { useAuth } from '../context/AuthContext'

// Vista de perfil del usuario autenticado. Funciona tambien como vista principal
// despues del login: muestra los datos basicos y un acceso directo al listado.
export default function ProfilePage() {
  const { user, refreshProfile } = useAuth()

  useEffect(() => {
    // Refresca por si el backend tiene datos mas recientes que el cache local.
    refreshProfile().catch(() => undefined)
  }, [refreshProfile])

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <h1 className="text-3xl font-extrabold tracking-tight">Hola, {user?.full_name?.split(' ')[0]}</h1>
        <p className="mt-2 text-slate-500">Esta es la informacion de tu cuenta.</p>

        <section className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="card">
            <h2 className="text-lg font-bold">Tu perfil</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <dt className="text-slate-500">Nombre</dt>
                <dd className="font-semibold">{user?.full_name}</dd>
              </div>
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <dt className="text-slate-500">Correo</dt>
                <dd className="font-semibold">{user?.email}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Cuenta creada</dt>
                <dd className="font-semibold">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                </dd>
              </div>
            </dl>
          </div>

          <div className="card flex flex-col justify-between bg-ink-900 text-white">
            <div>
              <h2 className="text-lg font-bold">Tus metodos de pago</h2>
              <p className="mt-2 text-sm text-white/70">
                Administra tarjetas, cuentas bancarias y CLABE de forma centralizada.
              </p>
            </div>
            <Link to="/methods" className="btn-pill mt-6 self-start">
              Ver mis metodos
              <span aria-hidden>{'>'}</span>
            </Link>
          </div>
        </section>

        <section className="mt-6">
          <PasswordChangeForm />
        </section>
      </main>
    </div>
  )
}
