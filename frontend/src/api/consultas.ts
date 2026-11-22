// Llamada a la consulta transversal de inscritos (HU-06.1).
// El contrato sale del backend (routers/consultas.py y schemas/consulta.py).
import type { Pagina } from '../types.ts'
import { api, descargarArchivo } from './cliente.ts'

// Un renglón de la consulta (InscritoConsulta)
export interface InscritoConsulta {
  nocontrol: string
  alumno: string
  carrera: string
  idgrupo: number
  idextraescolar: number
  actividad: string
  idsemestre: number
  semestre: string // ya armado, por ejemplo "Enero-Junio 2026"
  promotor: string
  calificacion: number | null
  desempenio: string | null
}

// Texto vacío = sin filtro
export interface FiltrosConsulta {
  extraescolar: string // idextraescolar
  semestre: string // idsemestre
}

export const TAMANO_CONSULTA = 10 // RN-11

// GET /api/consultas/inscritos?extraescolar=&semestre=&page=&size=
export function consultarInscritos(filtros: FiltrosConsulta, pagina: number): Promise<Pagina<InscritoConsulta>> {
  const parametros = new URLSearchParams({ page: String(pagina), size: String(TAMANO_CONSULTA) })
  if (filtros.extraescolar) parametros.set('extraescolar', filtros.extraescolar)
  if (filtros.semestre) parametros.set('semestre', filtros.semestre)
  return api.get<Pagina<InscritoConsulta>>(`/api/consultas/inscritos?${parametros.toString()}`)
}

// GET /api/export/inscritos.csv|xml?extraescolar=&semestre= (solo administrador; trae todos los renglones, sin paginar)
export function exportarInscritos(formato: 'csv' | 'xml', filtros: FiltrosConsulta): Promise<void> {
  const parametros = new URLSearchParams()
  if (filtros.extraescolar) parametros.set('extraescolar', filtros.extraescolar)
  if (filtros.semestre) parametros.set('semestre', filtros.semestre)
  const consulta = parametros.toString()
  return descargarArchivo(`/api/export/inscritos.${formato}${consulta ? `?${consulta}` : ''}`, `inscritos.${formato}`)
}
