import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { registrarCuenta } from '../api/auth.ts'
import { ErrorApi } from '../api/cliente.ts'
import { useAuth } from '../context/AuthContext.tsx'
import { useTitulo } from '../hooks/useTitulo.ts'
import { validarCorreo, validarNombre, validarPasswordNueva } from '../utils/validaciones.ts'

interface Errores {
  nombre?: string
  correo?: string
  password?: string
}

export default function Registro() {
  useTitulo('Crear cuenta')
  const { usuario } = useAuth()
  const navegar = useNavigate()

  const [nombre, setNombre] = useState('')
  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
  const [errores, setErrores] = useState<Errores>({})
  const [errorServidor, setErrorServidor] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Quien ya inició sesión no necesita crear cuenta
  if (usuario) return <Navigate to="/" replace />

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setErrorServidor('')

    // 1) Validar en el cliente. Lo capturado no se borra aunque haya errores (HU-01.1 CA3).
    const nuevos: Errores = {
      nombre: validarNombre(nombre) || undefined,
      correo: validarCorreo(correo) || undefined,
      password: validarPasswordNueva(password) || undefined,
    }
    setErrores(nuevos)
    const primerError = (['nombre', 'correo', 'password'] as const).find((campo) => nuevos[campo])
    if (primerError) {
      document.getElementById(primerError)?.focus()
      return
    }

    // 2) Mandar los datos a la API
    setEnviando(true)
    try {
      await registrarCuenta({ nombre: nombre.trim(), correo: correo.trim(), password })
      // Cuenta creada: se manda a /login con un aviso
      navegar('/login', { replace: true, state: { mensaje: 'Cuenta creada. Ya puedes iniciar sesión.' } })
    } catch (e) {
      if (e instanceof ErrorApi && e.status === 422) {
        // El servidor rechazó un campo: el mensaje se muestra junto a ese campo
        setErrores({ nombre: e.campos.nombre, correo: e.campos.correo, password: e.campos.password })
      }
      // 409 = el correo ya existe, y cualquier otro error se muestra arriba del botón
      setErrorServidor(e instanceof Error ? e.message : 'No se pudo crear la cuenta.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section>
      <h1>Crear cuenta</h1>
      <p>Las cuentas nuevas tienen rol de capturista. Un administrador puede cambiarlo después.</p>

      <form className="formulario" onSubmit={enviar} noValidate>
        <div className="campo">
          <label htmlFor="nombre">Nombre completo</label>
          <input
            id="nombre"
            type="text"
            autoComplete="name"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            aria-invalid={errores.nombre ? true : undefined}
            aria-describedby={errores.nombre ? 'nombre-error' : undefined}
          />
          {errores.nombre && (
            <p id="nombre-error" className="campo-error">
              {errores.nombre}
            </p>
          )}
        </div>

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
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={errores.password ? true : undefined}
            aria-describedby={errores.password ? 'password-ayuda password-error' : 'password-ayuda'}
          />
          <p id="password-ayuda" className="campo-ayuda">
            Mínimo 8 caracteres, con letras y números.
          </p>
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
          {enviando ? 'Creando cuenta…' : 'Crear cuenta'}
        </button>
      </form>

      <p className="enlace-aparte">
        ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
      </p>
    </section>
  )
}
