// Llamadas a las inscripciones de un grupo y a la búsqueda de alumnos para inscribir.
// Los contratos salen del backend (routers/inscripciones.py, schemas/inscripcion.py y routers/alumnos.py).
import type { Pagina } from '../types.ts'
import { api } from './cliente.ts'

// Un alumno inscrito en el grupo (InscritoSalida). calificacion y desempenio son null si aún no se evalúa.
export interface Inscrito {
  nocontrol: string
  alumno: string // "López García Ana": apellidos y nombre, ya armado por el servidor
  carrera: string
  activo: boolean // false si el alumno se dio de baja después de inscribirse
  calificacion: number | null
  desempenio: string | null // lo calcula el servidor (RN-05); el cliente nunca lo manda
}

// Lo que se necesita de un alumno en el buscador (parte de AlumnoSalida)
export interface AlumnoEncontrado {
  nocontrol: string
  nombre: string
  apaterno: string
  amaterno: string | null
  carrera: string
  activo: boolean
}

export const TAMANO_BUSQUEDA = 10 // RN-11

function rutaGrupo(idgrupo: string): string {
  return `/api/grupos/${encodeURIComponent(idgrupo)}`
}

// GET /api/grupos/{id}/inscritos
export function listarInscritos(idgrupo: string): Promise<Inscrito[]> {
  return api.get<Inscrito[]>(`${rutaGrupo(idgrupo)}/inscritos`)
}

// POST /api/grupos/{id}/inscripciones (201). 409 si ya está inscrito o está de baja (RN-04).
export function inscribirAlumno(idgrupo: string, nocontrol: string): Promise<Inscrito> {
  return api.post<Inscrito>(`${rutaGrupo(idgrupo)}/inscripciones`, { nocontrol })
}

// PUT /api/grupos/{id}/inscripciones/{nocontrol}. Solo se manda la calificación:
// el servidor calcula el desempeño y lo regresa en la respuesta.
export function evaluarAlumno(idgrupo: string, nocontrol: string, calificacion: number): Promise<Inscrito> {
  return api.put<Inscrito>(`${rutaGrupo(idgrupo)}/inscripciones/${encodeURIComponent(nocontrol)}`, { calificacion })
}

// DELETE /api/grupos/{id}/inscripciones/{nocontrol} (204).
// Si el alumno ya tiene calificación el servidor responde 409 hasta que se mande ?confirmar=true.
export function quitarInscripcion(idgrupo: string, nocontrol: string, confirmar: boolean): Promise<void> {
  const parametro = confirmar ? '?confirmar=true' : ''
  return api.delete<void>(`${rutaGrupo(idgrupo)}/inscripciones/${encodeURIComponent(nocontrol)}${parametro}`)
}

// GET /api/alumnos?q=&page=&size=. Por defecto el servidor solo devuelve alumnos activos.
export function buscarAlumnos(texto: string, pagina: number): Promise<Pagina<AlumnoEncontrado>> {
  const parametros = new URLSearchParams({ q: texto, page: String(pagina), size: String(TAMANO_BUSQUEDA) })
  return api.get<Pagina<AlumnoEncontrado>>(`/api/alumnos?${parametros.toString()}`)
}
