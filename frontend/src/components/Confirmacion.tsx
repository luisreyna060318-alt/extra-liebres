import { useEffect, useRef } from 'react'
import type { KeyboardEvent } from 'react'

interface Props {
  id: string // para unir el título y el texto con aria-labelledby / aria-describedby
  titulo: string
  texto: string
  textoConfirmar: string // por ejemplo "Sí, eliminar"
  enviando: boolean
  peligrosa?: boolean // true pinta el botón en rojo (eliminar, suspender)
  onConfirmar: () => void
  onCancelar: () => void
}

// Panel de confirmación dentro de la página (no es un modal): nada se envía hasta pulsar el botón de confirmar.
export default function Confirmacion({ id, titulo, texto, textoConfirmar, enviando, peligrosa = true, onConfirmar, onCancelar }: Props) {
  const refTitulo = useRef<HTMLHeadingElement>(null)

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
      <h3 id={`${id}-titulo`} ref={refTitulo} tabIndex={-1}>
        {titulo}
      </h3>
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
