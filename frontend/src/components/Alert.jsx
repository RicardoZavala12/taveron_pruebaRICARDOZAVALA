// Componente simple para mostrar mensajes de error o exito en los formularios.
// Se mantiene minimalista para no robar protagonismo al resto del UI.
export default function Alert({ kind = 'error', children }) {
  if (!children) return null
  const tone =
    kind === 'success'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
      : 'border-red-200 bg-red-50 text-red-800'
  return (
    <div className={`rounded-xl border px-4 py-3 text-sm ${tone}`}>{children}</div>
  )
}
