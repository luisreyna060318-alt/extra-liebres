import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useSearchParams } from 'react-router-dom'
import { TAMANO_PAGINA, actualizarAlumno, darDeBajaAlumno, listarAlumnos, obtenerOpciones } from '../api/alumnos.ts'
import type { FiltrosAlumnos } from '../api/alumnos.ts'
import CampoFormulario from '../components/CampoFormulario.tsx'
import Estado from '../components/Estado.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import type { Alumno } from '../types.ts'
import { nombreCompleto } from '../utils/alumnos.ts'

// Estado que otras pantallas mandan al navegar aquí (por ejemplo, "Alumno creado.")
interface EstadoNavegacion {
  mensaje?: string
}

const OPCIONES_ESTADO = [
  { valor: 'activos', etiqueta: 'Activos' },
  { valor: 'bajas', etiqueta: 'Bajas' },
  { valor: 'todos', etiqueta: 'Todos' },
]

interface PropsBuscador {
  inicial: string
  onBuscar: (texto: string) => void
}

// Cuadro de búsqueda: lo escrito solo se aplica al pulsar "Buscar" (así no se consulta en cada tecla)
function Buscador({ inicial, onBuscar }: PropsBuscador) {
  const [texto, setTexto] = useState(inicial)

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    onBuscar(texto.trim())
  }

  return (
    <form className="busqueda" role="search" onSubmit={enviar}>
      <CampoFormulario
        id="filtro-q"
        etiqueta="Nombre o número de control"
        valor={texto}
        onCambio={setTexto}
        ayuda="Escribe los acentos tal como están registrados."
      />
      <button type="submit" className="boton">
        Buscar
      </button>
    </form>
  )
}

