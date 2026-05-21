import { useState } from 'react'
import { authApi } from '../services/api'
import Alert from './Alert'

// Formulario para cambiar la contrasena del usuario autenticado.
// Pide la contrasena actual + la nueva (con confirmacion) y delega la
// validacion estricta al backend. Tras un cambio exitoso se limpian los
// campos y se muestra un mensaje de confirmacion.
export default function PasswordChangeForm() {
  const [form, setForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const update = (field) => (event) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }))

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (form.new_password !== form.confirm_password) {
      setError('La nueva contrasena y su confirmacion no coinciden')
      return
    }

    setSubmitting(true)
    try {
      await authApi.changePassword({
        current_password: form.current_password,
        new_password: form.new_password,
      })
      setSuccess('Tu contrasena se actualizo correctamente')
      setForm({ current_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      const detail = err?.response?.data?.detail
      // Si Pydantic devuelve un detail tipo array (422), se aplana a texto.
      const message = Array.isArray(detail)
        ? detail.map((d) => d.msg).join(', ')
        : detail || 'No fue posible actualizar la contrasena'
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={submit} className="card">
      <h2 className="text-lg font-bold">Cambiar contrasena</h2>
      <p className="mt-1 text-sm text-slate-500">
        Por seguridad necesitamos confirmar tu contrasena actual antes de
        actualizarla.
      </p>

      <div className="mt-5 space-y-4">
        <div>
          <label className="label" htmlFor="current_password">Contrasena actual</label>
          <input
            id="current_password"
            type="password"
            className="input"
            autoComplete="current-password"
            required
            value={form.current_password}
            onChange={update('current_password')}
          />
        </div>
        <div>
          <label className="label" htmlFor="new_password">Nueva contrasena</label>
          <input
            id="new_password"
            type="password"
            className="input"
            autoComplete="new-password"
            required
            minLength={8}
            value={form.new_password}
            onChange={update('new_password')}
          />
          <p className="mt-1 text-xs text-slate-500">
            Minimo 8 caracteres, debe incluir al menos una letra y un numero.
          </p>
        </div>
        <div>
          <label className="label" htmlFor="confirm_password">Confirmar nueva contrasena</label>
          <input
            id="confirm_password"
            type="password"
            className="input"
            autoComplete="new-password"
            required
            minLength={8}
            value={form.confirm_password}
            onChange={update('confirm_password')}
          />
        </div>

        <Alert kind="error">{error}</Alert>
        <Alert kind="success">{success}</Alert>

        <div className="flex justify-end">
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? 'Guardando...' : 'Actualizar contrasena'}
          </button>
        </div>
      </div>
    </form>
  )
}
