import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import PaymentMethodCard from './PaymentMethodCard'

// Pila de tarjetas estilo Apple Wallet, funcional tanto en desktop como mobile.
//
// Cada card vive en posicion absoluta, con un offset vertical proporcional a su
// indice. La interaccion es por hover en desktop y por tap en mobile:
//
// - Desktop: pasar el mouse eleva la card y las que estan debajo se desplazan.
//   Click directo navega al detalle.
// - Mobile: el primer tap eleva la card (y desplaza las siguientes). El segundo
//   tap sobre la misma card activa el detalle. Asi el usuario puede "abrir"
//   visualmente el stack antes de comprometerse a entrar a una tarjeta.
//
// El stack solo muestra hasta VISIBLE_LIMIT cards; si hay mas, aparece un boton
// "Ver todos" que cambia la vista a una grilla paginada.

const CARD_HEIGHT = 220
const STACK_GAP = 56
const PEEK_OFFSET = 170
const VISIBLE_LIMIT = 6

export default function WalletStack({ methods, totalAvailable }) {
  const [activeIndex, setActiveIndex] = useState(null)
  const navigate = useNavigate()

  const visibleMethods = methods.slice(0, VISIBLE_LIMIT)
  const stackHeight =
    CARD_HEIGHT + (visibleMethods.length - 1) * STACK_GAP + PEEK_OFFSET

  const handleCardClick = (index, method) => (event) => {
    // En desktop el hover ya marco la card como activa. En mobile el primer tap
    // la marca, el segundo entra al detalle.
    if (activeIndex !== index) {
      event.preventDefault()
      setActiveIndex(index)
      return
    }
    navigate(`/methods/${method.id}`)
  }

  return (
    <div
      className="relative mx-auto w-full max-w-md"
      style={{ height: stackHeight }}
      onMouseLeave={() => setActiveIndex(null)}
    >
      {visibleMethods.map((method, index) => {
        const isHovered = activeIndex === index
        const isAfterHovered = activeIndex !== null && index > activeIndex

        let translateY = index * STACK_GAP
        if (isAfterHovered) {
          translateY += PEEK_OFFSET
        }
        if (isHovered) {
          translateY -= 12
        }

        const scale = isHovered ? 1.03 : 1
        const zIndex = isHovered ? 100 : index + 1
        const shadow = isHovered
          ? '0 30px 60px -20px rgba(15, 34, 55, 0.55)'
          : '0 18px 40px -22px rgba(15, 34, 55, 0.4)'

        return (
          <div
            key={method.id}
            role="button"
            tabIndex={0}
            aria-label={`${method.alias}, ${method.institution}`}
            className="absolute left-0 right-0 h-[220px] cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
            style={{
              transform: `translateY(${translateY}px) scale(${scale})`,
              zIndex,
              boxShadow: shadow,
              borderRadius: 24,
              // Transicion estilo Apple Wallet: ~550ms con curva ease-in-out
              // suave para los movimientos y una salida mas larga para que el
              // box-shadow desaparezca sin abruptos.
              transition:
                'transform 550ms cubic-bezier(0.25, 1, 0.5, 1), box-shadow 700ms cubic-bezier(0.25, 1, 0.5, 1)',
            }}
            onMouseEnter={() => setActiveIndex(index)}
            onFocus={() => setActiveIndex(index)}
            onClick={handleCardClick(index, method)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault()
                if (activeIndex !== index) setActiveIndex(index)
                else navigate(`/methods/${method.id}`)
              }
            }}
          >
            {/* asLink=false porque la navegacion la controla el handler del wrapper. */}
            <PaymentMethodCard method={method} asLink={false} />
          </div>
        )
      })}

      {totalAvailable > VISIBLE_LIMIT && (
        <div
          className="absolute inset-x-0 flex justify-center"
          style={{ top: stackHeight - 40 }}
        >
          <Link
            to="/methods?view=all"
            className="rounded-pill bg-white px-5 py-2 text-sm font-semibold text-ink-900 shadow-soft transition hover:bg-slate-100"
          >
            Ver todos ({totalAvailable})
          </Link>
        </div>
      )}
    </div>
  )
}
