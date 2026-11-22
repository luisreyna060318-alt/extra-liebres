import { useCallback, useEffect, useState } from 'react'

// Llama a la API cuando se abre la pantalla y devuelve el estado de la petición:
//   const { datos, cargando, error, recargar } = useApi(() => api.get<Alumno[]>('/api/alumnos'))
// `dependencias` sirve para volver a pedir los datos cuando cambia algo (un filtro, la página...).
export function useApi<T>(funcion: () => Promise<T>, dependencias: unknown[] = []) {
  const [datos, setDatos] = useState<T | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [intento, setIntento] = useState(0) // subirlo fuerza una nueva petición

  useEffect(() => {
    let vigente = true // evita guardar una respuesta vieja si ya cambió algo o se cerró la pantalla
    setCargando(true)
    setError(null)

    funcion()
      .then((resultado) => {
        if (vigente) setDatos(resultado)
      })
      .catch((e: unknown) => {
        if (vigente) setError(e instanceof Error ? e.message : 'Ocurrió un error inesperado')
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
    // La función se vuelve a crear en cada render; por eso solo se vigilan las dependencias indicadas
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencias, intento])

  const recargar = useCallback(() => setIntento((n) => n + 1), [])

  return { datos, cargando, error, recargar }
}
