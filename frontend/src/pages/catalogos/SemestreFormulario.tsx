import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { actualizarSemestre, crearSemestre } from '../../api/admin.ts'
import { ErrorApi } from '../../api/cliente.ts'
import CampoFormulario from '../../components/CampoFormulario.tsx'
import type { SemestreAdmin } from '../../tiposAdmin.ts'
import { OPCIONES_ANIO, OPCIONES_PERIODO, SEMESTRE_VACIO, textoError, validarSemestre } from '../../utils/admin.ts'
import type { DatosSemestre, ErroresSemestre } from '../../utils/admin.ts'

interface Props {
  semestre: SemestreAdmin | null // el semestre a editar (null = semestre nuevo)
  onGuardado: (mensaje: string) => void
  onCancelar: () => void
}

// Orden de los campos en pantalla: sirve para mandar el foco al primero que tenga error
const ORDEN_CAMPOS: (keyof DatosSemestre)[] = ['anio', 'periodo']

// Formulario de semestre (HU-03.3)
export default function SemestreFormulario({ semestre, onGuardado, onCancelar }: Props) {
  const [datos, setDatos] = useState<DatosSemestre>(() =>
    semestre
      ? { anio: String(semestre.anio), periodo: `${semestre.mesinicio}-${semestre.mestermino}` }
      : SEMESTRE_VACIO,
  )
  const [errores, setErrores] = useState<ErroresSemestre>({})
  const [aviso, setAviso] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Al abrirse el panel, el foco pasa al título
  const refTitulo = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    refTitulo.current?.focus()
  }, [])

  function cambiar(campo: keyof DatosSemestre, valor: string) {
    setDatos((anteriores) => ({ ...anteriores, [campo]: valor }))
    setErrores((anteriores) => ({ ...anteriores, [campo]: undefined }))
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setAviso('')

    const nuevos = validarSemestre(datos)
    setErrores(nuevos)
    const primerError = ORDEN_CAMPOS.find((campo) => nuevos[campo])
    if (primerError) {
      document.getElementById(`semestre-${primerError}`)?.focus()
      return
    }

    // El periodo "1-6" se separa en mes de inicio y mes de término; la API espera números
    const [mesinicio, mestermino] = datos.periodo.split('-').map(Number)
    const cuerpo = { anio: Number(datos.anio), mesinicio, mestermino }

    setEnviando(true)
    try {
      if (semestre) {
        await actualizarSemestre(semestre.idsemestre, cuerpo)
        onGuardado('Semestre actualizado.')
      } else {
        await crearSemestre(cuerpo)
        onGuardado('Semestre creado.')
      }
    } catch (e) {
      if (e instanceof ErrorApi && e.status === 422) {
        const delServidor: ErroresSemestre = {}
        for (const [campo, mensaje] of Object.entries(e.campos)) {
          if (campo === 'anio') delServidor.anio = mensaje
          else delServidor.periodo = mensaje // mesinicio, mestermino o el periodo completo
        }
        setErrores(delServidor)
      }
      // 409 (mismo año y mes de inicio), 403, 404, sin conexión...: el mensaje del servidor va en el aviso
      setAviso(textoError(e))
      setEnviando(false)
    }
  }

  return (
    <section className="tarjeta panel-formulario" aria-labelledby="semestre-titulo">
      <h3 id="semestre-titulo" ref={refTitulo} tabIndex={-1}>
        {semestre ? 'Editar semestre' : 'Nuevo semestre'}
      </h3>

      <form className="formulario formulario-ancho" onSubmit={enviar} noValidate>
        <CampoFormulario
          id="semestre-anio"
          etiqueta="Año"
          tipo="select"
          valor={datos.anio}
          onCambio={(v) => cambiar('anio', v)}
          opciones={OPCIONES_ANIO}
          ayuda="De 2000 a 2027."
          error={errores.anio}
        />
        <CampoFormulario
          id="semestre-periodo"
          etiqueta="Periodo"
          tipo="select"
          valor={datos.periodo}
          onCambio={(v) => cambiar('periodo', v)}
          opciones={OPCIONES_PERIODO}
          error={errores.periodo}
        />

        {aviso && (
          <div role="alert" className="alerta alerta-error ancho-completo">
            <p>{aviso}</p>
          </div>
        )}

        <div className="acciones ancho-completo">
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar semestre'}
          </button>
          <button type="button" className="boton boton-secundario" onClick={onCancelar} disabled={enviando}>
            Cancelar
          </button>
        </div>
      </form>
    </section>
  )
}
