import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cargarCatalogos } from '../api/catalogos.ts'
import { TAMANO_PAGINA, listarGrupos } from '../api/grupos.ts'
import type { FiltrosGrupos } from '../api/grupos.ts'
import CampoFormulario from '../components/CampoFormulario.tsx'
import Estado from '../components/Estado.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import { DIAS, nombreDia, nombrePromotor, nombreSemestre, recortarHora } from '../utils/grupos.ts'

const SIN_FILTROS: FiltrosGrupos = { semestre: '', extraescolar: '', promotor: '', dia: '' }

// Estado que otras pantallas mandan al navegar aquí (por ejemplo, "Grupo creado.")
interface EstadoNavegacion {
  mensaje?: string
}

// Lista de grupos con filtros y paginación (HU-04.3). Los filtros se aplican en el servidor.
export default function Grupos() {
  useTitulo('Grupos')
  const mensaje = (useLocation().state as EstadoNavegacion | null)?.mensaje

  const [filtros, setFiltros] = useState<FiltrosGrupos>(SIN_FILTROS)
  const [pagina, setPagina] = useState(1)

  // Los catálogos llenan las listas de los filtros; si fallan, solo esa parte muestra el error
  const catalogos = useApi(cargarCatalogos)
  // Cada vez que cambia un filtro o la página se vuelve a consultar
  const grupos = useApi(() => listarGrupos(filtros, pagina), [filtros.semestre, filtros.extraescolar, filtros.promotor, filtros.dia, pagina])

  // Al cambiar un filtro se regresa a la primera página
  function cambiarFiltro(campo: keyof FiltrosGrupos, valor: string) {
    setFiltros((anteriores) => ({ ...anteriores, [campo]: valor }))
    setPagina(1)
  }

  function limpiarFiltros() {
    setFiltros(SIN_FILTROS)
    setPagina(1)
  }

  const hayFiltros = Object.values(filtros).some(Boolean)
  const total = grupos.datos?.total ?? 0
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_PAGINA))

  return (
    <section>
      <div className="encabezado-pagina">
        <h1>Grupos</h1>
        <Link to="/grupos/nuevo" className="boton">
          Nuevo grupo
        </Link>
      </div>

      {mensaje && (
        <p role="status" className="alerta alerta-exito">
          {mensaje}
        </p>
      )}

      <fieldset className="filtros">
        <legend>Filtrar grupos</legend>
        <Estado cargando={catalogos.cargando} error={catalogos.error} onReintentar={catalogos.recargar}>
          {catalogos.datos && (
            <div className="filtros-campos">
              <CampoFormulario
                id="filtro-semestre"
                etiqueta="Semestre"
                tipo="select"
                textoOpcionVacia="Todos"
                valor={filtros.semestre}
                onCambio={(v) => cambiarFiltro('semestre', v)}
                opciones={catalogos.datos.semestres.map((s) => ({ valor: String(s.idsemestre), etiqueta: nombreSemestre(s) }))}
              />
              <CampoFormulario
                id="filtro-actividad"
                etiqueta="Actividad"
                tipo="select"
                textoOpcionVacia="Todas"
                valor={filtros.extraescolar}
                onCambio={(v) => cambiarFiltro('extraescolar', v)}
                opciones={catalogos.datos.actividades.map((a) => ({ valor: String(a.idextraescolar), etiqueta: a.nombreextra }))}
              />
              <CampoFormulario
                id="filtro-promotor"
                etiqueta="Promotor"
                tipo="select"
                textoOpcionVacia="Todos"
                valor={filtros.promotor}
                onCambio={(v) => cambiarFiltro('promotor', v)}
                opciones={catalogos.datos.promotores.map((p) => ({ valor: p.rfc, etiqueta: nombrePromotor(p) }))}
              />
              <CampoFormulario
                id="filtro-dia"
                etiqueta="Día"
                tipo="select"
                textoOpcionVacia="Todos"
                valor={filtros.dia}
                onCambio={(v) => cambiarFiltro('dia', v)}
                opciones={DIAS.map((d) => ({ valor: d.valor, etiqueta: d.etiqueta }))}
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
        cargando={grupos.cargando}
        error={grupos.error}
        onReintentar={grupos.recargar}
        vacio={grupos.datos?.items.length === 0}
        textoVacio={hayFiltros ? 'Ningún grupo cumple con los filtros elegidos.' : 'Todavía no hay grupos registrados.'}
      >
        {grupos.datos && (
          <>
            <p aria-live="polite">
              {total} {total === 1 ? 'grupo' : 'grupos'} en total
            </p>

            <div className="tabla-contenedor">
              <table className="tabla tabla-apilable">
                <caption className="solo-lectores">Grupos registrados</caption>
                <thead>
                  <tr>
                    <th scope="col">Actividad</th>
                    <th scope="col">Semestre</th>
                    <th scope="col">Promotor</th>
                    <th scope="col">Día</th>
                    <th scope="col">Horario</th>
                    <th scope="col">Lugar</th>
                    <th scope="col">Inscritos</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {grupos.datos.items.map((g) => (
                    <tr key={g.idgrupo}>
                      <td data-etiqueta="Actividad">{g.actividad}</td>
                      <td data-etiqueta="Semestre">{g.semestre}</td>
                      <td data-etiqueta="Promotor">{g.promotor}</td>
                      <td data-etiqueta="Día">{nombreDia(g.dia)}</td>
                      <td data-etiqueta="Horario">
                        {recortarHora(g.horainicio)} a {recortarHora(g.horatermino)}
                      </td>
                      <td data-etiqueta="Lugar">{g.aula}</td>
                      <td data-etiqueta="Inscritos">{g.inscritos}</td>
                      <td data-etiqueta="Acciones">
                        <Link to={`/grupos/${g.idgrupo}/editar`} aria-label={`Editar el grupo de ${g.actividad}, ${nombreDia(g.dia)} ${recortarHora(g.horainicio)}`}>
                          Editar
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <nav className="paginacion" aria-label="Paginación de grupos">
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
