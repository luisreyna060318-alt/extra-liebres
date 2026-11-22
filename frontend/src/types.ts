// Tipos compartidos. Reflejan lo que devuelve la API.

export type Rol = 'administrador' | 'capturista'

// GET /api/auth/me
export interface Usuario {
  id: number
  nombre: string
  correo: string
  rol: Rol
  activo: boolean
  creado_en: string
}

// --- Listados paginados (Pagina[T] del backend: schemas/comun.py) ---
export interface Pagina<T> {
  items: T[]
  total: number
  page: number
  size: number
}

// --- Catálogos (docs/propuesta-v2.md §6; los endpoints son del catálogo de Luis) ---
export type TipoActividad = 'deportiva' | 'cultural' | 'civica'

export interface Actividad {
  idextraescolar: number
  nombreextra: string
  tipo: TipoActividad
  al_aire_libre: boolean // si es true, el formulario de grupo muestra el pronóstico
  activo?: boolean
}

export interface Promotor {
  rfc: string
  nombre: string
  apaterno: string
  amaterno: string | null
  activo?: boolean
}

export interface Semestre {
  idsemestre: number
  mesinicio: number // 1 a 12
  mestermino: number
  anio: number
}

// --- Grupos (backend: schemas/grupo.py, GrupoSalida) ---
export interface Grupo {
  idgrupo: number
  idsemestre: number
  semestre: string // nombre ya armado, por ejemplo "Enero-Junio 2026"
  idextraescolar: number
  actividad: string
  tipo_actividad: TipoActividad
  rfcpromotor: string
  promotor: string
  dia: string // sin acentos: lunes ... sabado
  horainicio: string // "HH:MM:SS"
  horatermino: string
  aula: string // aula o instalación (el lugar del grupo)
  inscritos: number
}

// Lo que se manda al crear o editar (GrupoCrear / GrupoActualizar)
export interface GrupoEntrada {
  idsemestre: number
  idextraescolar: number
  rfcpromotor: string
  dia: string
  horainicio: string // "HH:MM"
  horatermino: string
  aula: string
}

// --- Clima (backend: schemas/clima.py). Si disponible es false, solo viene mensaje ---
export interface Clima {
  disponible: boolean
  mensaje?: string
  temperatura?: number
  prob_lluvia?: number
  aviso_lluvia?: boolean
}

// --- Alumnos (backend: schemas/alumno.py) ---
export type Sexo = 'M' | 'F'

export interface Alumno {
  nocontrol: string // texto, no número: puede empezar con ceros o con una letra
  nombre: string
  apaterno: string
  amaterno: string | null
  sexo: Sexo
  carrera: string
  campus: string
  activo: boolean // false = dado de baja (baja lógica, no se borra)
}

// Lo que se manda al editar (AlumnoActualizar). Al crear se agrega también nocontrol (AlumnoCrear).
export interface AlumnoEntrada {
  nombre: string
  apaterno: string
  amaterno?: string // si se omite, el alumno no tiene segundo apellido
  sexo: Sexo
  carrera: string
  campus: string
  activo?: boolean // true reactiva a un alumno dado de baja
}

// GET /api/alumnos/opciones: valores que ya existen, para las listas de sugerencias y los filtros
export interface OpcionesAlumno {
  carreras: string[]
  campus: string[]
}

// GET /api/alumnos/{nocontrol}/historial: una actividad que cursó el alumno
export interface HistorialItem {
  idgrupo: number
  actividad: string
  semestre_anio: number
  semestre_mesinicio: number
  semestre_mestermino: number
  promotor: string
  dia: string // sin acentos: lunes ... sabado
  horainicio: string // "HH:MM:SS"
  horatermino: string
  aula: string
  calificacion: number | null // null = todavía sin evaluar
  desempenio: string | null
}
