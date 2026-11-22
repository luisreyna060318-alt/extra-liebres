// GET /api/dashboard/resumen?semestre=<id>: cifras del tablero de un semestre (HU-07.1)
import type { ResumenTablero } from '../types.ts'
import { api } from './cliente.ts'

export function pedirResumen(idsemestre: number): Promise<ResumenTablero> {
  return api.get<ResumenTablero>(`/api/dashboard/resumen?semestre=${idsemestre}`)
}
