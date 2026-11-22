import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.tsx'

interface Props {
  soloAdmin?: boolean
  soloPersonal?: boolean // administrador y capturista (el lector no entra)
}

// Protege un grupo de rutas. Ocultar enlaces no es seguridad: el servidor vuelve a validar el rol.
export default function RutaPrivada({ soloAdmin = false, soloPersonal = false }: Props) {
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

  if (soloPersonal && usuario.rol === 'lector') {
    return (
      <section>
        <h1>Sin permiso</h1>
        <p role="alert">
          Tu cuenta es de lector: solo puede ver el tablero y los grupos. Pide a un administrador que te dé más permisos.
        </p>
      </section>
    )
  }

  return <Outlet />
}
