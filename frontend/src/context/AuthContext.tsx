import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'
import type { Usuario } from '../types.ts'

// PROVISIONAL (C01): la sesión vive solo en memoria y no habla con la API.
// En C03 este archivo se reemplaza por el contexto real (token + /api/auth/me).

interface AuthValor {
  usuario: Usuario | null
  iniciarSesion: (usuario: Usuario) => void
  cerrarSesion: () => void
}

const AuthContext = createContext<AuthValor | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)

  const valor: AuthValor = {
    usuario,
    iniciarSesion: setUsuario,
    cerrarSesion: () => setUsuario(null),
  }

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}

// Hook para leer la sesión desde cualquier componente
// (se deja junto al contexto a propósito para que sea fácil de seguir)
// oxlint-disable-next-line react/only-export-components
export function useAuth(): AuthValor {
  const valor = useContext(AuthContext)
  if (!valor) throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  return valor
}
