// Datos, textos y validaciones de las pantallas de administración (catálogos y usuarios).
// Las reglas son las mismas que revisa el backend (schemas/promotor.py, extraescolar.py y semestre.py);
// aquí dan respuesta inmediata, pero el servidor siempre las vuelve a validar.
import type { Rol, TipoActividad } from '../types.ts'

// --- Textos para mostrar ---

export const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
] // prettier-ignore

// Opciones del select de meses: el valor es el número (1 a 12) que espera la API
export const OPCIONES_MES = MESES.map((nombre, i) => ({ valor: String(i + 1), etiqueta: nombre }))

export function nombreMes(numero: number): string {
  return MESES[numero - 1] ?? String(numero)
}

// El tipo se guarda sin acentos ("civica"); la etiqueta es la que ve la persona
export const TIPOS_ACTIVIDAD: { valor: TipoActividad; etiqueta: string }[] = [
  { valor: 'deportiva', etiqueta: 'Deportiva' },
  { valor: 'cultural', etiqueta: 'Cultural' },
  { valor: 'civica', etiqueta: 'Cívica' },
]

export function nombreTipo(tipo: string): string {
  return TIPOS_ACTIVIDAD.find((t) => t.valor === tipo)?.etiqueta ?? tipo
}

export const ROLES: { valor: Rol; etiqueta: string }[] = [
  { valor: 'administrador', etiqueta: 'Administrador' },
  { valor: 'capturista', etiqueta: 'Capturista' },
]

export function nombreRol(rol: string): string {
  return ROLES.find((r) => r.valor === rol)?.etiqueta ?? rol
}

// La API manda la fecha en formato ISO; se muestra como "21 de noviembre de 2026"
export function formatoFecha(fecha: string): string {
  const f = new Date(fecha)
  if (Number.isNaN(f.getTime())) return fecha
  return f.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })
}

// Mensaje para mostrar cuando una llamada a la API falla
export function textoError(e: unknown): string {
  return e instanceof Error ? e.message : 'Ocurrió un error inesperado.'
}

// --- Promotores ---

// Lo capturado en el formulario: todo es texto porque así lo entregan los campos
export interface DatosPromotor {
  rfc: string
  nombre: string
  apaterno: string
  amaterno: string
}

export type ErroresPromotor = Partial<Record<keyof DatosPromotor, string>>

export const PROMOTOR_VACIO: DatosPromotor = { rfc: '', nombre: '', apaterno: '', amaterno: '' }

// Igual que el servidor: sin espacios y en mayúsculas ("rusp800101ab1 " y "RUSP800101AB1" son el mismo RFC)
export function normalizarRfc(valor: string): string {
  return valor.trim().replace(/\s/g, '').toUpperCase()
}

// 3 o 4 letras + fecha (6 dígitos) + homoclave (3): 12 caracteres (moral) o 13 (física)
const FORMATO_RFC = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/

// Revisa un texto obligatorio con largo máximo. "articulo" completa la frase: "Escribe el nombre."
function validarTexto(valor: string, articulo: string, max: number): string {
  const texto = valor.trim()
  if (!texto) return `Escribe ${articulo}.`
  if (texto.length > max) return `${articulo.charAt(0).toUpperCase()}${articulo.slice(1)} no puede pasar de ${max} caracteres.`
  return ''
}

// pedirRfc es false al editar: el RFC es el identificador y no se puede cambiar
export function validarPromotor(datos: DatosPromotor, pedirRfc: boolean): ErroresPromotor {
  const errores: ErroresPromotor = {}

  if (pedirRfc) {
    const rfc = normalizarRfc(datos.rfc)
    if (!rfc) errores.rfc = 'Escribe el RFC.'
    else if (!FORMATO_RFC.test(rfc)) {
      errores.rfc = 'El RFC debe tener 12 o 13 caracteres con el formato oficial (ej. RUSP800101AB1).'
    }
  }

  const nombre = validarTexto(datos.nombre, 'el nombre', 60)
  if (nombre) errores.nombre = nombre
  const apaterno = validarTexto(datos.apaterno, 'el apellido paterno', 60)
  if (apaterno) errores.apaterno = apaterno

  // El apellido materno es opcional: solo se revisa el largo
  if (datos.amaterno.trim().length > 60) errores.amaterno = 'El apellido materno no puede pasar de 60 caracteres.'

  return errores
}

// --- Actividades ---

export interface DatosActividad {
  nombreextra: string
  tipo: string // '' mientras no se elija
  alAireLibre: boolean
}

export type ErroresActividad = Partial<Record<'nombreextra' | 'tipo', string>>

export const ACTIVIDAD_VACIA: DatosActividad = { nombreextra: '', tipo: '', alAireLibre: false }

export function validarActividad(datos: DatosActividad): ErroresActividad {
  const errores: ErroresActividad = {}

  const nombre = validarTexto(datos.nombreextra, 'el nombre de la actividad', 80)
  if (nombre) errores.nombreextra = nombre
  if (!TIPOS_ACTIVIDAD.some((t) => t.valor === datos.tipo)) errores.tipo = 'Elige el tipo de actividad.'

  return errores
}

// --- Semestres ---

export interface DatosSemestre {
  anio: string
  mesinicio: string
  mestermino: string
}

export type ErroresSemestre = Partial<Record<keyof DatosSemestre, string>>

export const SEMESTRE_VACIO: DatosSemestre = { anio: '', mesinicio: '', mestermino: '' }

export function validarSemestre(datos: DatosSemestre): ErroresSemestre {
  const errores: ErroresSemestre = {}

  const anio = datos.anio.trim()
  if (!anio) errores.anio = 'Escribe el año.'
  else if (!/^\d{4}$/.test(anio) || Number(anio) < 2000 || Number(anio) > 2100) {
    errores.anio = 'El año debe ser un número entre 2000 y 2100.'
  }
  if (!datos.mesinicio) errores.mesinicio = 'Elige el mes de inicio.'
  if (!datos.mestermino) errores.mestermino = 'Elige el mes de término.'

  return errores
}
