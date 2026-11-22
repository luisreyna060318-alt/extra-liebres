import { Link } from 'react-router-dom'
import { useTitulo } from '../hooks/useTitulo.ts'

// Placeholder: el tablero con gráficas y clima llega en el commit C13
export default function Tablero() {
  useTitulo('Tablero')

  return (
    <section>
      <h1>Tablero</h1>
      <p>Pantalla en construcción. Mientras tanto, entra a una sección:</p>

      <ul className="rejilla">
        <li className="tarjeta">
          <h2><Link to="/alumnos">Alumnos</Link></h2>
          <p>Consulta y captura de alumnos y su historial.</p>
        </li>
        <li className="tarjeta">
          <h2><Link to="/grupos">Grupos</Link></h2>
          <p>Grupos por semestre, actividad y promotor.</p>
        </li>
        <li className="tarjeta">
          <h2><Link to="/consultas">Consultas</Link></h2>
          <p>Inscritos por actividad y semestre.</p>
        </li>
      </ul>
    </section>
  )
}
