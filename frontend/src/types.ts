// Tipos compartidos. Reflejan lo que devuelve la API (GET /api/auth/me).

export type Rol = 'administrador' | 'capturista'

export interface Usuario {
  id: number
  nombre: string
  correo: string
  rol: Rol
  activo: boolean
  creado_en: string
}
