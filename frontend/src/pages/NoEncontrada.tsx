import { Link } from 'react-router-dom'
import { useTitulo } from '../hooks/useTitulo.ts'

export default function NoEncontrada() {
  useTitulo('Página no encontrada')

  return (
    <section>
      <h1>Página no encontrada</h1>
      <p>
        La dirección que escribiste no existe. <Link to="/">Volver al inicio</Link>
      </p>
    </section>
  )
}
