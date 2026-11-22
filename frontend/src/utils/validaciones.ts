// Validaciones en el cliente: dan respuesta inmediata, pero NO sustituyen a las del servidor.
// Cada función devuelve el mensaje de error, o '' si el valor es válido.
// Las reglas son las mismas que usa el backend (schemas/usuario.py).

export function validarNombre(valor: string): string {
  const nombre = valor.trim()
  if (!nombre) return 'Escribe tu nombre.'
  if (nombre.length < 2) return 'El nombre debe tener al menos 2 caracteres.'
  if (nombre.length > 100) return 'El nombre no puede pasar de 100 caracteres.'
  return ''
}

export function validarCorreo(valor: string): string {
  const correo = valor.trim()
  if (!correo) return 'Escribe tu correo.'
  if (correo.length > 120) return 'El correo no puede pasar de 120 caracteres.'
  // Revisión sencilla: algo@algo.algo, sin espacios
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) return 'Escribe un correo válido, por ejemplo ana@correo.com.'
  return ''
}

// Para crear cuenta: mínimo 8 caracteres, con letras y números (RN del backend)
export function validarPasswordNueva(valor: string): string {
  if (!valor) return 'Escribe una contraseña.'
  if (valor.length < 8) return 'La contraseña debe tener al menos 8 caracteres.'
  if (!/[A-Za-z]/.test(valor) || !/\d/.test(valor)) return 'La contraseña debe combinar letras y números.'
  return ''
}

// Para iniciar sesión solo se exige que no esté vacía (el servidor decide si es correcta)
export function validarPasswordLogin(valor: string): string {
  return valor ? '' : 'Escribe tu contraseña.'
}
