import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import PaymentMethodCard from '../components/PaymentMethodCard'
import WalletStack from '../components/WalletStack'
import Alert from '../components/Alert'
import { paymentMethodsApi } from '../services/api'

// Listado de metodos de pago con dos modos de visualizacion:
// - "wallet": stack estilo Apple Wallet en desktop, grid en mobile.
// - "all": grid de cards con paginacion para revisarlos todos.
// El modo se controla con el query param view=all.
export default function MethodsListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const view = searchParams.get('view') === 'all' ? 'all' : 'wallet'

  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [size] = useState(view === 'all' ? 12 : 50)
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = { page, size }
      if (typeFilter) params.type = typeFilter
      if (statusFilter) params.status = statusFilter
      const { data } = await paymentMethodsApi.list(params)
      setItems(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(err?.response?.data?.detail || 'No fue posible cargar los metodos')
    } finally {
      setLoading(false)
    }
  }, [page, size, typeFilter, statusFilter])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / size)), [total, size])

  const switchToAll = () => {
    setPage(1)
    setSearchParams({ view: 'all' })
  }

  const switchToWallet = () => {
    setPage(1)
    setSearchParams({})
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">Mis metodos de pago</h1>
            <p className="mt-2 text-slate-500">
              {total === 0
                ? 'Aun no tienes metodos registrados.'
                : `Tienes ${total} ${total === 1 ? 'metodo' : 'metodos'} registrados.`}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            {view === 'all' ? (
              <button type="button" className="btn-secondary" onClick={switchToWallet}>
                Volver al wallet
              </button>
            ) : (
              total > 0 && (
                <button type="button" className="btn-secondary" onClick={switchToAll}>
                  Ver todos
                </button>
              )
            )}
            <Link to="/methods/new" className="btn-primary">
              Agregar metodo
              <span aria-hidden>{'+'}</span>
            </Link>
          </div>
        </header>

        {view === 'all' && (
          <section className="mt-6 flex flex-wrap gap-3 rounded-card bg-white p-4 shadow-soft">
            <div>
              <label className="label" htmlFor="type-filter">Tipo</label>
              <select
                id="type-filter"
                className="input"
                value={typeFilter}
                onChange={(e) => { setTypeFilter(e.target.value); setPage(1) }}
              >
                <option value="">Todos</option>
                <option value="card">Tarjeta</option>
                <option value="bank_account">Cuenta bancaria</option>
                <option value="clabe">CLABE</option>
                <option value="other">Otro</option>
              </select>
            </div>
            <div>
              <label className="label" htmlFor="status-filter">Estatus</label>
              <select
                id="status-filter"
                className="input"
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
              >
                <option value="">Todos</option>
                <option value="active">Activo</option>
                <option value="inactive">Inactivo</option>
              </select>
            </div>
          </section>
        )}

        {error && <div className="mt-6"><Alert kind="error">{error}</Alert></div>}

        <section className="mt-8">
          {loading ? (
            <div className="rounded-card bg-white p-10 text-center text-slate-500 shadow-soft">
              Cargando metodos...
            </div>
          ) : items.length === 0 ? (
            <div className="rounded-card bg-white p-10 text-center shadow-soft">
              <p className="text-lg font-semibold">No hay metodos para mostrar</p>
              <p className="mt-2 text-slate-500">
                Comienza registrando tu primera tarjeta o cuenta bancaria.
              </p>
              <Link to="/methods/new" className="btn-primary mt-6 inline-flex">
                Agregar metodo
              </Link>
            </div>
          ) : view === 'wallet' ? (
            // Stack apilado tipo Apple Wallet en todos los tamanos.
            // En desktop la interaccion es por hover; en mobile el primer tap
            // eleva la card y el segundo navega al detalle (logica dentro de
            // WalletStack).
            <WalletStack methods={items} totalAvailable={total} />
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((method) => (
                <div key={method.id} className="h-[220px]">
                  <PaymentMethodCard method={method} />
                </div>
              ))}
            </div>
          )}
        </section>

        {view === 'all' && total > size && (
          <nav className="mt-8 flex items-center justify-center gap-2">
            <button
              type="button"
              className="btn-secondary"
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Anterior
            </button>
            <span className="px-4 text-sm text-slate-500">
              Pagina {page} de {totalPages}
            </span>
            <button
              type="button"
              className="btn-secondary"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Siguiente
            </button>
          </nav>
        )}
      </main>
    </div>
  )
}
