import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { pedirToken, pedirUsuarioActual } from '../api/auth.ts'
import { borrarToken, guardarToken, leerToken, registrarAlExpirarSesion } from '../api/cliente.ts'
import type { Usuario } from '../types.ts'

interface AuthValor {
  usuario: Usuario | null
  cargando: boolean // true mientras se comprueba si el token guardado sigue siendo válido
  login: (correo: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthValor | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  // Si hay un token guardado, hay que preguntarle a la API quién es antes de decidir qué mostrar
  const [cargando, setCargando] = useState(() => leerToken() !== null)

  // Al abrir la app: recuperar la sesión con el token guardado (si lo hay)
  useEffect(() => {
    if (leerToken() === null) return

    let vigente = true
    pedirUsuarioActual()
      .then((u) => {
        if (vigente) setUsuario(u)
      })
      .catch(() => {
        // Token vencido o inválido: la sesión no se recupera (el 401 ya borró el token)
        borrarToken()
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [])

  // Si la API responde 401 en cualquier petición, se cierra la sesión.
  // Las rutas privadas ven usuario = null y mandan a /login.
  useEffect(() => {
    registrarAlExpirarSesion(() => setUsuario(null))
    return () => registrarAlExpirarSesion(null)
  }, [])

  async function login(correo: string, password: string) {
    const { access_token } = await pedirToken(correo, password)
    guardarToken(access_token)
    setUsuario(await pedirUsuarioActual())
  }

  function logout() {
    borrarToken()
    setUsuario(null)
  }

  return <AuthContext.Provider value={{ usuario, cargando, login, logout }}>{children}</AuthContext.Provider>
}

// Hook para leer la sesión desde cualquier componente
// (se deja junto al contexto a propósito para que sea fácil de seguir)
// oxlint-disable-next-line react/only-export-components
export function useAuth(): AuthValor {
  const valor = useContext(AuthContext)
  if (!valor) throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  return valor
}
