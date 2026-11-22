// Tipos de las pantallas de administración (catálogos y usuarios).
// Reflejan los esquemas del servidor: backend/app/schemas/{promotor,extraescolar,semestre,usuario}.py
import type { Rol, TipoActividad, Usuario } from './types.ts'

// Filtro de estado de promotores y actividades (parámetro ?estado= de la API)
export type FiltroEstado = 'activos' | 'bajas' | 'todos'

// --- Salida: lo que devuelve la API (aquí "activo" siempre viene) ---
export interface PromotorAdmin {
  rfc: string
  nombre: string
  apaterno: string
  amaterno: string | null
  activo: boolean
}

export interface ActividadAdmin {
  idextraescolar: number
  nombreextra: string
  tipo: TipoActividad
  al_aire_libre: boolean
  activo: boolean
}

export interface SemestreAdmin {
  idsemestre: number
  anio: number
  mesinicio: number
  mestermino: number
}

// --- Entrada: lo que se manda al crear (POST) o editar (PUT) ---
export interface PromotorNuevo {
  rfc: string
  nombre: string
  apaterno: string
  amaterno: string | null
}

// En el PUT el RFC no viaja (va en la URL). "activo" sirve para desactivar o reactivar.
export interface PromotorCambios {
  nombre: string
  apaterno: string
  amaterno: string | null
  activo?: boolean
}

export interface ActividadNueva {
  nombreextra: string
  tipo: TipoActividad
  al_aire_libre: boolean
}

export interface ActividadCambios extends ActividadNueva {
  activo?: boolean
}

export interface SemestreEntrada {
  anio: number
  mesinicio: number
  mestermino: number
}

// --- Usuarios ---
export type UsuarioAdmin = Usuario

export type FiltroCuentas = 'todas' | 'activas' | 'suspendidas'

export interface FiltrosUsuarios {
  q: string
  rol: '' | Rol // '' = todos los roles
  cuentas: FiltroCuentas
}

// PATCH /api/usuarios/{id}: se manda solo lo que cambia
export interface UsuarioCambios {
  rol?: Rol
  activo?: boolean
}
