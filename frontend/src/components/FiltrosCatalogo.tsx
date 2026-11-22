import { useState } from 'react'
import type { FormEvent } from 'react'
import type { FiltroEstado } from '../tiposAdmin.ts'
import CampoFormulario from './CampoFormulario.tsx'

interface Props {
  prefijo: string // para que los ids de los campos no se repitan entre pestañas
  etiquetaBusqueda: string // por ejemplo "RFC o nombre"
  estado: FiltroEstado
  onBuscar: (q: string) => void
  onEstado: (estado: FiltroEstado) => void
}

// Búsqueda por texto y filtro de estado de promotores y actividades.
// El texto se aplica al pulsar "Buscar" (así no se consulta en cada letra); el estado, al elegirlo.
export default function FiltrosCatalogo({ prefijo, etiquetaBusqueda, estado, onBuscar, onEstado }: Props) {
  const [texto, setTexto] = useState('')

  function buscar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    onBuscar(texto.trim())
  }

  return (
    <form onSubmit={buscar}>
      <fieldset className="filtros">
        <legend>Buscar y filtrar</legend>
        <div className="filtros-campos">
          <CampoFormulario id={`${prefijo}-q`} etiqueta={`Buscar por ${etiquetaBusqueda}`} valor={texto} onCambio={setTexto} />
          <div className="campo">
            <label htmlFor={`${prefijo}-estado`}>Mostrar</label>
            <select id={`${prefijo}-estado`} value={estado} onChange={(e) => onEstado(e.target.value as FiltroEstado)}>
              <option value="activos">Activos</option>
              <option value="bajas">Dados de baja</option>
              <option value="todos">Todos</option>
            </select>
          </div>
        </div>
        <button type="submit" className="boton">
          Buscar
        </button>
      </fieldset>
    </form>
  )
}
