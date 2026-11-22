import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.tsx'
import { useTitulo } from '../hooks/useTitulo.ts'

// Placeholder: el formulario real llega en el commit C04
export default function Login() {
  useTitulo('Iniciar sesión')
  const { usuario, iniciarSesion } = useAuth()

  // Si ya hay sesión, no tiene caso mostrar el login
  if (usuario) return <Navigate to="/" replace />

  return (
    <section>
      <h1>Iniciar sesión</h1>
      <p>Pantalla en construcción.</p>

      {/* Solo en desarrollo (npm run dev): permite probar el menú por rol sin API. Se quita en C03. */}
      {import.meta.env.DEV && (
        <p>
          <button
            type="button"
            className="boton"
            onClick={() =>
              iniciarSesion({
                id: 0,
                nombre: 'Persona de prueba',
                correo: 'prueba@ejemplo.com',
                rol: 'capturista',
                activo: true,
                creado_en: '',
              })
            }
          >
            Simular sesión de capturista
          </button>{' '}
          <button
            type="button"
            className="boton boton-secundario"
            onClick={() =>
              iniciarSesion({
                id: 0,
                nombre: 'Admin de prueba',
                correo: 'admin@ejemplo.com',
                rol: 'administrador',
                activo: true,
                creado_en: '',
              })
            }
          >
            Simular sesión de administrador
          </button>
        </p>
      )}

      <p>
        ¿No tienes cuenta? <Link to="/registro">Crear cuenta</Link>
      </p>
    </section>
  )
}
