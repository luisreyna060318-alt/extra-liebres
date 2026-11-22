import { TAMANO_PAGINA } from '../api/grupos.ts'

interface Props {
  etiqueta: string // nombre de la navegación para lectores de pantalla, por ejemplo "Paginación de promotores"
  pagina: number
  total: number // total de resultados que informa el servidor
  onCambiar: (pagina: number) => void
}

// Botones Anterior / Siguiente con "Página X de Y" (el servidor entrega 10 resultados por página)
export default function Paginacion({ etiqueta, pagina, total, onCambiar }: Props) {
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_PAGINA))

  return (
    <nav className="paginacion" aria-label={etiqueta}>
      <button type="button" className="boton boton-secundario" disabled={pagina <= 1} onClick={() => onCambiar(pagina - 1)}>
        Anterior
      </button>
      <span>
        Página {pagina} de {totalPaginas}
      </span>
      <button type="button" className="boton boton-secundario" disabled={pagina >= totalPaginas} onClick={() => onCambiar(pagina + 1)}>
        Siguiente
      </button>
    </nav>
  )
}
