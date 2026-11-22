// Datos y reglas de los grupos que usan la lista y el formulario.
// Las reglas del formulario son las mismas que revisa el backend (schemas/grupo.py);
// aquí dan respuesta inmediata, pero el servidor siempre las vuelve a validar.
import type { Actividad, Promotor, Semestre } from '../types.ts'

// Los días se guardan sin acentos (así los espera la API); la etiqueta es la que ve la persona
export const DIAS = [
  { valor: 'lunes', etiqueta: 'Lunes' },
  { valor: 'martes', etiqueta: 'Martes' },
  { valor: 'miercoles', etiqueta: 'Miércoles' },
  { valor: 'jueves', etiqueta: 'Jueves' },
  { valor: 'viernes', etiqueta: 'Viernes' },
  { valor: 'sabado', etiqueta: 'Sábado' },
]

// Lugares de las actividades deportivas. Misma lista que INSTALACIONES en backend/app/core/constantes.py
export const INSTALACIONES = [
  'Cancha de fútbol',
  'Cancha de básquetbol',
  'Cancha de voleibol',
  'Gimnasio',
  'Pista de atletismo',
  'Alberca',
]

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
] // prettier-ignore

export function nombreSemestre(s: Semestre): string {
  return `${MESES[s.mesinicio - 1]}-${MESES[s.mestermino - 1]} ${s.anio}`
}

export function nombrePromotor(p: Promotor): string {
  return [p.nombre, p.apaterno, p.amaterno].filter(Boolean).join(' ')
}

export function nombreDia(valor: string): string {
  return DIAS.find((d) => d.valor === valor)?.etiqueta ?? valor
}

// La API manda "08:00:00"; los campos de hora y la tabla usan "08:00"
export function recortarHora(hora: string): string {
  return hora.slice(0, 5)
}

// --- Formulario ---

// Lo capturado en el formulario. Todo es texto porque así lo entregan los campos.
export interface DatosGrupo {
  idsemestre: string
  idextraescolar: string
  rfcpromotor: string
  dia: string
  horainicio: string
  horatermino: string
  lugar: string // se envía como "aula": instalación (deportiva) o aula escrita (cultural o cívica)
}

export type ErroresGrupo = Partial<Record<keyof DatosGrupo, string>>

export const GRUPO_VACIO: DatosGrupo = {
  idsemestre: '',
  idextraescolar: '',
  rfcpromotor: '',
  dia: '',
  horainicio: '',
  horatermino: '',
  lugar: '',
}

// Las deportivas piden una instalación de la lista; las demás, un aula escrita
export function esDeportiva(actividad: Actividad | undefined): boolean {
  return actividad?.tipo === 'deportiva'
}

// Devuelve un mensaje por cada campo con problema ({} si todo está bien)
export function validarGrupo(datos: DatosGrupo, actividad: Actividad | undefined): ErroresGrupo {
  const errores: ErroresGrupo = {}

  if (!datos.idsemestre) errores.idsemestre = 'Elige el semestre.'
  if (!datos.idextraescolar) errores.idextraescolar = 'Elige la actividad.'
  if (!datos.rfcpromotor) errores.rfcpromotor = 'Elige el promotor.'
  if (!datos.dia) errores.dia = 'Elige el día.'
  if (!datos.horainicio) errores.horainicio = 'Escribe la hora de inicio.'
  if (!datos.horatermino) errores.horatermino = 'Escribe la hora de término.'

  // Las horas "HH:MM" se pueden comparar como texto (regla RN-03: el fin debe ser posterior al inicio)
  if (datos.horainicio && datos.horatermino && datos.horatermino <= datos.horainicio) {
    errores.horatermino = 'La hora de término debe ser posterior a la de inicio.'
  }

  // El lugar depende de la actividad: sin actividad elegida todavía no se puede revisar
  if (actividad) {
    const lugar = datos.lugar.trim()
    if (esDeportiva(actividad)) {
      if (!lugar) errores.lugar = 'Elige el lugar.'
      else if (!INSTALACIONES.includes(lugar)) errores.lugar = 'Elige un lugar de la lista.'
    } else if (!lugar) {
      errores.lugar = 'Escribe el aula.'
    } else if (lugar.length > 60) {
      errores.lugar = 'El aula no puede pasar de 60 caracteres.'
    }
  }

  return errores
}
