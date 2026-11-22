import type { ReactNode } from 'react'

interface Props {
  cargando: boolean
  error: string | null
  vacio?: boolean // true cuando la consulta salió bien pero no hay resultados
  textoVacio?: string
  onReintentar?: () => void
  children?: ReactNode // el contenido real, que solo se muestra si no hay carga, error ni vacío
}

// Toda pantalla que consulta la API muestra uno de estos estados: cargando, error, vacío o el contenido
export default function Estado({
  cargando,
  error,
  vacio = false,
  textoVacio = 'No hay resultados.',
  onReintentar,
  children,
}: Props) {
  if (cargando) {
    return (
      <div className="estado" role="status">
        <p>Cargando…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="estado" role="alert">
        <p>{error}</p>
        {onReintentar && (
          <button type="button" className="boton" onClick={onReintentar}>
            Reintentar
          </button>
        )}
      </div>
    )
  }

  if (vacio) {
    return (
      <div className="estado" role="status">
        <p>{textoVacio}</p>
      </div>
    )
  }

  return <>{children}</>
}
