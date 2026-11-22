import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { obtenerGrupo } from '../api/grupos.ts'
import { listarInscritos } from '../api/inscripciones.ts'
import Estado from '../components/Estado.tsx'
import FilaInscrito from '../components/FilaInscrito.tsx'
import InscribirAlumno from '../components/InscribirAlumno.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import { nombreDia, recortarHora } from '../utils/grupos.ts'
import '../styles/inscripciones.css'

// Detalle de un grupo: sus datos, la tabla de inscritos con su evaluación y el buscador para inscribir
// (HU-05.1 a HU-05.3). Las reglas (duplicados, bajas, desempeño) las aplica el servidor.
export default function GrupoDetalle() {
  const { id = '' } = useParams()
  useTitulo('Detalle del grupo')

  const grupo = useApi(() => obtenerGrupo(id), [id])
  const inscritos = useApi(() => listarInscritos(id), [id])

  // Mensaje que queda después de quitar a un alumno (la fila ya no existe para mostrarlo)
  const [mensaje, setMensaje] = useState('')
  const refMensaje = useRef<HTMLParagraphElement>(null)

  // El botón que tenía el foco desaparece con la fila: el foco pasa al mensaje cuando ya está en pantalla
  useEffect(() => {
    if (mensaje) refMensaje.current?.focus()
  }, [mensaje])

  function alQuitar(texto: string) {
    setMensaje(texto)
    inscritos.recargar()
  }

  function alInscribir() {
    setMensaje('')
    inscritos.recargar()
  }

  const yaInscritos = new Set((inscritos.datos ?? []).map((i) => i.nocontrol))
  const cuantos = inscritos.datos?.length ?? 0

  return (
    <section>
      <p>
        <Link to="/grupos">← Volver a grupos</Link>
      </p>

      {/* El título siempre existe, aunque el grupo todavía no cargue o no exista */}
      <h1>
        {grupo.datos
          ? `${grupo.datos.actividad} · ${nombreDia(grupo.datos.dia)} ${recortarHora(grupo.datos.horainicio)}`
          : 'Detalle del grupo'}
      </h1>

      <Estado cargando={grupo.cargando} error={grupo.error} onReintentar={grupo.recargar}>
        {grupo.datos && (
          <>
            <dl className="datos-grupo">
              <div>
                <dt>Actividad</dt>
                <dd>{grupo.datos.actividad}</dd>
              </div>
              <div>
                <dt>Semestre</dt>
                <dd>{grupo.datos.semestre}</dd>
              </div>
              <div>
                <dt>Promotor</dt>
                <dd>{grupo.datos.promotor}</dd>
              </div>
              <div>
                <dt>Día</dt>
                <dd>{nombreDia(grupo.datos.dia)}</dd>
              </div>
              <div>
                <dt>Horario</dt>
                <dd>
                  {recortarHora(grupo.datos.horainicio)} a {recortarHora(grupo.datos.horatermino)}
                </dd>
              </div>
              <div>
                <dt>Lugar</dt>
                <dd>{grupo.datos.aula}</dd>
              </div>
            </dl>

            <section className="tarjeta-seccion" aria-labelledby="titulo-inscritos">
              <h2 id="titulo-inscritos">Alumnos inscritos</h2>
              <p className="campo-ayuda">
                Captura la calificación (entero de 0 a 100) y presiona Guardar. El desempeño lo calcula el sistema.
              </p>

              {mensaje && (
                <p ref={refMensaje} tabIndex={-1} role="status" className="alerta alerta-exito">
                  {mensaje}
                </p>
              )}

              <Estado
                cargando={inscritos.cargando}
                error={inscritos.error}
                onReintentar={inscritos.recargar}
                vacio={cuantos === 0}
                textoVacio="Todavía no hay alumnos inscritos en este grupo."
              >
                <p>
                  {cuantos} {cuantos === 1 ? 'alumno inscrito' : 'alumnos inscritos'}
                </p>
                <div className="tabla-contenedor">
                  <table className="tabla tabla-apilable">
                    <caption className="solo-lectores">Alumnos inscritos en el grupo, con su calificación y desempeño</caption>
                    <thead>
                      <tr>
                        <th scope="col">No. de control</th>
                        <th scope="col">Alumno</th>
                        <th scope="col">Carrera</th>
                        <th scope="col">Calificación</th>
                        <th scope="col">Desempeño</th>
                        <th scope="col">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {/* key: si la lista se recarga, cada fila vuelve a tomar los datos del servidor */}
                      {inscritos.datos?.map((i) => (
                        <FilaInscrito key={i.nocontrol} idgrupo={id} inscrito={i} onQuitado={alQuitar} />
                      ))}
                    </tbody>
                  </table>
                </div>
              </Estado>
            </section>

            <InscribirAlumno idgrupo={id} yaInscritos={yaInscritos} onInscrito={alInscribir} />
          </>
        )}
      </Estado>
    </section>
  )
}
