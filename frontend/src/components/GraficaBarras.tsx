import { useId } from 'react'
import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, XAxis, YAxis } from 'recharts'

export interface Dato {
  nombre: string
  total: number
}

interface Props {
  titulo: string
  descripcion: string // texto alternativo: qué muestra la gráfica
  etiquetaNombre: string // nombre de la columna de categorías en la tabla, por ejemplo "Actividad"
  etiquetaValor: string // nombre de la columna de números en la tabla, por ejemplo "Inscritos"
  datos: Dato[]
  horizontal?: boolean // barras horizontales: mejor cuando los nombres son largos
}

// Altura de cada barra horizontal, para que quepan todas las actividades sin amontonarse
const ALTO_BARRA = 36

// Recorta nombres largos en el eje (el nombre completo siempre está en la tabla)
function recortar(texto: string): string {
  return texto.length > 20 ? `${texto.slice(0, 19)}…` : texto
}

// Eje numérico con un poco de espacio arriba de la barra más alta: así el número escrito sobre ella no queda pegado
// al borde ni se corta (antes el eje terminaba justo en la barra más alta)
const ESPACIO_ARRIBA: [number, (maximo: number) => number] = [0, (maximo) => Math.ceil(maximo * 1.15)]

// Gráfica de barras con título, texto alternativo y la misma información en una tabla desplegable.
// El dibujo es solo visual (aria-hidden): con lector de pantalla se lee la descripción y la tabla.
export default function GraficaBarras({
  titulo,
  descripcion,
  etiquetaNombre,
  etiquetaValor,
  datos,
  horizontal = false,
}: Props) {
  const idTitulo = useId()
  const alto = horizontal ? Math.max(180, datos.length * ALTO_BARRA + 40) : 260

  return (
    <section className="grafica tarjeta" aria-labelledby={idTitulo}>
      <h2 id={idTitulo}>{titulo}</h2>
      <p className="grafica-descripcion">{descripcion}</p>

      {/* inert: Recharts deja varios elementos SVG enfocables con Tab; así el teclado salta directo a la tabla */}
      <div className="grafica-dibujo" aria-hidden="true" inert>
        <ResponsiveContainer width="100%" height={alto}>
          <BarChart
            data={datos}
            layout={horizontal ? 'vertical' : 'horizontal'}
            margin={{ top: 28, right: 40, bottom: 8, left: 0 }}
            accessibilityLayer={false}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#cbd2d9" horizontal={!horizontal} vertical={horizontal} />
            {horizontal ? (
              <>
                <XAxis type="number" allowDecimals={false} stroke="#52606d" domain={ESPACIO_ARRIBA} />
                <YAxis type="category" dataKey="nombre" width={130} tickFormatter={recortar} stroke="#52606d" />
              </>
            ) : (
              <>
                <XAxis type="category" dataKey="nombre" stroke="#52606d" />
                <YAxis type="number" allowDecimals={false} stroke="#52606d" domain={ESPACIO_ARRIBA} />
              </>
            )}
            {/* El número va escrito sobre cada barra: no hay que adivinarlo por el color o la altura */}
            <Bar dataKey="total" fill="#c8102e" isAnimationActive={false}>
              <LabelList dataKey="total" position={horizontal ? 'right' : 'top'} fill="#1f2933" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <details className="grafica-tabla">
        <summary>Ver los datos en tabla</summary>
        <div className="tabla-contenedor">
          <table className="tabla">
            <caption className="solo-lectores">{titulo}</caption>
            <thead>
              <tr>
                <th scope="col">{etiquetaNombre}</th>
                <th scope="col">{etiquetaValor}</th>
              </tr>
            </thead>
            <tbody>
              {datos.map((d) => (
                <tr key={d.nombre}>
                  <th scope="row">{d.nombre}</th>
                  <td>{d.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  )
}
