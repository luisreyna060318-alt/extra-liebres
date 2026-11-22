import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorApi } from '../api/cliente.ts'
import { evaluarAlumno, quitarInscripcion } from '../api/inscripciones.ts'
import type { Inscrito } from '../api/inscripciones.ts'
import { SIN_CALIFICAR, validarCalificacion } from '../utils/inscripciones.ts'

interface Props {
  idgrupo: string
  inscrito: Inscrito
  onQuitado: (mensaje: string) => void // la pantalla vuelve a cargar la lista y muestra el mensaje
}

// Un renglón de la tabla de inscritos: captura de la calificación (HU-05.2) y botón para quitarlo (HU-05.3).
// Cada renglón guarda su propio estado, así guardar uno no recarga ni mueve a los demás.
export default function FilaInscrito({ idgrupo, inscrito, onQuitado }: Props) {
  // "actual" se reemplaza con lo que regresa el servidor después de guardar (trae el desempeño calculado)
  const [actual, setActual] = useState<Inscrito>(inscrito)
  const [valor, setValor] = useState(inscrito.calificacion === null ? '' : String(inscrito.calificacion))
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [pidiendoConfirmacion, setPidiendoConfirmacion] = useState(false)
  const [quitando, setQuitando] = useState(false)

  const botonQuitar = useRef<HTMLButtonElement>(null)
  const botonConfirmar = useRef<HTMLButtonElement>(null)
  const regresarFoco = useRef(false) // true al cancelar: el foco vuelve al botón "Quitar"

  // Cuando aparece la pregunta, el foco va al botón de confirmar para que el teclado y el lector la encuentren.
  // Al cancelar, el botón "Quitar" vuelve a existir hasta el siguiente render; por eso se enfoca aquí y no en cancelar().
  useEffect(() => {
    if (pidiendoConfirmacion) {
      botonConfirmar.current?.focus()
    } else if (regresarFoco.current) {
      regresarFoco.current = false
      botonQuitar.current?.focus()
    }
  }, [pidiendoConfirmacion])

  // Ids para unir la etiqueta y el mensaje de error con su campo
  const idCampo = `calificacion-${actual.nocontrol}`
  const idError = `${idCampo}-error`

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setMensaje('')

    // 1) Validar en el cliente (entero de 0 a 100)
    const problema = validarCalificacion(valor)
    setError(problema)
    if (problema) {
      document.getElementById(idCampo)?.focus()
      return
    }

    // 2) Mandar SOLO la calificación. El desempeño lo calcula el servidor y llega en la respuesta.
    setGuardando(true)
    try {
      const respuesta = await evaluarAlumno(idgrupo, actual.nocontrol, Number(valor.trim()))
      setActual(respuesta)
      setValor(String(respuesta.calificacion))
      setMensaje(`Guardado: ${respuesta.desempenio}.`)
    } catch (e) {
      // 422 = el servidor no aceptó el dato; se muestra su mensaje junto al campo
      if (e instanceof ErrorApi && e.status === 422) setError(e.campos.calificacion ?? e.message)
      else setError(e instanceof Error ? e.message : 'No se pudo guardar la calificación.')
      document.getElementById(idCampo)?.focus()
    } finally {
      setGuardando(false)
    }
  }

  // Primero se intenta sin confirmar. Si ya tiene calificación, el servidor responde 409 y se pregunta en pantalla.
  async function quitar(confirmar: boolean) {
    setMensaje('')
    setQuitando(true)
    try {
      await quitarInscripcion(idgrupo, actual.nocontrol, confirmar)
      onQuitado(`Se quitó a ${actual.alumno} del grupo.`)
    } catch (e) {
      if (e instanceof ErrorApi && e.status === 409 && !confirmar) {
        setPidiendoConfirmacion(true)
      } else {
        setPidiendoConfirmacion(false)
        setMensaje(e instanceof Error ? e.message : 'No se pudo quitar al alumno.')
      }
      setQuitando(false)
    }
  }

  function cancelar() {
    regresarFoco.current = true
    setPidiendoConfirmacion(false)
  }

  return (
    <tr>
      <td data-etiqueta="No. de control">{actual.nocontrol}</td>
      <td data-etiqueta="Alumno">
        {actual.alumno}
        {!actual.activo && <span className="etiqueta-baja"> (de baja)</span>}
      </td>
      <td data-etiqueta="Carrera">{actual.carrera}</td>
      <td data-etiqueta="Calificación">
        <form className="form-calificacion" onSubmit={guardar} noValidate>
          <label htmlFor={idCampo} className="solo-lectores">
            Calificación de {actual.alumno}
          </label>
          <input
            id={idCampo}
            className="campo-calificacion"
            type="text"
            inputMode="numeric"
            maxLength={3}
            value={valor}
            placeholder="0 a 100"
            onChange={(e) => {
              setValor(e.target.value)
              setError('')
            }}
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? idError : undefined}
          />
          <button type="submit" className="boton boton-chico" disabled={guardando}>
            {guardando ? 'Guardando…' : 'Guardar'}
            <span className="solo-lectores"> calificación de {actual.alumno}</span>
          </button>
          {error && (
            <p id={idError} className="campo-error">
              {error}
            </p>
          )}
        </form>
      </td>
      <td data-etiqueta="Desempeño">
        {actual.desempenio ?? SIN_CALIFICAR}
        {/* Región que el lector de pantalla anuncia al guardar o si algo falla */}
        <span role="status" className="mensaje-fila">
          {mensaje}
        </span>
      </td>
      <td data-etiqueta="Acciones">
        {pidiendoConfirmacion ? (
          <div className="confirmacion" role="alert">
            <p>
              {actual.alumno} ya tiene calificación ({actual.calificacion}). Si se quita del grupo, esa calificación se
              pierde. ¿Quitar de todos modos?
            </p>
            <div className="acciones">
              <button
                type="button"
                ref={botonConfirmar}
                className="boton boton-peligro boton-chico"
                disabled={quitando}
                onClick={() => quitar(true)}
              >
                {quitando ? 'Quitando…' : 'Sí, quitar del grupo'}
              </button>
              <button type="button" className="boton boton-secundario boton-chico" onClick={cancelar}>
                Cancelar
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            ref={botonQuitar}
            className="boton boton-secundario boton-chico"
            disabled={quitando}
            onClick={() => quitar(false)}
          >
            {quitando ? 'Quitando…' : 'Quitar'}
            <span className="solo-lectores"> a {actual.alumno} del grupo</span>
          </button>
        )}
      </td>
    </tr>
  )
}
