import { useState } from 'react'
import { pedirSemestres } from '../api/catalogos.ts'
import { pedirResumen } from '../api/dashboard.ts'
import Estado from '../components/Estado.tsx'
import GraficaBarras from '../components/GraficaBarras.tsx'
import Pronostico from '../components/Pronostico.tsx'
import TarjetaIndicador from '../components/TarjetaIndicador.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import { nombreSemestre } from '../utils/grupos.ts'

// Cifras y gráficas de un semestre. Tiene su propia petición, así que al cambiar `idsemestre`
// se vuelve a pedir y todo se recalcula (HU-07.1 CA4).
function ResumenSemestre({ idsemestre }: { idsemestre: number }) {
  const { datos, cargando, error, recargar } = useApi(() => pedirResumen(idsemestre), [idsemestre])

  const actividades = (datos?.inscritos_por_actividad ?? []).map((a) => ({ nombre: a.actividad, total: a.total }))
  const desempenios = (datos?.distribucion_desempenio ?? []).map((d) => ({ nombre: d.desempenio, total: d.total }))
  // La distribución trae siempre las 5 categorías; si todas están en 0 no hay nada que graficar
  const hayCalificadas = desempenios.some((d) => d.total > 0)

  // El promedio llega null cuando nadie tiene calificación: se muestra una raya, no 0
  const promedio =
    datos?.promedio_calificacion == null
      ? '—'
      : datos.promedio_calificacion.toLocaleString('es-MX', { maximumFractionDigits: 2 })

  return (
    <Estado cargando={cargando} error={error} onReintentar={recargar}>
      {datos && (
        <>
          <dl className="indicadores">
            <TarjetaIndicador
              titulo="Alumnos activos"
              valor={datos.totales.alumnos_activos.toLocaleString('es-MX')}
              nota="En total; no depende del semestre"
            />
            <TarjetaIndicador titulo="Grupos" valor={datos.totales.grupos.toLocaleString('es-MX')} />
            <TarjetaIndicador titulo="Inscripciones" valor={datos.totales.inscripciones.toLocaleString('es-MX')} />
            <TarjetaIndicador titulo="Promedio de calificación" valor={promedio} nota="Solo inscripciones calificadas" />
          </dl>

          <div className="graficas">
            {actividades.length > 0 ? (
              <GraficaBarras
                titulo="Inscritos por actividad"
                descripcion="Gráfica de barras con el número de alumnos inscritos en cada actividad del semestre."
                etiquetaNombre="Actividad"
                etiquetaValor="Inscritos"
                datos={actividades}
                horizontal
              />
            ) : (
              <section className="tarjeta">
                <h2>Inscritos por actividad</h2>
                <Estado cargando={false} error={null} vacio textoVacio="Este semestre aún no tiene inscripciones." />
              </section>
            )}

            {hayCalificadas ? (
              <GraficaBarras
                titulo="Distribución del desempeño"
                descripcion="Gráfica de barras con cuántas inscripciones calificadas hay en cada nivel de desempeño, de Excelente a Insuficiente."
                etiquetaNombre="Desempeño"
                etiquetaValor="Inscripciones"
                datos={desempenios}
              />
            ) : (
              <section className="tarjeta">
                <h2>Distribución del desempeño</h2>
                <Estado cargando={false} error={null} vacio textoVacio="Este semestre aún no tiene calificaciones." />
              </section>
            )}
          </div>
        </>
      )}
    </Estado>
  )
}

export default function Tablero() {
  useTitulo('Tablero')

  const { datos: semestres, cargando, error, recargar } = useApi(pedirSemestres)
  // null = el usuario no ha elegido: se usa el primero de la lista (la API manda el más reciente primero)
  const [elegido, setElegido] = useState<number | null>(null)
  const idsemestre = elegido ?? semestres?.[0]?.idsemestre ?? null

  return (
    <section className="tablero">
      <h1>Tablero</h1>

      <div className="tablero-encabezado">
        <Estado
          cargando={cargando}
          error={error}
          vacio={semestres?.length === 0}
          textoVacio="Todavía no hay semestres registrados."
          onReintentar={recargar}
        >
          <div className="campo">
            <label htmlFor="semestre">Semestre</label>
            <select id="semestre" value={idsemestre ?? ''} onChange={(e) => setElegido(Number(e.target.value))}>
              {semestres?.map((s) => (
                <option key={s.idsemestre} value={s.idsemestre}>
                  {nombreSemestre(s)}
                </option>
              ))}
            </select>
          </div>
        </Estado>

        {/* El pronóstico es independiente: si falla, el resto del tablero sigue igual */}
        <Pronostico />
      </div>

      {idsemestre !== null && <ResumenSemestre idsemestre={idsemestre} />}
    </section>
  )
}
