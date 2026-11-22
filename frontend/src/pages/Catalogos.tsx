import { useState } from 'react'
import type { KeyboardEvent, ReactNode } from 'react'
import { useTitulo } from '../hooks/useTitulo.ts'
import Actividades from './catalogos/Actividades.tsx'
import Promotores from './catalogos/Promotores.tsx'
import Semestres from './catalogos/Semestres.tsx'

type IdPestana = 'promotores' | 'actividades' | 'semestres'

const PESTANAS: { id: IdPestana; etiqueta: string }[] = [
  { id: 'promotores', etiqueta: 'Promotores' },
  { id: 'actividades', etiqueta: 'Actividades' },
  { id: 'semestres', etiqueta: 'Semestres' },
]

// Contenido de cada pestaña
const PANELES: Record<IdPestana, ReactNode> = {
  promotores: <Promotores />,
  actividades: <Actividades />,
  semestres: <Semestres />,
}

// Catálogos (HU-03.1 a HU-03.3), solo administrador. Tres pestañas accesibles: tablist / tab / tabpanel.
export default function Catalogos() {
  useTitulo('Catálogos')
  const [activa, setActiva] = useState<IdPestana>('promotores')

  // Flechas, Inicio y Fin cambian de pestaña (patrón de pestañas de WAI-ARIA)
  function alTeclear(evento: KeyboardEvent<HTMLDivElement>) {
    const actual = PESTANAS.findIndex((p) => p.id === activa)
    let nuevo = actual
    if (evento.key === 'ArrowRight') nuevo = (actual + 1) % PESTANAS.length
    else if (evento.key === 'ArrowLeft') nuevo = (actual - 1 + PESTANAS.length) % PESTANAS.length
    else if (evento.key === 'Home') nuevo = 0
    else if (evento.key === 'End') nuevo = PESTANAS.length - 1
    else return

    evento.preventDefault()
    setActiva(PESTANAS[nuevo].id)
    document.getElementById(`pestana-${PESTANAS[nuevo].id}`)?.focus()
  }

  return (
    <section>
      <h1>Catálogos</h1>

      {/* Solo la pestaña activa está en el orden de tabulación; las demás se alcanzan con las flechas */}
      <div className="pestanas" role="tablist" aria-label="Catálogos" onKeyDown={alTeclear}>
        {PESTANAS.map((p) => (
          <button
            key={p.id}
            id={`pestana-${p.id}`}
            type="button"
            role="tab"
            className="pestana"
            aria-selected={activa === p.id}
            aria-controls={`panel-${p.id}`}
            tabIndex={activa === p.id ? 0 : -1}
            onClick={() => setActiva(p.id)}
          >
            {p.etiqueta}
          </button>
        ))}
      </div>

      {/* Los tres paneles existen, pero solo el activo se muestra y consulta la API */}
      {PESTANAS.map((p) => (
        <div key={p.id} id={`panel-${p.id}`} role="tabpanel" aria-labelledby={`pestana-${p.id}`} hidden={activa !== p.id} className="panel-pestana">
          {activa === p.id && PANELES[p.id]}
        </div>
      ))}
    </section>
  )
}
