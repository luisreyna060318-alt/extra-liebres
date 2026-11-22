// Llamadas de las pantallas de administración: catálogos y usuarios.
// Las rutas y los campos salen del backend (routers y schemas). Todas exigen sesión y las
// escrituras solo las permite el administrador (el servidor lo valida).
import type {
  ActividadAdmin,
  ActividadCambios,
  ActividadNueva,
  FiltroEstado,
  FiltrosUsuarios,
  PromotorAdmin,
  PromotorCambios,
  PromotorNuevo,
  SemestreAdmin,
  SemestreEntrada,
  UsuarioAdmin,
  UsuarioCambios,
} from '../tiposAdmin.ts'
import type { Pagina } from '../types.ts'
import { api } from './cliente.ts'
import { TAMANO_PAGINA } from './grupos.ts'

// Arma "page=1&size=10&q=...". Solo se mandan los filtros que tienen valor.
function consulta(pagina: number, filtros: Record<string, string> = {}): string {
  const parametros = new URLSearchParams({ page: String(pagina), size: String(TAMANO_PAGINA) })
  for (const [nombre, valor] of Object.entries(filtros)) {
    if (valor) parametros.set(nombre, valor)
  }
  return parametros.toString()
}

// --- Promotores: /api/promotores ---
export function listarPromotores(q: string, estado: FiltroEstado, pagina: number): Promise<Pagina<PromotorAdmin>> {
  return api.get<Pagina<PromotorAdmin>>(`/api/promotores?${consulta(pagina, { q, estado })}`)
}

export function crearPromotor(datos: PromotorNuevo): Promise<PromotorAdmin> {
  return api.post<PromotorAdmin>('/api/promotores', datos)
}

export function actualizarPromotor(rfc: string, datos: PromotorCambios): Promise<PromotorAdmin> {
  return api.put<PromotorAdmin>(`/api/promotores/${encodeURIComponent(rfc)}`, datos)
}

export function eliminarPromotor(rfc: string): Promise<void> {
  return api.delete<void>(`/api/promotores/${encodeURIComponent(rfc)}`)
}

// --- Actividades: /api/extraescolares ---
export function listarActividades(q: string, estado: FiltroEstado, pagina: number): Promise<Pagina<ActividadAdmin>> {
  return api.get<Pagina<ActividadAdmin>>(`/api/extraescolares?${consulta(pagina, { q, estado })}`)
}

export function crearActividad(datos: ActividadNueva): Promise<ActividadAdmin> {
  return api.post<ActividadAdmin>('/api/extraescolares', datos)
}

export function actualizarActividad(id: number, datos: ActividadCambios): Promise<ActividadAdmin> {
  return api.put<ActividadAdmin>(`/api/extraescolares/${id}`, datos)
}

export function eliminarActividad(id: number): Promise<void> {
  return api.delete<void>(`/api/extraescolares/${id}`)
}

// --- Semestres: /api/semestres (el servidor ya los entrega del más reciente al más antiguo) ---
export function listarSemestres(pagina: number): Promise<Pagina<SemestreAdmin>> {
  return api.get<Pagina<SemestreAdmin>>(`/api/semestres?${consulta(pagina)}`)
}

export function crearSemestre(datos: SemestreEntrada): Promise<SemestreAdmin> {
  return api.post<SemestreAdmin>('/api/semestres', datos)
}

export function actualizarSemestre(id: number, datos: SemestreEntrada): Promise<SemestreAdmin> {
  return api.put<SemestreAdmin>(`/api/semestres/${id}`, datos)
}

export function eliminarSemestre(id: number): Promise<void> {
  return api.delete<void>(`/api/semestres/${id}`)
}

// --- Usuarios: /api/usuarios ---
export function listarUsuarios(filtros: FiltrosUsuarios, pagina: number): Promise<Pagina<UsuarioAdmin>> {
  // La API espera activo=true|false; "todas" no manda nada
  const activo = filtros.cuentas === 'activas' ? 'true' : filtros.cuentas === 'suspendidas' ? 'false' : ''
  return api.get<Pagina<UsuarioAdmin>>(`/api/usuarios?${consulta(pagina, { q: filtros.q, rol: filtros.rol, activo })}`)
}

// PATCH: cambia el rol y/o suspende o reactiva. Puede responder 409 si dejaría al sistema sin administradores.
export function actualizarUsuario(id: number, cambios: UsuarioCambios): Promise<UsuarioAdmin> {
  return api.patch<UsuarioAdmin>(`/api/usuarios/${id}`, cambios)
}
