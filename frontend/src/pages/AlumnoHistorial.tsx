import { Link, useParams } from 'react-router-dom'
import { obtenerAlumno, obtenerHistorial } from '../api/alumnos.ts'
import Estado from '../components/Estado.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import { nombreCompleto, nombreSexo, semestreDelHistorial } from '../utils/alumnos.ts'
import { nombreDia, recortarHora } from '../utils/grupos.ts'

// Datos de un alumno y las actividades que ha cursado (HU-02.4)
export default function AlumnoHistorial() {
  const { nocontrol = '' } = useParams()

  const alumno = useApi(() => obtenerAlumno(nocontrol), [nocontrol])
  const historial = useApi(() => obtenerHistorial(nocontrol), [nocontrol])

  useTitulo(alumno.datos ? `Historial de ${nombreCompleto(alumno.datos)}` : 'Historial del alumno')

  function reintentar() {
    alumno.recargar()
    historial.recargar()
  }

  return (
    <section>
      <div className="encabezado-pagina">
        <h1>Historial del alumno</h1>
        <div className="acciones">
          {alumno.datos && (
            <Link to={`/alumnos/${encodeURIComponent(nocontrol)}/editar`} className="boton">
              Editar alumno
            </Link>
          )}
          <Link to="/alumnos" className="boton boton-secundario">
            Volver a alumnos
          </Link>
        </div>
      </div>

      {/* Si el alumno no existe (404) o falla la carga, solo se muestra ese mensaje */}
      <Estado cargando={alumno.cargando} error={alumno.error} onReintentar={reintentar}>
        {alumno.datos && (
          <>
            <div className="tarjeta datos-alumno">
              <h2>{nombreCompleto(alumno.datos)}</h2>
              <dl>
                <div>
                  <dt>Número de control</dt>
                  <dd>{alumno.datos.nocontrol}</dd>
                </div>
                <div>
                  <dt>Sexo</dt>
                  <dd>{nombreSexo(alumno.datos.sexo)}</dd>
                </div>
                <div>
                  <dt>Carrera</dt>
                  <dd>{alumno.datos.carrera}</dd>
                </div>
                <div>
                  <dt>Campus</dt>
                  <dd>{alumno.datos.campus}</dd>
                </div>
                <div>
                  <dt>Estado</dt>
                  <dd>{alumno.datos.activo ? 'Activo' : 'Baja'}</dd>
                </div>
              </dl>
            </div>

            <h2>Actividades cursadas</h2>
            <Estado
              cargando={historial.cargando}
              error={historial.error}
              onReintentar={historial.recargar}
              vacio={historial.datos?.length === 0}
              textoVacio="Este alumno aún no tiene actividades registradas"
            >
              {historial.datos && (
                <div className="tabla-contenedor">
                  <table className="tabla tabla-apilable">
                    <caption className="solo-lectores">Actividades cursadas por el alumno</caption>
                    <thead>
                      <tr>
                        <th scope="col">Actividad</th>
                        <th scope="col">Semestre</th>
                        <th scope="col">Promotor</th>
                        <th scope="col">Día</th>
                        <th scope="col">Horario</th>
                        <th scope="col">Aula o lugar</th>
                        <th scope="col">Calificación</th>
                        <th scope="col">Desempeño</th>
                      </tr>
                    </thead>
                    <tbody>
                      {historial.datos.map((h) => (
                        <tr key={h.idgrupo}>
                          <td data-etiqueta="Actividad">{h.actividad}</td>
                          <td data-etiqueta="Semestre">{semestreDelHistorial(h)}</td>
                          <td data-etiqueta="Promotor">{h.promotor}</td>
                          <td data-etiqueta="Día">{nombreDia(h.dia)}</td>
                          <td data-etiqueta="Horario">
                            {recortarHora(h.horainicio)} a {recortarHora(h.horatermino)}
                          </td>
                          <td data-etiqueta="Aula o lugar">{h.aula}</td>
                          {/* null = todavía no tiene calificación; 0 sí es una calificación válida */}
                          <td data-etiqueta="Calificación">{h.calificacion ?? 'Sin evaluar'}</td>
                          <td data-etiqueta="Desempeño">{h.desempenio ?? 'Sin evaluar'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Estado>
          </>
        )}
      </Estado>
    </section>
  )
}
