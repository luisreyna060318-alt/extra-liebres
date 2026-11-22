import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.tsx'

interface Props {
  soloAdmin?: boolean
}

// Protege un grupo de rutas. Ocultar enlaces no es seguridad: el servidor vuelve a validar el rol.
export default function RutaPrivada({ soloAdmin = false }: Props) {
  const { usuario, cargando } = useAuth()
  const ubicacion = useLocation()

  // Aún se está comprobando el token guardado: no se redirige todavía
  if (cargando) {
    return (
      <div className="estado" role="status">
        <p>Cargando…</p>
      </div>
    )
  }

  // Sin sesión: a /login, recordando a dónde quería ir
  if (!usuario) {
    return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />
  }

  if (soloAdmin && usuario.rol !== 'administrador') {
    return (
      <section>
        <h1>Sin permiso</h1>
        <p role="alert">Esta sección es solo para administradores.</p>
      </section>
    )
  }

  return <Outlet />
}
