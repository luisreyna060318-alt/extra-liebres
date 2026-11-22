import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.tsx'

// Estructura semántica común: header, nav, main y footer
export default function Layout() {
  const { usuario, logout } = useAuth()
  const navegar = useNavigate()
  const esAdmin = usuario?.rol === 'administrador'
  const esLector = usuario?.rol === 'lector'

  // La app es una SPA: al cambiar de pantalla la página no se recarga y el foco se queda en el enlace pulsado
  // (que puede desaparecer). Se mueve el foco al contenido para que teclado y lector de pantalla empiecen ahí.
  const { pathname } = useLocation()
  const rutaAnterior = useRef(pathname)
  useEffect(() => {
    if (rutaAnterior.current === pathname) return // la primera carga no roba el foco
    rutaAnterior.current = pathname
    document.getElementById('contenido')?.focus()
  }, [pathname])

  // Buscador global (HU-06.2): lleva a /buscar?q=texto, donde se muestran los resultados
  const [texto, setTexto] = useState('')
  function buscar(evento: FormEvent) {
    evento.preventDefault()
    const q = texto.trim()
    if (q) navegar(`/buscar?q=${encodeURIComponent(q)}`)
  }

  function cerrarSesion() {
    logout()
    navegar('/login')
  }

  return (
    <div className="app">
      <a className="saltar" href="#contenido">
        Saltar al contenido
      </a>

      <header className="encabezado">
        <Link to="/" className="marca">
          {/* El logo es decorativo: el nombre de la aplicación ya está escrito al lado */}
          <img src="/logo.png" alt="" width="44" height="44" className="marca-logo" />
          Extra-Liebres
        </Link>

        {usuario && !esLector && (
          <form className="buscador-global" role="search" aria-label="Buscar en todo el sistema" onSubmit={buscar}>
            <label htmlFor="buscador-global-texto" className="solo-lectores">
              Buscar alumnos y grupos
            </label>
            <input
              id="buscador-global-texto"
              type="search"
              placeholder="Buscar alumnos y grupos"
              maxLength={60}
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
            />
            <button type="submit" className="boton boton-secundario">
              Buscar
            </button>
          </form>
        )}

        {usuario && (
          <div className="sesion">
            <span>
              {usuario.nombre} <small>({usuario.rol})</small>
            </span>
            <button type="button" className="boton boton-secundario" onClick={cerrarSesion}>
              Cerrar sesión
            </button>
          </div>
        )}
      </header>

      <nav className="navegacion" aria-label="Principal">
        <ul>
          {usuario ? (
            <>
              <li><NavLink to="/" end>Tablero</NavLink></li>
              {/* El lector solo ve Tablero y Grupos; la API protege lo demás de todos modos */}
              {!esLector && <li><NavLink to="/alumnos">Alumnos</NavLink></li>}
              <li><NavLink to="/grupos">Grupos</NavLink></li>
              {!esLector && <li><NavLink to="/consultas">Consultas</NavLink></li>}
              {/* Solo se muestran a administrador; la API protege estas rutas de todos modos */}
              {esAdmin && <li><NavLink to="/catalogos">Catálogos</NavLink></li>}
              {esAdmin && <li><NavLink to="/usuarios">Usuarios</NavLink></li>}
            </>
          ) : (
            <>
              <li><NavLink to="/login">Iniciar sesión</NavLink></li>
              <li><NavLink to="/registro">Crear cuenta</NavLink></li>
            </>
          )}
        </ul>
      </nav>

      {/* tabIndex=-1 permite que el enlace "Saltar al contenido" mueva el foco aquí */}
      <main id="contenido" className="contenido" tabIndex={-1}>
        <Outlet />
      </main>

      <footer className="pie">
        <p>Extra-Liebres · Programación Web (AEB-1055) · ITCJ</p>
      </footer>
    </div>
  )
}
