// Búsqueda global en alumnos y grupos (HU-06.2).
// El contrato sale del backend (routers/busqueda.py y schemas/busqueda.py).
import { api } from './cliente.ts'

export interface AlumnoCoincidencia {
  nocontrol: string
  alumno: string // "Apellidos Nombre"
  carrera: string
}

export interface GrupoCoincidencia {
  idgrupo: number
  descripcion: string // por ejemplo "Fútbol (grupo 3), lunes de 08:00 a 09:00"
  semestre: string
  promotor: string
}

// Cada tipo trae como máximo 10 coincidencias; *_hay_mas avisa si hubo más
export interface Busqueda {
  q: string
  alumnos: AlumnoCoincidencia[]
  alumnos_hay_mas: boolean
  grupos: GrupoCoincidencia[]
  grupos_hay_mas: boolean
}

export const MINIMO_BUSQUEDA = 2 // el servidor responde 422 con menos letras

// GET /api/busqueda?q=
export function buscar(q: string): Promise<Busqueda> {
  return api.get<Busqueda>(`/api/busqueda?${new URLSearchParams({ q }).toString()}`)
}
