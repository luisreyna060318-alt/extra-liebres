// Cliente de la API: un envoltorio de fetch que agrega el token, usa la URL base
// y convierte los errores HTTP en un error con el mensaje del servidor.

// URL base de la API (se define en frontend/.env, ver .env.example)
const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const CLAVE_TOKEN = 'extra-liebres-token'

// --- Token: en memoria (rápido) y en localStorage (para que sobreviva a recargar la página) ---
// Nunca se imprime en consola.
let tokenEnMemoria: string | null = null

export function leerToken(): string | null {
  if (tokenEnMemoria) return tokenEnMemoria
  try {
    tokenEnMemoria = localStorage.getItem(CLAVE_TOKEN)
  } catch {
    // Si el navegador bloquea localStorage, se trabaja solo con la memoria
  }
  return tokenEnMemoria
}

export function guardarToken(token: string): void {
  tokenEnMemoria = token
  try {
    localStorage.setItem(CLAVE_TOKEN, token)
  } catch {
    // Igual que arriba: no es grave si no se puede guardar
  }
}

export function borrarToken(): void {
  tokenEnMemoria = null
  try {
    localStorage.removeItem(CLAVE_TOKEN)
  } catch {
    // Nada que hacer
  }
}

// --- Error de la API ---
// campos: mensajes por campo cuando el servidor responde 422 (por ejemplo { password: "..." })
export class ErrorApi extends Error {
  status: number
  campos: Record<string, string>

  constructor(mensaje: string, status: number, campos: Record<string, string> = {}) {
    super(mensaje)
    this.name = 'ErrorApi'
    this.status = status
    this.campos = campos
  }
}

// --- Qué hacer cuando la sesión ya no sirve (401) ---
// AuthContext registra aquí su función para cerrar la sesión; así este archivo no depende de React.
let alExpirarSesion: (() => void) | null = null

export function registrarAlExpirarSesion(funcion: (() => void) | null): void {
  alExpirarSesion = funcion
}

// FastAPI responde {"detail": "mensaje"} o, en el 422, {"detail": [{loc, msg}, ...]}
function leerError(status: number, cuerpo: unknown): ErrorApi {
  const detalle = (cuerpo as { detail?: unknown } | null)?.detail

  if (typeof detalle === 'string') return new ErrorApi(detalle, status)

  if (Array.isArray(detalle)) {
    const campos: Record<string, string> = {}
    for (const item of detalle as { loc?: unknown[]; msg?: string }[]) {
      // Pydantic antepone "Value error, " a los mensajes propios: se lo quitamos
      const mensaje = (item.msg ?? 'Dato no válido').replace(/^Value error, /, '')
      const campo = String(item.loc?.[item.loc.length - 1] ?? 'general')
      campos[campo] = mensaje
    }
    const resumen = Object.values(campos).join('. ') || 'Revisa los datos capturados'
    return new ErrorApi(resumen, status, campos)
  }

  return new ErrorApi(`Error del servidor (${status})`, status)
}

interface Opciones {
  metodo?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  cuerpo?: unknown // se envía como JSON
  formulario?: Record<string, string> // se envía como application/x-www-form-urlencoded (el login lo pide así)
}

export async function peticion<T>(ruta: string, opciones: Opciones = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' }
  const token = leerToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let body: BodyInit | undefined
  if (opciones.formulario) {
    body = new URLSearchParams(opciones.formulario) // fetch pone el Content-Type solo
  } else if (opciones.cuerpo !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(opciones.cuerpo)
  }

  let respuesta: Response
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, { method: opciones.metodo ?? 'GET', headers, body })
  } catch {
    // fetch solo falla así cuando no hay red o el servidor no responde
    throw new ErrorApi('No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.', 0)
  }

  // 204 no trae cuerpo
  if (respuesta.status === 204) return undefined as T

  // Si el cuerpo no es JSON válido, se queda en null
  const cuerpo: unknown = await respuesta.json().catch(() => null)

  if (!respuesta.ok) {
    // 401 = sesión vencida o inválida: se borra el token y se avisa a AuthContext
    if (respuesta.status === 401) {
      borrarToken()
      alExpirarSesion?.()
    }
    throw leerError(respuesta.status, cuerpo)
  }

  return cuerpo as T
}

// Atajos para los métodos más usados
export const api = {
  get: <T>(ruta: string) => peticion<T>(ruta),
  post: <T>(ruta: string, cuerpo?: unknown) => peticion<T>(ruta, { metodo: 'POST', cuerpo }),
  put: <T>(ruta: string, cuerpo?: unknown) => peticion<T>(ruta, { metodo: 'PUT', cuerpo }),
  patch: <T>(ruta: string, cuerpo?: unknown) => peticion<T>(ruta, { metodo: 'PATCH', cuerpo }),
  delete: <T>(ruta: string) => peticion<T>(ruta, { metodo: 'DELETE' }),
}
