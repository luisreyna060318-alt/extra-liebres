// Llamadas a /api/auth/*. Los contratos salen del backend (routers/auth.py y schemas/).
import type { Usuario } from '../types.ts'
import { api, peticion } from './cliente.ts'

interface Token {
  access_token: string
  token_type: string
}

// POST /api/auth/login: el backend usa el formulario estándar de OAuth2,
// así que se manda como formulario y el correo va en el campo "username".
export function pedirToken(correo: string, password: string): Promise<Token> {
  return peticion<Token>('/api/auth/login', {
    metodo: 'POST',
    formulario: { username: correo, password },
  })
}

// POST /api/auth/register: crea la cuenta (siempre con rol capturista). Devuelve 201.
export function registrarCuenta(datos: { nombre: string; correo: string; password: string }): Promise<Usuario> {
  return api.post<Usuario>('/api/auth/register', datos)
}

// GET /api/auth/me: el usuario dueño del token actual
export function pedirUsuarioActual(): Promise<Usuario> {
  return api.get<Usuario>('/api/auth/me')
}
