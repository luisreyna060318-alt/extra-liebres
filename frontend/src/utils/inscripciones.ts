// Reglas de la evaluación que se revisan en el cliente para dar respuesta inmediata.
// El servidor las vuelve a validar siempre (schemas/inscripcion.py responde 422 si no se cumplen).

// RN-05: la calificación es un número entero de 0 a 100. Devuelve el mensaje de error o '' si está bien.
export function validarCalificacion(texto: string): string {
  const valor = texto.trim()
  if (!valor) return 'Escribe la calificación.'
  // Solo dígitos: así se rechazan "94.5", "-3" o "9a"
  if (!/^\d+$/.test(valor)) return 'La calificación debe ser un número entero, sin decimales.'
  const numero = Number(valor)
  if (numero > 100) return 'La calificación debe estar entre 0 y 100.'
  return ''
}

// Lo que se muestra cuando el alumno aún no tiene calificación
export const SIN_CALIFICAR = 'Sin calificar'

// "López García Ana": mismo orden que usa el servidor en las listas
export function nombreCompleto(a: { nombre: string; apaterno: string; amaterno: string | null }): string {
  return [a.apaterno, a.amaterno, a.nombre].filter(Boolean).join(' ')
}
