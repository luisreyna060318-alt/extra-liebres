import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { actualizarPromotor, crearPromotor } from '../../api/admin.ts'
import { ErrorApi } from '../../api/cliente.ts'
import CampoFormulario from '../../components/CampoFormulario.tsx'
import type { PromotorAdmin } from '../../tiposAdmin.ts'
import { PROMOTOR_VACIO, normalizarRfc, textoError, validarPromotor } from '../../utils/admin.ts'
import type { DatosPromotor, ErroresPromotor } from '../../utils/admin.ts'

interface Props {
  promotor: PromotorAdmin | null // el promotor a editar (null = promotor nuevo)
  onGuardado: (mensaje: string) => void
  onCancelar: () => void
}

// Orden de los campos en pantalla: sirve para mandar el foco al primero que tenga error
const ORDEN_CAMPOS: (keyof DatosPromotor)[] = ['rfc', 'nombre', 'apaterno', 'amaterno']

// Formulario de promotor (HU-03.1). Al crear pide el RFC; al editar el RFC se muestra pero no se cambia.
export default function PromotorFormulario({ promotor, onGuardado, onCancelar }: Props) {
  const [datos, setDatos] = useState<DatosPromotor>(() =>
    promotor ? { rfc: promotor.rfc, nombre: promotor.nombre, apaterno: promotor.apaterno, amaterno: promotor.amaterno ?? '' } : PROMOTOR_VACIO,
  )
  const [errores, setErrores] = useState<ErroresPromotor>({})
  const [aviso, setAviso] = useState('') // error del servidor que no corresponde a un solo campo
  const [enviando, setEnviando] = useState(false)

  // Al abrirse el panel, el foco pasa al título para que se note que apareció el formulario
  const refTitulo = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    refTitulo.current?.focus()
  }, [])

  // Cambia un campo y borra su error (la persona ya lo está corrigiendo)
  function cambiar(campo: keyof DatosPromotor, valor: string) {
    setDatos((anteriores) => ({ ...anteriores, [campo]: valor }))
    setErrores((anteriores) => ({ ...anteriores, [campo]: undefined }))
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setAviso('')

    // 1) Validar en el cliente. Lo capturado no se borra aunque haya errores.
    const nuevos = validarPromotor(datos, !promotor)
    setErrores(nuevos)
    const primerError = ORDEN_CAMPOS.find((campo) => nuevos[campo])
    if (primerError) {
      document.getElementById(`promotor-${primerError}`)?.focus()
      return
    }

    // 2) Mandar a la API. El apellido materno vacío viaja como null (así lo espera el servidor).
    const nombre = datos.nombre.trim()
    const apaterno = datos.apaterno.trim()
    const amaterno = datos.amaterno.trim() || null

    setEnviando(true)
    try {
      if (promotor) {
        await actualizarPromotor(promotor.rfc, { nombre, apaterno, amaterno })
        onGuardado('Promotor actualizado.')
      } else {
        await crearPromotor({ rfc: normalizarRfc(datos.rfc), nombre, apaterno, amaterno })
        onGuardado('Promotor creado.')
      }
    } catch (e) {
      if (e instanceof ErrorApi && e.status === 422) {
        // El servidor rechazó datos que el cliente dejó pasar: se marca cada campo
        const delServidor: ErroresPromotor = {}
        for (const [campo, mensaje] of Object.entries(e.campos)) {
          if (campo in PROMOTOR_VACIO) delServidor[campo as keyof DatosPromotor] = mensaje
        }
        setErrores(delServidor)
      }
      // 409 (RFC repetido), 403, 404, sin conexión...: el mensaje del servidor va en el aviso
      setAviso(textoError(e))
      setEnviando(false)
    }
  }

  return (
    <section className="tarjeta panel-formulario" aria-labelledby="promotor-titulo">
      <h3 id="promotor-titulo" ref={refTitulo} tabIndex={-1}>
        {promotor ? 'Editar promotor' : 'Nuevo promotor'}
      </h3>

      <form className="formulario formulario-ancho" onSubmit={enviar} noValidate>
        {promotor ? (
          <p className="ancho-completo">
            <strong>RFC:</strong> {promotor.rfc} <span className="campo-ayuda">(no se puede cambiar)</span>
          </p>
        ) : (
          <CampoFormulario
            id="promotor-rfc"
            etiqueta="RFC"
            valor={datos.rfc}
            onCambio={(v) => cambiar('rfc', v)}
            maxLength={13}
            ayuda="12 o 13 caracteres, por ejemplo RUSP800101AB1. Se guarda en mayúsculas."
            error={errores.rfc}
          />
        )}

        <CampoFormulario
          id="promotor-nombre"
          etiqueta="Nombre"
          valor={datos.nombre}
          onCambio={(v) => cambiar('nombre', v)}
          maxLength={60}
          error={errores.nombre}
        />
        <CampoFormulario
          id="promotor-apaterno"
          etiqueta="Apellido paterno"
          valor={datos.apaterno}
          onCambio={(v) => cambiar('apaterno', v)}
          maxLength={60}
          error={errores.apaterno}
        />
        <CampoFormulario
          id="promotor-amaterno"
          etiqueta="Apellido materno (opcional)"
          valor={datos.amaterno}
          onCambio={(v) => cambiar('amaterno', v)}
          maxLength={60}
          error={errores.amaterno}
        />

        {aviso && (
          <div role="alert" className="alerta alerta-error ancho-completo">
            <p>{aviso}</p>
          </div>
        )}

        <div className="acciones ancho-completo">
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar promotor'}
          </button>
          <button type="button" className="boton boton-secundario" onClick={onCancelar} disabled={enviando}>
            Cancelar
          </button>
        </div>
      </form>
    </section>
  )
}
