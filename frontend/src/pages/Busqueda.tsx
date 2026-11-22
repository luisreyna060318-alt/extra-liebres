import { Link, useSearchParams } from 'react-router-dom'
import { MINIMO_BUSQUEDA, buscar } from '../api/busqueda.ts'
import Estado from '../components/Estado.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import '../styles/busqueda.css'

// Resultados de la búsqueda global: alumnos y grupos agrupados por tipo (HU-06.2).
// El texto viaja en la dirección (?q=...), así que el resultado se puede recargar o compartir.
export default function Busqueda() {
  const [parametros] = useSearchParams()
  const q = (parametros.get('q') ?? '').trim()
  useTitulo(q ? `Resultados de “${q}”` : 'Búsqueda')

  const muyCorta = q.length < MINIMO_BUSQUEDA
  // Con menos de 2 letras no se llama al servidor (respondería 422)
  const resultado = useApi(() => (muyCorta ? Promise.resolve(null) : buscar(q)), [q])
  const datos = resultado.datos
  const sinCoincidencias = datos !== null && datos.alumnos.length === 0 && datos.grupos.length === 0

  return (
    <section>
      <h1>Resultados de la búsqueda</h1>

      {muyCorta ? (
        <p>Escribe al menos {MINIMO_BUSQUEDA} letras en el buscador de arriba para encontrar alumnos y grupos.</p>
      ) : (
        <Estado
          cargando={resultado.cargando}
          error={resultado.error}
          onReintentar={resultado.recargar}
          vacio={sinCoincidencias}
          textoVacio={`No hay alumnos ni grupos que coincidan con “${q}”.`}
        >
          {datos && (
            <>
              <p aria-live="polite">Coincidencias para “{datos.q}”</p>

              <section aria-labelledby="busqueda-alumnos">
                <h2 id="busqueda-alumnos">Alumnos</h2>
                {datos.alumnos.length === 0 ? (
                  <p>No hay alumnos que coincidan.</p>
                ) : (
                  <ul className="busqueda-lista">
                    {datos.alumnos.map((a) => (
                      <li key={a.nocontrol} className="busqueda-item">
                        <Link to={`/alumnos/${a.nocontrol}`}>{a.alumno}</Link>
                        <span>
                          {a.nocontrol} · {a.carrera}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
                {datos.alumnos_hay_mas && (
                  <p>
                    Hay más alumnos que coinciden: escribe más letras para afinar o ve a{' '}
                    <Link to="/alumnos">la lista de alumnos</Link>.
                  </p>
                )}
              </section>

              <section aria-labelledby="busqueda-grupos">
                <h2 id="busqueda-grupos">Grupos</h2>
                {datos.grupos.length === 0 ? (
                  <p>No hay grupos que coincidan.</p>
                ) : (
                  <ul className="busqueda-lista">
                    {datos.grupos.map((g) => (
                      <li key={g.idgrupo} className="busqueda-item">
                        <Link to={`/grupos/${g.idgrupo}`}>{g.descripcion}</Link>
                        <span>
                          {g.semestre} · {g.promotor}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
                {datos.grupos_hay_mas && (
                  <p>
                    Hay más grupos que coinciden: escribe más letras para afinar o ve a{' '}
                    <Link to="/grupos">la lista de grupos</Link>.
                  </p>
                )}
              </section>
            </>
          )}
        </Estado>
      )}
    </section>
  )
}
