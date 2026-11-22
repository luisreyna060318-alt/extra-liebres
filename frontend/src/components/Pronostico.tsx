import { pedirClima } from '../api/grupos.ts'
import { useApi } from '../hooks/useApi.ts'
import Estado from './Estado.tsx'

// Pronóstico de Ciudad Juárez junto al formulario (HU-04.2 CA3). Solo se monta si la actividad es al aire libre.
export default function Pronostico() {
  const { datos, cargando, error, recargar } = useApi(pedirClima)

  return (
    <aside className="tarjeta pronostico" aria-labelledby="titulo-pronostico">
      <h2 id="titulo-pronostico">Pronóstico en Ciudad Juárez</h2>

      <Estado cargando={cargando} error={error} onReintentar={recargar}>
        {datos?.disponible ? (
          <>
            <p>
              Temperatura actual: <strong>{datos.temperatura} °C</strong>
            </p>
            <p>
              Probabilidad de lluvia en las próximas 12 horas: <strong>{datos.prob_lluvia} %</strong>
            </p>
            {datos.aviso_lluvia && (
              <div role="alert" className="alerta alerta-error">
                Hay alta probabilidad de lluvia: la actividad al aire libre podría verse afectada.
              </div>
            )}
          </>
        ) : (
          // El backend responde 200 con disponible: false cuando Open-Meteo no contesta
          <p>{datos?.mensaje ?? 'Pronóstico no disponible'}</p>
        )}
      </Estado>
    </aside>
  )
}
