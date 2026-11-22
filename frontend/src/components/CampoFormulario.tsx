// Un campo de formulario: etiqueta + control (input o select) + mensaje de error.
// La etiqueta se une al control con htmlFor/id, y el error se asocia con aria-describedby.

export interface Opcion {
  valor: string
  etiqueta: string
}

interface Props {
  id: string
  etiqueta: string
  valor: string
  onCambio: (valor: string) => void
  tipo?: 'text' | 'time' | 'select'
  opciones?: Opcion[] // solo para tipo "select"
  textoOpcionVacia?: string // primera opción del select (valor ""), por ejemplo "Elige…" o "Todos"
  error?: string
  ayuda?: string
  maxLength?: number
}

export default function CampoFormulario({
  id,
  etiqueta,
  valor,
  onCambio,
  tipo = 'text',
  opciones = [],
  textoOpcionVacia = 'Elige…',
  error,
  ayuda,
  maxLength,
}: Props) {
  // Ids de los textos de apoyo, para que el lector de pantalla los lea junto con el campo
  const idError = `${id}-error`
  const idAyuda = `${id}-ayuda`
  const describedBy = [ayuda ? idAyuda : '', error ? idError : ''].filter(Boolean).join(' ') || undefined

  return (
    <div className="campo">
      <label htmlFor={id}>{etiqueta}</label>

      {tipo === 'select' ? (
        <select
          id={id}
          value={valor}
          onChange={(e) => onCambio(e.target.value)}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
        >
          <option value="">{textoOpcionVacia}</option>
          {opciones.map((o) => (
            <option key={o.valor} value={o.valor}>
              {o.etiqueta}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={id}
          type={tipo}
          value={valor}
          maxLength={maxLength}
          onChange={(e) => onCambio(e.target.value)}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
        />
      )}

      {ayuda && (
        <p id={idAyuda} className="campo-ayuda">
          {ayuda}
        </p>
      )}
      {error && (
        <p id={idError} className="campo-error">
          {error}
        </p>
      )}
    </div>
  )
}
