import { Link } from 'react-router-dom'

// Tarjeta visual que simula una tarjeta fisica al estilo Apple Wallet.
// Se usa tanto en el grid de mobile como apilada dentro de WalletStack.
// Cada tipo recibe su propio gradiente para que el listado se vea variado.

const GRADIENTS = {
  card: 'from-brand-700 via-brand-500 to-aqua-400',
  bank_account: 'from-slate-800 via-slate-700 to-slate-500',
  clabe: 'from-emerald-700 via-emerald-500 to-aqua-400',
  other: 'from-indigo-700 via-indigo-500 to-purple-400',
}

const TYPE_LABELS = {
  card: 'Tarjeta',
  bank_account: 'Cuenta bancaria',
  clabe: 'CLABE',
  other: 'Otro',
}

// Icono de wifi/contactless dibujado en SVG para no depender de assets.
function ContactlessIcon({ className = '' }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M8.5 8.5a5 5 0 0 1 0 7" />
      <path d="M11.5 5.5a9 9 0 0 1 0 13" />
      <path d="M14.5 2.5a13 13 0 0 1 0 19" />
    </svg>
  )
}

function ChipIcon({ className = '' }) {
  return (
    <svg className={className} viewBox="0 0 32 24" aria-hidden>
      <rect x="1" y="1" width="30" height="22" rx="4" fill="url(#chipGrad)" stroke="rgba(255,255,255,0.45)" />
      <path
        d="M8 6 v12 M16 6 v12 M24 6 v12 M4 10 h24 M4 14 h24"
        stroke="rgba(255,255,255,0.55)"
        strokeWidth="1"
        fill="none"
      />
      <defs>
        <linearGradient id="chipGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f4d089" />
          <stop offset="60%" stopColor="#caa14a" />
          <stop offset="100%" stopColor="#8c6b22" />
        </linearGradient>
      </defs>
    </svg>
  )
}

export default function PaymentMethodCard({ method, asLink = true }) {
  const gradient = GRADIENTS[method.type] || GRADIENTS.other
  const label = TYPE_LABELS[method.type] || 'Metodo'
  const isInactive = method.status === 'inactive'

  const inner = (
    <div
      className={`relative h-full w-full overflow-hidden rounded-card bg-gradient-to-br ${gradient} p-6 text-white shadow-soft`}
    >
      {/* Brillo sutil arriba para darle volumen */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-1/2 bg-gradient-to-b from-white/15 to-transparent" />

      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/70">{label}</p>
          <p className="mt-1 text-lg font-semibold leading-tight">{method.alias}</p>
        </div>
        <span
          className={`rounded-pill px-3 py-1 text-[10px] font-semibold uppercase tracking-wider ${
            isInactive ? 'bg-white/20 text-white/80' : 'bg-white/90 text-ink-900'
          }`}
        >
          {isInactive ? 'Inactivo' : 'Activo'}
        </span>
      </div>

      <div className="relative mt-6 flex items-center gap-3">
        <ChipIcon className="h-7 w-9 drop-shadow" />
        <ContactlessIcon className="h-5 w-5 text-white/80" />
      </div>

      <p className="relative mt-4 font-mono text-xl tracking-[0.25em]">
        <span aria-hidden>{'•••• •••• •••• '}</span>
        <span>{method.identifier_last4}</span>
      </p>

      <div className="relative mt-5 flex items-end justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/60">Institucion</p>
          <p className="text-sm font-semibold">{method.institution}</p>
        </div>
        <span className="rounded-pill bg-white/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider">
          {method.currency}
        </span>
      </div>
    </div>
  )

  if (!asLink) return inner

  return (
    <Link to={`/methods/${method.id}`} className="block h-full w-full">
      {inner}
    </Link>
  )
}
