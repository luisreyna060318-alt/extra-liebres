import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.tsx'
import { useTitulo } from '../hooks/useTitulo.ts'
import { validarCorreo, validarPasswordLogin } from '../utils/validaciones.ts'

interface Errores {
  correo?: string
  password?: string
}

// Estado que otras pantallas mandan al navegar a /login
interface EstadoNavegacion {
  desde?: string // la ruta privada a la que se quería entrar
  mensaje?: string // por ejemplo, "Cuenta creada" después del registro
}

export default function Login() {
  useTitulo('Iniciar sesión')
  const { usuario, login } = useAuth()
  const estado = useLocation().state as EstadoNavegacion | null

  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
  const [errores, setErrores] = useState<Errores>({})
  const [errorServidor, setErrorServidor] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Con sesión iniciada se vuelve a donde se quería entrar (o al tablero)
  if (usuario) return <Navigate to={estado?.desde ?? '/'} replace />

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault() // evita que el navegador recargue la página
    setErrorServidor('')

    // 1) Validar en el cliente, con el mensaje junto a cada campo
    const nuevos: Errores = {
      correo: validarCorreo(correo) || undefined,
      password: validarPasswordLogin(password) || undefined,
    }
    setErrores(nuevos)
    if (nuevos.correo || nuevos.password) {
      // El foco va al primer campo con error para que se note (también con lector de pantalla)
      document.getElementById(nuevos.correo ? 'correo' : 'password')?.focus()
      return
    }

    // 2) Mandar los datos a la API. Si sale bien, AuthContext guarda al usuario y esta pantalla redirige.
    setEnviando(true)
    try {
      await login(correo.trim(), password)
    } catch (e) {
      // El mensaje viene del servidor (por ejemplo, "Correo o contraseña incorrectos")
      setErrorServidor(e instanceof Error ? e.message : 'No se pudo iniciar sesión.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section>
      <h1>Iniciar sesión</h1>

      {estado?.mensaje && (
        <p role="status" className="alerta alerta-exito">
          {estado.mensaje}
        </p>
      )}

      {/* noValidate: los mensajes los muestra nuestra validación, no el navegador */}
      <form className="formulario" onSubmit={enviar} noValidate>
        <div className="campo">
          <label htmlFor="correo">Correo electrónico</label>
          <input
            id="correo"
            type="email"
            autoComplete="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            aria-invalid={errores.correo ? true : undefined}
            aria-describedby={errores.correo ? 'correo-error' : undefined}
          />
          {errores.correo && (
            <p id="correo-error" className="campo-error">
              {errores.correo}
            </p>
          )}
        </div>

        <div className="campo">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={errores.password ? true : undefined}
            aria-describedby={errores.password ? 'password-error' : undefined}
          />
          {errores.password && (
            <p id="password-error" className="campo-error">
              {errores.password}
            </p>
          )}
        </div>

        {errorServidor && (
          <p role="alert" className="alerta alerta-error">
            {errorServidor}
          </p>
        )}

        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Entrando…' : 'Entrar'}
        </button>
      </form>

      <p className="enlace-aparte">
        ¿No tienes cuenta? <Link to="/registro">Crear cuenta</Link>
      </p>
    </section>
  )
}
