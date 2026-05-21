import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Alert from '../components/Alert'
import Navbar from '../components/Navbar'
import { paymentMethodsApi } from '../services/api'

// Formulario de alta de un metodo de pago.
// La logica de validacion estricta vive en el backend; aqui solo se aplican
// reglas suaves (longitud minima, agrupar el numero en bloques) para mejorar
// la experiencia.
const TYPES = [
  { value: 'card', label: 'Tarjeta' },
  { value: 'bank_account', label: 'Cuenta bancaria' },
  { value: 'clabe', label: 'CLABE' },
  { value: 'other', label: 'Otro' },
]

const CURRENCIES = ['MXN', 'USD', 'EUR']

// Catalogo de instituciones financieras frecuentes en Mexico. Se incluye
// la opcion "Otra" para cuando la institucion no este en la lista; en ese
// caso el formulario muestra un input libre.
const INSTITUTIONS = [
  'BBVA',
  'Banamex',
  'Santander',
  'Banorte',
  'HSBC',
  'Scotiabank',
  'Inbursa',
  'Banco Azteca',
  'BanCoppel',
  'Banregio',
  'Afirme',
  'Banco del Bajio',
  'Mifel',
  'Multiva',
  'Banjercito',
  'American Express',
  'Nu',
  'Hey Banco',
  'Klar',
  'Mercado Pago',
  'PayPal',
  'Stori',
  'Rappi Pay',
  'DolarApp',
  'Albo',
  'Cuenca',
]
const OTHER_INSTITUTION = '__other__'

export default function NewMethodPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    type: 'card',
    alias: '',
    // institution_choice guarda el valor del select (un nombre del catalogo
    // o el sentinel OTHER_INSTITUTION). institution_custom guarda el texto
    // libre cuando el usuario elige "Otra".
    institution_choice: 'BBVA',
    institution_custom: '',
    currency: 'MXN',
    identifier: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const isOtherInstitution = form.institution_choice === OTHER_INSTITUTION
  const resolvedInstitution = isOtherInstitution
    ? form.institution_custom.trim()
    : form.institution_choice

  const update = (field) => (event) => {
    let value = event.target.value
    if (field === 'identifier' && form.type === 'card') {
      // Permite que el usuario escriba con o sin espacios, los normaliza visualmente
      value = value.replace(/\s|-/g, '').replace(/(.{4})/g, '$1 ').trim()
    }
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const submit = async (event) => {
    event.preventDefault()
    setError('')

    if (!resolvedInstitution) {
      setError('Selecciona o escribe el nombre de la institucion')
      return
    }

    setSubmitting(true)
    try {
      const payload = {
        type: form.type,
        alias: form.alias,
        currency: form.currency,
        institution: resolvedInstitution,
        identifier: form.identifier.replace(/\s/g, ''),
      }
      await paymentMethodsApi.create(payload)
      navigate('/methods', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'No fue posible registrar el metodo')
    } finally {
      setSubmitting(false)
    }
  }

  const identifierLabel = {
    card: 'Numero de tarjeta',
    bank_account: 'Numero de cuenta',
    clabe: 'CLABE',
    other: 'Identificador',
  }[form.type]

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <Link to="/methods" className="text-sm text-slate-500 hover:text-slate-700">
          {'<- Volver al listado'}
        </Link>
        <h1 className="mt-2 text-3xl font-extrabold tracking-tight">
          Agregar metodo de pago
        </h1>
        <p className="mt-2 text-slate-500">
          Tus datos sensibles se cifran antes de almacenarse. Solo conservamos los
          ultimos cuatro caracteres en claro para identificacion.
        </p>

        <form onSubmit={submit} className="card mt-8 space-y-5">
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label className="label" htmlFor="type">Tipo</label>
              <select
                id="type"
                className="input"
                value={form.type}
                onChange={(e) => setForm((prev) => ({ ...prev, type: e.target.value, identifier: '' }))}
              >
                {TYPES.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label" htmlFor="currency">Moneda</label>
              <select
                id="currency"
                className="input"
                value={form.currency}
                onChange={update('currency')}
              >
                {CURRENCIES.map((code) => (
                  <option key={code} value={code}>{code}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label className="label" htmlFor="alias">Alias</label>
              <input
                id="alias"
                type="text"
                className="input"
                placeholder="Ej. Tarjeta personal"
                required
                minLength={2}
                value={form.alias}
                onChange={update('alias')}
              />
            </div>
            <div>
              <label className="label" htmlFor="institution">Institucion</label>
              <select
                id="institution"
                className="input"
                value={form.institution_choice}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    institution_choice: e.target.value,
                    // Si el usuario regresa a una opcion del catalogo,
                    // se limpia el texto libre para evitar inconsistencias.
                    institution_custom:
                      e.target.value === OTHER_INSTITUTION ? prev.institution_custom : '',
                  }))
                }
              >
                {INSTITUTIONS.map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
                <option value={OTHER_INSTITUTION}>Otra...</option>
              </select>
              {isOtherInstitution && (
                <input
                  type="text"
                  className="input mt-2"
                  placeholder="Nombre de la institucion"
                  required
                  minLength={2}
                  value={form.institution_custom}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, institution_custom: e.target.value }))
                  }
                />
              )}
            </div>
          </div>

          <div>
            <label className="label" htmlFor="identifier">{identifierLabel}</label>
            <input
              id="identifier"
              type="text"
              inputMode="numeric"
              autoComplete="off"
              className="input font-mono tracking-widest"
              placeholder={form.type === 'card' ? '1234 5678 9012 3456' : 'Identificador'}
              required
              minLength={4}
              value={form.identifier}
              onChange={update('identifier')}
            />
            <p className="mt-1 text-xs text-slate-500">
              Acepta cualquier secuencia alfanumerica de 4 a 40 caracteres. El
              valor se cifra en el servidor; solo conservamos visibles los
              ultimos cuatro caracteres. No se permite repetir un identificador
              que ya hayas registrado.
            </p>
          </div>

          <Alert kind="error">{error}</Alert>

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Link to="/methods" className="btn-secondary">Cancelar</Link>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Guardando...' : 'Guardar metodo'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
