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
  return valor.trim().toUpperCase()
}

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
    } else if (!/^[A-Z0-9]{7,10}$/.test(nocontrol)) {
      // Es texto, no número: puede empezar con ceros o con una letra (RN-01)
      errores.nocontrol = 'Debe tener de 7 a 10 letras o números, sin espacios.'
    }
  }

  const nombre = validarTexto(datos.nombre, 'el nombre', 60)
  if (nombre) errores.nombre = nombre
  const apaterno = validarTexto(datos.apaterno, 'el apellido paterno', 60)
  if (apaterno) errores.apaterno = apaterno

  // El apellido materno es opcional: solo se revisa el largo
  if (datos.amaterno.trim().length > 60) errores.amaterno = 'Máximo 60 caracteres.'

  if (datos.sexo !== 'M' && datos.sexo !== 'F') errores.sexo = 'Elige el sexo.'

  const carrera = validarTexto(datos.carrera, 'la carrera', 80)
  if (carrera) errores.carrera = carrera
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
