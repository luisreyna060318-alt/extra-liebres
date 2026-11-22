// Llamadas a /api/grupos y /api/clima. Los contratos salen del backend
// (routers/grupos.py, schemas/grupo.py y schemas/clima.py).
import type { Clima, Grupo, GrupoEntrada, Pagina } from '../types.ts'
import { api } from './cliente.ts'

// Filtros de la lista: texto vacío = sin filtro
export interface FiltrosGrupos {
  semestre: string // idsemestre
  extraescolar: string // idextraescolar
  promotor: string // RFC
  dia: string
}

export const TAMANO_PAGINA = 10 // RN-11

// GET /api/grupos?semestre=&extraescolar=&promotor=&dia=&page=&size=
export function listarGrupos(filtros: FiltrosGrupos, pagina: number): Promise<Pagina<Grupo>> {
  const parametros = new URLSearchParams({ page: String(pagina), size: String(TAMANO_PAGINA) })
  // Solo se mandan los filtros que tienen valor
  for (const [nombre, valor] of Object.entries(filtros)) {
    if (valor) parametros.set(nombre, valor)
  }
  return api.get<Pagina<Grupo>>(`/api/grupos?${parametros.toString()}`)
}

export function obtenerGrupo(id: string): Promise<Grupo> {
  return api.get<Grupo>(`/api/grupos/${encodeURIComponent(id)}`)
}

// POST /api/grupos (201). Puede responder 404, 409 (cruce de horario) o 422.
export function crearGrupo(datos: GrupoEntrada): Promise<Grupo> {
  return api.post<Grupo>('/api/grupos', datos)
}

// PUT /api/grupos/{id}: reemplaza los datos y el servidor vuelve a revisar los cruces
export function actualizarGrupo(id: string, datos: GrupoEntrada): Promise<Grupo> {
  return api.put<Grupo>(`/api/grupos/${encodeURIComponent(id)}`, datos)
}

// GET /api/clima: temperatura y probabilidad de lluvia en Ciudad Juárez (el backend consulta Open-Meteo)
export function pedirClima(): Promise<Clima> {
  return api.get<Clima>('/api/clima')
}
