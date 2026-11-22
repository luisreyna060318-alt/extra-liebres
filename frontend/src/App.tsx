import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.tsx'
import RutaPrivada from './components/RutaPrivada.tsx'
import AlumnoFormulario from './pages/AlumnoFormulario.tsx'
import AlumnoHistorial from './pages/AlumnoHistorial.tsx'
import Alumnos from './pages/Alumnos.tsx'
import Catalogos from './pages/Catalogos.tsx'
import Consultas from './pages/Consultas.tsx'
import GrupoDetalle from './pages/GrupoDetalle.tsx'
import GrupoFormulario from './pages/GrupoFormulario.tsx'
import Grupos from './pages/Grupos.tsx'
import Login from './pages/Login.tsx'
import NoEncontrada from './pages/NoEncontrada.tsx'
import Registro from './pages/Registro.tsx'
import Tablero from './pages/Tablero.tsx'
import Usuarios from './pages/Usuarios.tsx'

// Todas las rutas comparten el Layout (header, nav, main, footer)
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Públicas */}
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />

        {/* Privadas: sin sesión redirigen a /login */}
        <Route element={<RutaPrivada />}>
          <Route path="/" element={<Tablero />} />
          <Route path="/alumnos" element={<Alumnos />} />
          <Route path="/alumnos/nuevo" element={<AlumnoFormulario />} />
          <Route path="/alumnos/:nocontrol" element={<AlumnoHistorial />} />
          <Route path="/alumnos/:nocontrol/editar" element={<AlumnoFormulario />} />
          <Route path="/grupos" element={<Grupos />} />
          <Route path="/grupos/nuevo" element={<GrupoFormulario />} />
          <Route path="/grupos/:id" element={<GrupoDetalle />} />
          <Route path="/grupos/:id/editar" element={<GrupoFormulario />} />
          <Route path="/consultas" element={<Consultas />} />
        </Route>

        {/* Solo administrador (la API también lo valida en el servidor) */}
        <Route element={<RutaPrivada soloAdmin />}>
          <Route path="/catalogos" element={<Catalogos />} />
          <Route path="/usuarios" element={<Usuarios />} />
        </Route>

        <Route path="*" element={<NoEncontrada />} />
      </Route>
    </Routes>
  )
}
