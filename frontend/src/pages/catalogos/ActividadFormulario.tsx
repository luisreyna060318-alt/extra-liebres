import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { actualizarActividad, crearActividad } from '../../api/admin.ts'
import { ErrorApi } from '../../api/cliente.ts'
import CampoFormulario from '../../components/CampoFormulario.tsx'
import type { ActividadAdmin } from '../../tiposAdmin.ts'
import type { TipoActividad } from '../../types.ts'
import { ACTIVIDAD_VACIA, TIPOS_ACTIVIDAD, textoError, validarActividad } from '../../utils/admin.ts'
import type { DatosActividad, ErroresActividad } from '../../utils/admin.ts'

interface Props {
  actividad: ActividadAdmin | null // la actividad a editar (null = actividad nueva)
  onGuardado: (mensaje: string) => void
  onCancelar: () => void
}

// Orden de los campos en pantalla: sirve para mandar el foco al primero que tenga error
const ORDEN_CAMPOS: (keyof ErroresActividad)[] = ['nombreextra', 'tipo']

// Formulario de actividad extraescolar (HU-03.2)
export default function ActividadFormulario({ actividad, onGuardado, onCancelar }: Props) {
  const [datos, setDatos] = useState<DatosActividad>(() =>
    actividad ? { nombreextra: actividad.nombreextra, tipo: actividad.tipo, alAireLibre: actividad.al_aire_libre } : ACTIVIDAD_VACIA,
  )
  const [errores, setErrores] = useState<ErroresActividad>({})
  const [aviso, setAviso] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Al abrirse el panel, el foco pasa al título
  const refTitulo = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    refTitulo.current?.focus()
  }, [])

  function cambiar(campo: 'nombreextra' | 'tipo', valor: string) {
    setDatos((anteriores) => ({ ...anteriores, [campo]: valor }))
    setErrores((anteriores) => ({ ...anteriores, [campo]: undefined }))
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setAviso('')

    const nuevos = validarActividad(datos)
    setErrores(nuevos)
    const primerError = ORDEN_CAMPOS.find((campo) => nuevos[campo])
    if (primerError) {
      document.getElementById(`actividad-${primerError}`)?.focus()
      return
    }

    // En la API el campo se llama al_aire_libre
    const cuerpo = {
      nombreextra: datos.nombreextra.trim(),
      tipo: datos.tipo as TipoActividad, // ya se validó que sea uno de los tres
      al_aire_libre: datos.alAireLibre,
    }

    setEnviando(true)
    try {
      if (actividad) {
        await actualizarActividad(actividad.idextraescolar, cuerpo)
        onGuardado('Actividad actualizada.')
      } else {
        await crearActividad(cuerpo)
        onGuardado('Actividad creada.')
      }
    } catch (e) {
      if (e instanceof ErrorApi && e.status === 422) {
        const delServidor: ErroresActividad = {}
        for (const [campo, mensaje] of Object.entries(e.campos)) {
          if (campo === 'nombreextra' || campo === 'tipo') delServidor[campo] = mensaje
        }
        setErrores(delServidor)
      }
      // 409 (nombre repetido), 403, 404, sin conexión...: el mensaje del servidor va en el aviso
      setAviso(textoError(e))
      setEnviando(false)
    }
  }

  return (
    <section className="tarjeta panel-formulario" aria-labelledby="actividad-titulo">
      <h3 id="actividad-titulo" ref={refTitulo} tabIndex={-1}>
        {actividad ? 'Editar actividad' : 'Nueva actividad'}
      </h3>

      <form className="formulario formulario-ancho" onSubmit={enviar} noValidate>
        <CampoFormulario
          id="actividad-nombreextra"
          etiqueta="Nombre de la actividad"
          valor={datos.nombreextra}
          onCambio={(v) => cambiar('nombreextra', v)}
          maxLength={80}
          error={errores.nombreextra}
        />
        <CampoFormulario
          id="actividad-tipo"
          etiqueta="Tipo"
          tipo="select"
          valor={datos.tipo}
          onCambio={(v) => cambiar('tipo', v)}
          opciones={TIPOS_ACTIVIDAD.map((t) => ({ valor: t.valor, etiqueta: t.etiqueta }))}
          error={errores.tipo}
        />

        {/* Casilla: si está marcada, el formulario de grupos muestra el pronóstico del clima */}
        <div className="campo-casilla ancho-completo">
          <input
            id="actividad-aire"
            type="checkbox"
            checked={datos.alAireLibre}
            onChange={(e) => setDatos((anteriores) => ({ ...anteriores, alAireLibre: e.target.checked }))}
            aria-describedby="actividad-aire-ayuda"
          />
          <div>
            <label htmlFor="actividad-aire">Se realiza al aire libre</label>
            <p id="actividad-aire-ayuda" className="campo-ayuda">
              Si la marcas, al crear un grupo de esta actividad se mostrará el pronóstico del clima.
            </p>
          </div>
        </div>

        {aviso && (
          <div role="alert" className="alerta alerta-error ancho-completo">
            <p>{aviso}</p>
          </div>
        )}

        <div className="acciones ancho-completo">
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar actividad'}
          </button>
          <button type="button" className="boton boton-secundario" onClick={onCancelar} disabled={enviando}>
            Cancelar
          </button>
        </div>
      </form>
    </section>
  )
}
