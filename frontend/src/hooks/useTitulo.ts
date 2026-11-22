import { useEffect } from 'react'

// Cambia el título de la pestaña en cada pantalla (ayuda a la accesibilidad y a Lighthouse)
export function useTitulo(titulo: string) {
  useEffect(() => {
    document.title = `${titulo} · Extra-Liebres`
  }, [titulo])
}
