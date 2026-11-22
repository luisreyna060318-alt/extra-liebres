// Llamadas a /api/alumnos. Los contratos salen del backend (routers/alumnos.py y schemas/alumno.py).
import type { Alumno, AlumnoEntrada, HistorialItem, OpcionesAlumno, Pagina } from '../types.ts'
import { ErrorApi, api } from './cliente.ts'

// Filtros de la lista: texto vacío = sin filtro
export interface FiltrosAlumnos {
  q: string // búsqueda por nombre o número de control
  carrera: string
  campus: string
  estado: 'activos' | 'bajas' | 'todos'
}

export const TAMANO_PAGINA = 10 // RN-11

// GET /api/alumnos?q=&carrera=&campus=&estado=&page=&size=
export function listarAlumnos(filtros: FiltrosAlumnos, pagina: number): Promise<Pagina<Alumno>> {
  const parametros = new URLSearchParams({
    estado: filtros.estado,
    page: String(pagina),
    size: String(TAMANO_PAGINA),
  })
  // Solo se mandan los filtros de texto que tienen valor
  if (filtros.q) parametros.set('q', filtros.q)
  if (filtros.carrera) parametros.set('carrera', filtros.carrera)
  if (filtros.campus) parametros.set('campus', filtros.campus)
  return api.get<Pagina<Alumno>>(`/api/alumnos?${parametros.toString()}`)
}

// GET /api/alumnos/opciones: carreras y campus que ya existen
export function obtenerOpciones(): Promise<OpcionesAlumno> {
  return api.get<OpcionesAlumno>('/api/alumnos/opciones')
}

// Si el servidor dice 404 se cambia el mensaje por uno claro para la persona
function alumnoNoExiste(e: unknown): never {
  if (e instanceof ErrorApi && e.status === 404) throw new ErrorApi('El alumno no existe', 404)
  throw e
}

// GET /api/alumnos/{nocontrol}
export function obtenerAlumno(nocontrol: string): Promise<Alumno> {
  return api.get<Alumno>(`/api/alumnos/${encodeURIComponent(nocontrol)}`).catch(alumnoNoExiste)
}

// POST /api/alumnos (201). Puede responder 409 (número de control repetido) o 422.
export function crearAlumno(nocontrol: string, datos: AlumnoEntrada): Promise<Alumno> {
  return api.post<Alumno>('/api/alumnos', { nocontrol, ...datos })
}

// PUT /api/alumnos/{nocontrol}: con activo=true también reactiva al alumno
export function actualizarAlumno(nocontrol: string, datos: AlumnoEntrada): Promise<Alumno> {
  return api.put<Alumno>(`/api/alumnos/${encodeURIComponent(nocontrol)}`, datos)
}

// DELETE /api/alumnos/{nocontrol} (204): baja lógica, el alumno no se borra
export function darDeBajaAlumno(nocontrol: string): Promise<void> {
  return api.delete<void>(`/api/alumnos/${encodeURIComponent(nocontrol)}`)
}

// GET /api/alumnos/{nocontrol}/historial
export function obtenerHistorial(nocontrol: string): Promise<HistorialItem[]> {
  return api.get<HistorialItem[]>(`/api/alumnos/${encodeURIComponent(nocontrol)}/historial`).catch(alumnoNoExiste)
}
