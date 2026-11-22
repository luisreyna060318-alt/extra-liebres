import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.tsx'
import { useTitulo } from '../hooks/useTitulo.ts'

// Placeholder: el formulario real llega en el commit C04
export default function Login() {
  useTitulo('Iniciar sesión')
  const { usuario } = useAuth()

  // Si ya hay sesión, no tiene caso mostrar el login
  if (usuario) return <Navigate to="/" replace />

  return (
    <section>
      <h1>Iniciar sesión</h1>
      <p>Pantalla en construcción.</p>
      <p>
        ¿No tienes cuenta? <Link to="/registro">Crear cuenta</Link>
      </p>
    </section>
  )
}
