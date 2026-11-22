import { useEffect, useRef } from 'react'
import type { KeyboardEvent } from 'react'

interface Props {
  id: string // para unir el título y el texto con aria-labelledby / aria-describedby
  titulo: string
  texto: string
  textoConfirmar: string // por ejemplo "Sí, eliminar"
  enviando: boolean
  peligrosa?: boolean // true pinta el botón en rojo (eliminar, suspender)
  nivelTitulo?: 2 | 3 // h2 si el panel va justo debajo del h1 (sin h2 antes); h3 si va dentro de una sección con h2
  onConfirmar: () => void
  onCancelar: () => void
}

// Panel de confirmación dentro de la página (no es un modal): nada se envía hasta pulsar el botón de confirmar.
export default function Confirmacion({ id, titulo, texto, textoConfirmar, enviando, peligrosa = true, nivelTitulo = 3, onConfirmar, onCancelar }: Props) {
  const refTitulo = useRef<HTMLHeadingElement>(null)
  // Así los encabezados no se saltan un nivel (h1 → h3), que desorienta a quien navega por encabezados
  const Titulo = nivelTitulo === 2 ? 'h2' : 'h3'

  // Al aparecer, el foco pasa al título para que el teclado y el lector de pantalla lo noten
  useEffect(() => {
    refTitulo.current?.focus()
  }, [])

  // Esc cancela, como en cualquier diálogo
  function alTeclear(evento: KeyboardEvent<HTMLElement>) {
    if (evento.key === 'Escape') onCancelar()
  }

  return (
    <section
      className="tarjeta confirmacion"
      role="group"
      aria-labelledby={`${id}-titulo`}
      aria-describedby={`${id}-texto`}
      onKeyDown={alTeclear}
    >
      <Titulo id={`${id}-titulo`} ref={refTitulo} tabIndex={-1}>
        {titulo}
      </Titulo>
      <p id={`${id}-texto`}>{texto}</p>
      <div className="acciones">
        <button type="button" className={peligrosa ? 'boton boton-peligro' : 'boton'} onClick={onConfirmar} disabled={enviando}>
          {enviando ? 'Enviando…' : textoConfirmar}
        </button>
        <button type="button" className="boton boton-secundario" onClick={onCancelar} disabled={enviando}>
          Cancelar
        </button>
      </div>
    </section>
  )
}
