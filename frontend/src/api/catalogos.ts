// Llamadas a los catálogos. OJO: estos endpoints son del catálogo de Luis (feature/backend-catalogos)
// y todavía no existen en main; se consumen según docs/propuesta-v2.md §7.
// Todas las llamadas viven aquí para cambiar un solo archivo si el contrato cambia.
import type { Actividad, Pagina, Promotor, Semestre } from '../types.ts'
import { api } from './cliente.ts'

// El listado puede venir como arreglo o como Pagina { items }. Se aceptan los dos.
// size=50 es el máximo de la paginación y alcanza para los catálogos (≈10 promotores, 8 actividades, 6 semestres).
async function pedirLista<T>(ruta: string): Promise<T[]> {
  const respuesta = await api.get<T[] | Pagina<T>>(`${ruta}?size=50`)
  return Array.isArray(respuesta) ? respuesta : respuesta.items
}

export interface Catalogos {
  actividades: Actividad[]
  promotores: Promotor[]
  semestres: Semestre[]
}

// Pide los tres catálogos juntos: si uno falla, la pantalla muestra un solo error con "Reintentar"
export async function cargarCatalogos(): Promise<Catalogos> {
  try {
    const [actividades, promotores, semestres] = await Promise.all([
      pedirLista<Actividad>('/api/extraescolares'),
      pedirLista<Promotor>('/api/promotores'),
      pedirLista<Semestre>('/api/semestres'),
    ])
    return { actividades, promotores, semestres }
  } catch (e) {
    // El mensaje original puede venir en inglés ("Not Found"): se explica en español qué falló
    const motivo = e instanceof Error ? ` (${e.message})` : ''
    throw new Error(`No se pudieron cargar las actividades, los promotores y los semestres${motivo}.`)
  }
}
