// Datos y reglas de los alumnos que usan la lista, el formulario y el historial.
// Las reglas del formulario son las mismas que revisa el backend (schemas/alumno.py);
// aquí dan respuesta inmediata, pero el servidor siempre las vuelve a validar.
import type { Alumno, AlumnoEntrada, HistorialItem } from '../types.ts'
import { nombreSemestre } from './grupos.ts'

export const SEXOS = [
  { valor: 'M', etiqueta: 'Masculino' },
  { valor: 'F', etiqueta: 'Femenino' },
]

// Apellidos primero, como en las listas escolares: "López García, Ana"
export function nombreCompleto(a: Pick<Alumno, 'nombre' | 'apaterno' | 'amaterno'>): string {
  const apellidos = [a.apaterno, a.amaterno].filter(Boolean).join(' ')
  return `${apellidos}, ${a.nombre}`
}

// El historial trae el semestre en tres campos; se arma "Enero-Junio 2026" con el mismo helper de grupos
export function semestreDelHistorial(h: HistorialItem): string {
  return nombreSemestre({ idsemestre: 0, anio: h.semestre_anio, mesinicio: h.semestre_mesinicio, mestermino: h.semestre_mestermino })
}

export function nombreSexo(sexo: string): string {
  return SEXOS.find((s) => s.valor === sexo)?.etiqueta ?? sexo
}

// --- Formulario ---

// Lo capturado en el formulario. Todo es texto porque así lo entregan los campos.
export interface DatosAlumno {
  nocontrol: string
  nombre: string
  apaterno: string
  amaterno: string
  sexo: string
  carrera: string
  campus: string
}

export type ErroresAlumno = Partial<Record<keyof DatosAlumno, string>>

export const ALUMNO_VACIO: DatosAlumno = {
  nocontrol: '',
  nombre: '',
  apaterno: '',
  amaterno: '',
  sexo: '',
  carrera: '',
  campus: '',
}

// Quita espacios de los lados y pasa a mayúsculas: "b19110001 " y "B19110001" son el mismo número
export function normalizarNocontrol(valor: string): string {
  return valor.trim()
}

// El número de control tiene exactamente 8 dígitos y, de momento, no puede ser mayor a este valor (RN-01)
export const NOCONTROL_MAXIMO = 26999999

// Revisa un texto obligatorio con largo máximo; devuelve el mensaje o '' si está bien
function validarTexto(valor: string, nombre: string, maximo: number): string {
  const texto = valor.trim()
  if (!texto) return `Escribe ${nombre}.`
  if (texto.length > maximo) return `Máximo ${maximo} caracteres.`
  return ''
}

// Devuelve un mensaje por cada campo con problema ({} si todo está bien).
// Al editar no se revisa el número de control porque no se puede cambiar.
export function validarAlumno(datos: DatosAlumno, editando: boolean): ErroresAlumno {
  const errores: ErroresAlumno = {}

  if (!editando) {
    const nocontrol = normalizarNocontrol(datos.nocontrol)
    if (!nocontrol) {
      errores.nocontrol = 'Escribe el número de control.'
    } else if (!/^\d{8}$/.test(nocontrol)) {
      errores.nocontrol = 'Debe tener exactamente 8 dígitos, solo números.'
    } else if (Number(nocontrol) > NOCONTROL_MAXIMO) {
      errores.nocontrol = `No puede ser mayor a ${NOCONTROL_MAXIMO}.`
    }
  }

  const nombre = validarTexto(datos.nombre, 'el nombre o los nombres', 60)
  if (nombre) errores.nombre = nombre
  const apaterno = validarTexto(datos.apaterno, 'el apellido paterno', 60)
  if (apaterno) errores.apaterno = apaterno

  // El apellido materno es opcional: solo se revisa el largo
  if (datos.amaterno.trim().length > 60) errores.amaterno = 'Máximo 60 caracteres.'

  if (datos.sexo !== 'M' && datos.sexo !== 'F') errores.sexo = 'Elige el sexo.'

  // La carrera se elige de una lista; el servidor también comprueba que sea una de las oficiales
  if (!datos.carrera.trim()) errores.carrera = 'Elige la carrera.'
  const campus = validarTexto(datos.campus, 'el campus', 40)
  if (campus) errores.campus = campus

  return errores
}

// Convierte lo capturado en lo que espera la API (textos limpios; sin amaterno si está en blanco)
export function datosParaEnviar(datos: DatosAlumno): AlumnoEntrada {
  const amaterno = datos.amaterno.trim()
  return {
    nombre: datos.nombre.trim(),
    apaterno: datos.apaterno.trim(),
    ...(amaterno ? { amaterno } : {}),
    sexo: datos.sexo === 'F' ? 'F' : 'M', // validarAlumno ya aseguró que es M o F
    carrera: datos.carrera.trim(),
    campus: datos.campus.trim(),
  }
}
