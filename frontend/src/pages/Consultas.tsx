import { useState } from 'react'
import { Link } from 'react-router-dom'
import { cargarCatalogos } from '../api/catalogos.ts'
import { TAMANO_CONSULTA, consultarInscritos } from '../api/consultas.ts'
import type { FiltrosConsulta } from '../api/consultas.ts'
import CampoFormulario from '../components/CampoFormulario.tsx'
import Estado from '../components/Estado.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import { nombreSemestre } from '../utils/grupos.ts'
import { SIN_CALIFICAR } from '../utils/inscripciones.ts'
import '../styles/inscripciones.css'

const SIN_FILTROS: FiltrosConsulta = { extraescolar: '', semestre: '' }

// Consulta transversal: alumnos inscritos por actividad y/o semestre, con su grupo y evaluación (HU-06.1)
export default function Consultas() {
  useTitulo('Consultas')

  const [filtros, setFiltros] = useState<FiltrosConsulta>(SIN_FILTROS)
  const [pagina, setPagina] = useState(1)

  const catalogos = useApi(cargarCatalogos)
  // Cada vez que cambia un filtro o la página se vuelve a consultar al servidor
  const consulta = useApi(() => consultarInscritos(filtros, pagina), [filtros.extraescolar, filtros.semestre, pagina])

  // Al cambiar un filtro se regresa a la primera página
  function cambiarFiltro(campo: keyof FiltrosConsulta, valor: string) {
    setFiltros((anteriores) => ({ ...anteriores, [campo]: valor }))
    setPagina(1)
  }

  function limpiarFiltros() {
    setFiltros(SIN_FILTROS)
    setPagina(1)
  }

  const hayFiltros = Boolean(filtros.extraescolar || filtros.semestre)
  const total = consulta.datos?.total ?? 0
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_CONSULTA))

  return (
    <section>
      <h1>Consultas</h1>
      <p>Alumnos inscritos por actividad y semestre, con su grupo, calificación y desempeño.</p>

      <fieldset className="filtros">
        <legend>Filtrar inscritos</legend>
        <Estado cargando={catalogos.cargando} error={catalogos.error} onReintentar={catalogos.recargar}>
          {catalogos.datos && (
            <div className="filtros-campos filtros-dos">
              <CampoFormulario
                id="consulta-actividad"
                etiqueta="Actividad"
                tipo="select"
                textoOpcionVacia="Todas"
                valor={filtros.extraescolar}
                onCambio={(v) => cambiarFiltro('extraescolar', v)}
                opciones={catalogos.datos.actividades.map((a) => ({ valor: String(a.idextraescolar), etiqueta: a.nombreextra }))}
              />
              <CampoFormulario
                id="consulta-semestre"
                etiqueta="Semestre"
                tipo="select"
                textoOpcionVacia="Todos"
                valor={filtros.semestre}
                onCambio={(v) => cambiarFiltro('semestre', v)}
                opciones={catalogos.datos.semestres.map((s) => ({ valor: String(s.idsemestre), etiqueta: nombreSemestre(s) }))}
              />
            </div>
          )}
        </Estado>
        {hayFiltros && (
          <button type="button" className="boton boton-secundario" onClick={limpiarFiltros}>
            Limpiar filtros
          </button>
        )}
      </fieldset>

      <Estado
        cargando={consulta.cargando}
        error={consulta.error}
        onReintentar={consulta.recargar}
        vacio={consulta.datos?.items.length === 0}
        textoVacio={hayFiltros ? 'No hay alumnos inscritos con los filtros elegidos.' : 'Todavía no hay alumnos inscritos.'}
      >
        {consulta.datos && (
          <>
            <p aria-live="polite">
              {total} {total === 1 ? 'inscripción' : 'inscripciones'} en total
            </p>

            <div className="tabla-contenedor">
              <table className="tabla tabla-apilable">
                <caption className="solo-lectores">Alumnos inscritos con su grupo, calificación y desempeño</caption>
                <thead>
                  <tr>
                    <th scope="col">No. de control</th>
                    <th scope="col">Alumno</th>
                    <th scope="col">Actividad</th>
                    <th scope="col">Semestre</th>
                    <th scope="col">Promotor</th>
                    <th scope="col">Calificación</th>
                    <th scope="col">Desempeño</th>
                    <th scope="col">Grupo</th>
                  </tr>
                </thead>
                <tbody>
                  {consulta.datos.items.map((fila) => (
                    // Un alumno puede estar en varios grupos: la llave combina los dos
                    <tr key={`${fila.nocontrol}-${fila.idgrupo}`}>
                      <td data-etiqueta="No. de control">{fila.nocontrol}</td>
                      <td data-etiqueta="Alumno">{fila.alumno}</td>
                      <td data-etiqueta="Actividad">{fila.actividad}</td>
                      <td data-etiqueta="Semestre">{fila.semestre}</td>
                      <td data-etiqueta="Promotor">{fila.promotor}</td>
                      <td data-etiqueta="Calificación">{fila.calificacion ?? SIN_CALIFICAR}</td>
                      <td data-etiqueta="Desempeño">{fila.desempenio ?? SIN_CALIFICAR}</td>
                      <td data-etiqueta="Grupo">
                        <Link to={`/grupos/${fila.idgrupo}`}>
                          Ver grupo<span className="solo-lectores"> de {fila.actividad} de {fila.alumno}</span>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <nav className="paginacion" aria-label="Paginación de la consulta">
              <button type="button" className="boton boton-secundario" disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>
                Anterior
              </button>
              <span>
                Página {pagina} de {totalPaginas}
              </span>
              <button type="button" className="boton boton-secundario" disabled={pagina >= totalPaginas} onClick={() => setPagina(pagina + 1)}>
                Siguiente
              </button>
            </nav>
          </>
        )}
      </Estado>
    </section>
  )
}