// Lista de alumnos con búsqueda, filtros y paginación (HU-02.1 a HU-02.3).
// Los filtros viven en la URL (?q=...&carrera=...) para que el botón Atrás los recupere.
export default function Alumnos() {
  useTitulo('Alumnos')
  const mensajeInicial = (useLocation().state as EstadoNavegacion | null)?.mensaje ?? ''

  const [parametros, setParametros] = useSearchParams()
  const q = parametros.get('q') ?? ''
  const carrera = parametros.get('carrera') ?? ''
  const campus = parametros.get('campus') ?? ''
  // Cualquier valor raro en la URL se trata como "activos" (el valor por defecto)
  const estadoUrl = parametros.get('estado')
  const estado: FiltrosAlumnos['estado'] = estadoUrl === 'bajas' || estadoUrl === 'todos' ? estadoUrl : 'activos'
  const pagina = Math.max(1, Number(parametros.get('page')) || 1)

  const [aviso, setAviso] = useState(mensajeInicial) // confirmación de la última acción
  const [errorAccion, setErrorAccion] = useState('') // error de la última acción
  const [porBajar, setPorBajar] = useState<Alumno | null>(null) // alumno que espera confirmación de baja
  const [procesando, setProcesando] = useState('') // nocontrol del alumno con una acción en curso

  const dialogo = useRef<HTMLDialogElement>(null)

  // El cuadro de confirmación se abre como diálogo modal (el foco queda dentro y Esc lo cierra)
  useEffect(() => {
    if (porBajar && !dialogo.current?.open) dialogo.current?.showModal()
  }, [porBajar])

  const opciones = useApi(obtenerOpciones)
  const filtros: FiltrosAlumnos = { q, carrera, campus, estado }
  const alumnos = useApi(() => listarAlumnos(filtros, pagina), [q, carrera, campus, estado, pagina])

  // Guarda los filtros en la URL. Solo se escriben los que tienen valor; al filtrar se vuelve a la página 1.
  function aplicarFiltros(nuevos: FiltrosAlumnos, nuevaPagina = 1) {
    const siguiente = new URLSearchParams()
    if (nuevos.q) siguiente.set('q', nuevos.q)
    if (nuevos.carrera) siguiente.set('carrera', nuevos.carrera)
    if (nuevos.campus) siguiente.set('campus', nuevos.campus)
    if (nuevos.estado !== 'activos') siguiente.set('estado', nuevos.estado)
    if (nuevaPagina > 1) siguiente.set('page', String(nuevaPagina))
    setParametros(siguiente)
    setAviso('')
    setErrorAccion('')
  }

  function limpiarFiltros() {
    aplicarFiltros({ q: '', carrera: '', campus: '', estado: 'activos' })
  }

  // Después de una baja o reactivación: si la página se quedó sin filas, se retrocede una; si no, se recarga
  function terminarAccion(mensaje: string) {
    const quedaVacia = alumnos.datos?.items.length === 1 && pagina > 1 && estado !== 'todos'
    if (quedaVacia) aplicarFiltros(filtros, pagina - 1) // al cambiar la URL la lista se consulta sola
    else alumnos.recargar()
    setAviso(mensaje) // va al final porque aplicarFiltros borra el aviso
  }

  function cancelarBaja() {
    dialogo.current?.close()
    // Se limpia el estado aquí mismo y no solo con el evento "close" del <dialog>: así, aunque ese evento
    // tarde o no llegue, el siguiente clic en "Dar de baja" vuelve a abrir el diálogo.
    setPorBajar(null)
  }

  async function confirmarBaja() {
    if (!porBajar) return
    const alumno = porBajar
    dialogo.current?.close()
    setPorBajar(null)
    setErrorAccion('')
    setProcesando(alumno.nocontrol)
    try {
      await darDeBajaAlumno(alumno.nocontrol) // DELETE: baja lógica, el alumno no se borra
      terminarAccion(`Se dio de baja a ${nombreCompleto(alumno)}.`)
    } catch (e) {
      setAviso('')
      setErrorAccion(e instanceof Error ? e.message : 'No se pudo dar de baja al alumno.')
    } finally {
      setProcesando('')
    }
  }

  async function reactivar(alumno: Alumno) {
    setErrorAccion('')
    setProcesando(alumno.nocontrol)
    try {
      // PUT pide todos los datos del alumno; se reenvían los mismos y solo cambia activo
      await actualizarAlumno(alumno.nocontrol, {
        nombre: alumno.nombre,
        apaterno: alumno.apaterno,
        ...(alumno.amaterno ? { amaterno: alumno.amaterno } : {}),
        sexo: alumno.sexo,
        carrera: alumno.carrera,
        campus: alumno.campus,
        activo: true,
      })
      terminarAccion(`Se reactivó a ${nombreCompleto(alumno)}.`)
    } catch (e) {
      setAviso('')
      setErrorAccion(e instanceof Error ? e.message : 'No se pudo reactivar al alumno.')
    } finally {
      setProcesando('')
    }
  }

  const hayFiltros = Boolean(q || carrera || campus || estado !== 'activos')
  const total = alumnos.datos?.total ?? 0
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_PAGINA))

  return (
    <section>
      <div className="encabezado-pagina">
        <h1>Alumnos</h1>
        <Link to="/alumnos/nuevo" className="boton">
          Nuevo alumno
        </Link>
      </div>

      {/* role="status" avisa a los lectores de pantalla sin mover el foco */}
      {aviso && (
        <p role="status" className="alerta alerta-exito">
          {aviso}
        </p>
      )}
      {errorAccion && (
        <p role="alert" className="alerta alerta-error">
          {errorAccion}
        </p>
      )}

      <fieldset className="filtros">
        <legend>Buscar y filtrar alumnos</legend>

        {/* key={q}: si la búsqueda de la URL cambia (Atrás, Limpiar filtros) el cuadro se reinicia con ese valor */}
        <Buscador key={q} inicial={q} onBuscar={(texto) => aplicarFiltros({ ...filtros, q: texto })} />

        <div className="filtros-campos alumnos-filtros">
          <CampoFormulario
            id="filtro-carrera"
            etiqueta="Carrera"
            tipo="select"
            textoOpcionVacia="Todas"
            valor={carrera}
            onCambio={(v) => aplicarFiltros({ ...filtros, carrera: v })}
            opciones={(opciones.datos?.carreras ?? []).map((c) => ({ valor: c, etiqueta: c }))}
          />
          <CampoFormulario
            id="filtro-campus"
            etiqueta="Campus"
            tipo="select"
            textoOpcionVacia="Todos"
            valor={campus}
            onCambio={(v) => aplicarFiltros({ ...filtros, campus: v })}
            opciones={(opciones.datos?.campus ?? []).map((c) => ({ valor: c, etiqueta: c }))}
          />
          {/* Sin opción vacía: siempre hay un estado elegido. Se usa un select propio por eso. */}
          <div className="campo">
            <label htmlFor="filtro-estado">Estado</label>
            <select
              id="filtro-estado"
              value={estado}
              onChange={(e) => aplicarFiltros({ ...filtros, estado: e.target.value as FiltrosAlumnos['estado'] })}
            >
              {OPCIONES_ESTADO.map((o) => (
                <option key={o.valor} value={o.valor}>
                  {o.etiqueta}
                </option>
              ))}
            </select>
          </div>
        </div>

        {opciones.error && <p className="campo-ayuda">No se pudieron cargar las carreras y campus: {opciones.error}</p>}

        {hayFiltros && (
          <button type="button" className="boton boton-secundario" onClick={limpiarFiltros}>
            Limpiar filtros
          </button>
        )}
      </fieldset>

      <Estado cargando={alumnos.cargando} error={alumnos.error} onReintentar={alumnos.recargar}>
        {alumnos.datos && alumnos.datos.items.length === 0 && (
          <div className="estado" role="status">
            <p>{hayFiltros ? 'Ningún alumno cumple con la búsqueda o los filtros elegidos.' : 'Todavía no hay alumnos registrados.'}</p>
            {hayFiltros && (
              <button type="button" className="boton boton-secundario" onClick={limpiarFiltros}>
                Limpiar filtros
              </button>
            )}
          </div>
        )}

        {alumnos.datos && alumnos.datos.items.length > 0 && (
          <>
            <p aria-live="polite">
              {total} {total === 1 ? 'alumno' : 'alumnos'} en total
            </p>

            <div className="tabla-contenedor">
              <table className="tabla tabla-apilable">
                <caption className="solo-lectores">Alumnos registrados</caption>
                <thead>
                  <tr>
                    <th scope="col">Número de control</th>
                    <th scope="col">Nombre</th>
                    <th scope="col">Carrera</th>
                    <th scope="col">Campus</th>
                    <th scope="col">Estado</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {alumnos.datos.items.map((a) => {
                    const nombre = nombreCompleto(a)
                    return (
                      <tr key={a.nocontrol}>
                        <td data-etiqueta="Número de control">{a.nocontrol}</td>
                        <td data-etiqueta="Nombre">{nombre}</td>
                        <td data-etiqueta="Carrera">{a.carrera}</td>
                        <td data-etiqueta="Campus">{a.campus}</td>
                        <td data-etiqueta="Estado">{a.activo ? 'Activo' : 'Baja'}</td>
                        <td data-etiqueta="Acciones">
                          <div className="acciones-fila">
                            <Link to={`/alumnos/${encodeURIComponent(a.nocontrol)}`} aria-label={`Ver historial de ${nombre}`}>
                              Ver historial
                            </Link>
                            <Link to={`/alumnos/${encodeURIComponent(a.nocontrol)}/editar`} aria-label={`Editar a ${nombre}`}>
                              Editar
                            </Link>
                            {a.activo ? (
                              <button
                                type="button"
                                className="boton-texto boton-texto-peligro"
                                disabled={procesando === a.nocontrol}
                                onClick={() => setPorBajar(a)}
                                aria-label={`Dar de baja a ${nombre}`}
                              >
                                Dar de baja
                              </button>
                            ) : (
                              <button
                                type="button"
                                className="boton-texto"
                                disabled={procesando === a.nocontrol}
                                onClick={() => reactivar(a)}
                                aria-label={`Reactivar a ${nombre}`}
                              >
                                Reactivar
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <nav className="paginacion" aria-label="Paginación de alumnos">
              <button type="button" className="boton boton-secundario" disabled={pagina <= 1} onClick={() => aplicarFiltros(filtros, pagina - 1)}>
                Anterior
              </button>
              <span>
                Página {pagina} de {totalPaginas}
              </span>
              <button type="button" className="boton boton-secundario" disabled={pagina >= totalPaginas} onClick={() => aplicarFiltros(filtros, pagina + 1)}>
                Siguiente
              </button>
            </nav>
          </>
        )}
      </Estado>

      {/* Confirmación explícita antes de la baja: nada se envía hasta pulsar "Sí, dar de baja" */}
      {porBajar && (
        <dialog ref={dialogo} className="dialogo" aria-labelledby="titulo-baja" onClose={() => setPorBajar(null)}>
          <h2 id="titulo-baja">¿Dar de baja al alumno?</h2>
          <p>
            Vas a dar de baja a <strong>{nombreCompleto(porBajar)}</strong> ({porBajar.nocontrol}). No se borra: podrás reactivarlo después.
          </p>
          <div className="acciones">
            <button type="button" className="boton boton-peligro-solido" onClick={confirmarBaja}>
              Sí, dar de baja
            </button>
            <button type="button" className="boton boton-secundario" onClick={cancelarBaja}>
              Cancelar
            </button>
          </div>
        </dialog>
      )}
    </section>
  )
}
