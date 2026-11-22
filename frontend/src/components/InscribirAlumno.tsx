import { useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorApi } from '../api/cliente.ts'
import { TAMANO_BUSQUEDA, buscarAlumnos, inscribirAlumno } from '../api/inscripciones.ts'
import type { AlumnoEncontrado } from '../api/inscripciones.ts'
import { useApi } from '../hooks/useApi.ts'
import { nombreCompleto } from '../utils/inscripciones.ts'
import CampoFormulario from './CampoFormulario.tsx'
import Estado from './Estado.tsx'

interface Props {
  idgrupo: string
  yaInscritos: Set<string> // números de control que ya están en el grupo (solo para avisar en la lista)
  onInscrito: () => void // la pantalla vuelve a cargar la tabla de inscritos
}

interface Aviso {
  tipo: 'exito' | 'error'
  texto: string
}

// Buscador de alumnos activos y botón para inscribirlos al grupo (HU-05.1)
export default function InscribirAlumno({ idgrupo, yaInscritos, onInscrito }: Props) {
  const [texto, setTexto] = useState('') // lo que se escribe en el campo
  const [buscado, setBuscado] = useState('') // lo que se mandó a buscar (cambia al enviar el formulario)
  const [pagina, setPagina] = useState(1)
  const [errorTexto, setErrorTexto] = useState('')
  const [aviso, setAviso] = useState<Aviso | null>(null)
  const [inscribiendo, setInscribiendo] = useState<string | null>(null) // nocontrol que se está inscribiendo

  // Solo se consulta cuando ya hay algo que buscar
  const resultados = useApi(() => (buscado ? buscarAlumnos(buscado, pagina) : Promise.resolve(null)), [buscado, pagina])

  function buscar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const limpio = texto.trim()
    if (!limpio) {
      setErrorTexto('Escribe un nombre, apellido o número de control.')
      document.getElementById('buscar-alumno')?.focus()
      return
    }
    setErrorTexto('')
    setAviso(null)
    setBuscado(limpio)
    setPagina(1)
  }

  async function inscribir(alumno: AlumnoEncontrado) {
    const nombre = nombreCompleto(alumno)
    setAviso(null)
    setInscribiendo(alumno.nocontrol)
    try {
      await inscribirAlumno(idgrupo, alumno.nocontrol)
      setAviso({ tipo: 'exito', texto: `Se inscribió a ${nombre} en el grupo.` })
      onInscrito()
    } catch (e) {
      // 409: ya inscrito o dado de baja (RN-04). Se muestra tal cual el mensaje del servidor.
      const motivo = e instanceof Error ? e.message : 'Ocurrió un error inesperado.'
      const titulo = e instanceof ErrorApi && e.status === 409 ? `No se puede inscribir a ${nombre}` : 'No se pudo inscribir'
      setAviso({ tipo: 'error', texto: `${titulo}: ${motivo}` })
    } finally {
      setInscribiendo(null)
    }
  }

  const total = resultados.datos?.total ?? 0
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_BUSQUEDA))

  return (
    <section className="tarjeta-seccion" aria-labelledby="titulo-inscribir">
      <h2 id="titulo-inscribir">Inscribir alumno</h2>

      <form className="buscador" onSubmit={buscar} noValidate role="search">
        <CampoFormulario
          id="buscar-alumno"
          etiqueta="Buscar alumno activo"
          valor={texto}
          onCambio={(v) => {
            setTexto(v)
            setErrorTexto('')
          }}
          ayuda="Nombre, apellidos o número de control."
          error={errorTexto}
          maxLength={60}
        />
        <button type="submit" className="boton">
          Buscar
        </button>
      </form>

      {/* El aviso vive fuera de la lista para que no desaparezca cuando la lista se recarga */}
      {aviso && (
        <p role={aviso.tipo === 'error' ? 'alert' : 'status'} className={`alerta alerta-${aviso.tipo}`}>
          {aviso.texto}
        </p>
      )}

      {buscado && (
        <Estado
          cargando={resultados.cargando}
          error={resultados.error}
          onReintentar={resultados.recargar}
          vacio={resultados.datos?.items.length === 0}
          textoVacio={`Ningún alumno activo coincide con “${buscado}”.`}
        >
          {resultados.datos && (
            <>
              <ul className="lista-resultados" aria-label={`Resultados para ${buscado}`}>
                {resultados.datos.items.map((a) => {
                  const nombre = nombreCompleto(a)
                  const yaEsta = yaInscritos.has(a.nocontrol)
                  return (
                    <li key={a.nocontrol} className="resultado">
                      <div>
                        <strong>{nombre}</strong>
                        <span className="campo-ayuda">
                          {' '}
                          {a.nocontrol} · {a.carrera}
                          {yaEsta && ' · ya está en el grupo'}
                        </span>
                      </div>
                      <button
                        type="button"
                        className="boton boton-chico"
                        disabled={inscribiendo !== null}
                        onClick={() => inscribir(a)}
                      >
                        {inscribiendo === a.nocontrol ? 'Inscribiendo…' : 'Inscribir'}
                        <span className="solo-lectores"> a {nombre}</span>
                      </button>
                    </li>
                  )
                })}
              </ul>

              {totalPaginas > 1 && (
                <nav className="paginacion" aria-label="Paginación de la búsqueda de alumnos">
                  <button type="button" className="boton boton-secundario" disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>
                    Anterior
                  </button>
                  <span>
                    Página {pagina} de {totalPaginas}
                  </span>
                  <button type="button" className="boton boton-secundario" disabled={pagina >= totalPaginas} onClick={() => setPagina(pagina + 1)}>
                    Siguiente
                  </button>
                </nav>
              )}
            </>
          )}
        </Estado>
      )}
    </section>
  )
}
