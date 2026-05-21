import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Alert from '../components/Alert'
import Navbar from '../components/Navbar'
import { paymentMethodsApi } from '../services/api'

// Detalle de un metodo de pago. Permite desactivarlo o eliminarlo (soft delete).
// La eliminacion solicita confirmacion para evitar accidentes.
const TYPE_LABELS = {
  card: 'Tarjeta',
  bank_account: 'Cuenta bancaria',
  clabe: 'CLABE',
  other: 'Otro',
}

export default function MethodDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [method, setMethod] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      try {
        const { data } = await paymentMethodsApi.detail(id)
        if (!cancelled) setMethod(data)
      } catch (err) {
        if (!cancelled) setError(err?.response?.data?.detail || 'No se pudo cargar el metodo')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [id])

  const deactivate = async () => {
    setActionError('')
    setBusy(true)
    try {
      const { data } = await paymentMethodsApi.deactivate(id)
      setMethod(data)
    } catch (err) {
      setActionError(err?.response?.data?.detail || 'No se pudo desactivar')
    } finally {
      setBusy(false)
    }
  }

  const remove = async () => {
    const confirmed = window.confirm(
      'Estas seguro de eliminar este metodo de pago? Esta accion conservara la trazabilidad pero el metodo dejara de aparecer en tus listados.',
    )
    if (!confirmed) return
    setActionError('')
    setBusy(true)
    try {
      await paymentMethodsApi.remove(id)
      navigate('/methods', { replace: true })
    } catch (err) {
      setActionError(err?.response?.data?.detail || 'No se pudo eliminar el metodo')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <Link to="/methods" className="text-sm text-slate-500 hover:text-slate-700">
          {'<- Volver al listado'}
        </Link>

        {loading ? (
          <div className="card mt-6 text-center text-slate-500">Cargando...</div>
        ) : error ? (
          <div className="mt-6">
            <Alert kind="error">{error}</Alert>
          </div>
        ) : method ? (
          <>
            <h1 className="mt-2 text-3xl font-extrabold tracking-tight">{method.alias}</h1>
            <p className="mt-1 text-slate-500">{TYPE_LABELS[method.type]} en {method.institution}</p>

            <section className="mt-8 overflow-hidden rounded-card bg-gradient-to-br from-brand-700 via-brand-500 to-aqua-400 p-8 text-white shadow-soft">
              <p className="text-xs uppercase tracking-widest text-white/70">{TYPE_LABELS[method.type]}</p>
              <p className="mt-6 font-mono text-3xl tracking-widest">
                <span aria-hidden>{'•••• •••• •••• '}</span>
                <span>{method.identifier_last4}</span>
              </p>
              <div className="mt-10 flex items-end justify-between">
                <div>
                  <p className="text-xs uppercase tracking-widest text-white/60">Institucion</p>
                  <p className="text-sm font-semibold">{method.institution}</p>
                </div>
                <span className="rounded-pill bg-white/10 px-3 py-1 text-xs font-semibold">
                  {method.currency}
                </span>
              </div>
            </section>

            <section className="card mt-8">
              <h2 className="text-lg font-bold">Detalles</h2>
              <dl className="mt-4 space-y-3 text-sm">
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <dt className="text-slate-500">Tipo</dt>
                  <dd className="font-semibold">{TYPE_LABELS[method.type]}</dd>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <dt className="text-slate-500">Alias</dt>
                  <dd className="font-semibold">{method.alias}</dd>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <dt className="text-slate-500">Institucion</dt>
                  <dd className="font-semibold">{method.institution}</dd>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <dt className="text-slate-500">Moneda</dt>
                  <dd className="font-semibold">{method.currency}</dd>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <dt className="text-slate-500">Ultimos 4</dt>
                  <dd className="font-mono font-semibold">{method.identifier_last4}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Estatus</dt>
                  <dd className="font-semibold capitalize">
                    {method.status === 'active' ? 'Activo' : 'Inactivo'}
                  </dd>
                </div>
              </dl>
            </section>

            {actionError && <div className="mt-6"><Alert kind="error">{actionError}</Alert></div>}

            <section className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-end">
              {method.status === 'active' && (
                <button type="button" className="btn-secondary" onClick={deactivate} disabled={busy}>
                  Desactivar
                </button>
              )}
              <button type="button" className="btn-danger" onClick={remove} disabled={busy}>
                Eliminar
              </button>
            </section>
          </>
        ) : null}
      </main>
    </div>
  )
}
