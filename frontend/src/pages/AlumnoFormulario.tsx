import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { actualizarAlumno, crearAlumno, obtenerAlumno, obtenerOpciones } from '../api/alumnos.ts'
import { ErrorApi } from '../api/cliente.ts'
import CampoFormulario from '../components/CampoFormulario.tsx'
import Estado from '../components/Estado.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import type { Alumno, OpcionesAlumno } from '../types.ts'
import { ALUMNO_VACIO, SEXOS, datosParaEnviar, normalizarNocontrol, validarAlumno } from '../utils/alumnos.ts'
import type { DatosAlumno, ErroresAlumno } from '../utils/alumnos.ts'

// Orden de los campos en pantalla: sirve para mandar el foco al primero que tenga error
const ORDEN_CAMPOS: (keyof DatosAlumno)[] = ['nocontrol', 'nombre', 'apaterno', 'amaterno', 'sexo', 'carrera', 'campus']

// --- Pantalla: carga el alumno (si se edita) y las opciones, y luego muestra el formulario ---
export default function AlumnoFormulario() {
  const { nocontrol } = useParams() // sin nocontrol = alumno nuevo; con nocontrol = editar
  useTitulo(nocontrol ? 'Editar alumno' : 'Nuevo alumno')

  const alumno = useApi(() => (nocontrol ? obtenerAlumno(nocontrol) : Promise.resolve(null)), [nocontrol])
  // Las opciones solo son sugerencias: si fallan, el formulario se puede usar igual
  const opciones = useApi(obtenerOpciones)

  return (
    <section>
      <h1>{nocontrol ? 'Editar alumno' : 'Nuevo alumno'}</h1>

      <Estado cargando={alumno.cargando} error={alumno.error} onReintentar={alumno.recargar}>
        {/* key: al cambiar de alumno se crea un formulario nuevo con sus datos iniciales */}
        <Formulario key={nocontrol ?? 'nuevo'} nocontrol={nocontrol} alumno={alumno.datos} opciones={opciones.datos} />
      </Estado>

      {/* Si falla la carga (por ejemplo, el alumno no existe) la persona necesita una salida */}
      {alumno.error && (
        <p className="enlace-aparte">
          <Link to="/alumnos">Volver a alumnos</Link>
        </p>
      )}
    </section>
  )
}

interface PropsFormulario {
  nocontrol: string | undefined
  alumno: Alumno | null // el alumno a editar (null al crear)
  opciones: OpcionesAlumno | null // carreras (lista fija) y sugerencias de campus (null si aún no llegan o fallaron)
}

// Convierte el alumno que devuelve la API en los textos que usan los campos
function datosIniciales(alumno: Alumno | null): DatosAlumno {
  if (!alumno) return ALUMNO_VACIO
  return {
    nocontrol: alumno.nocontrol,
    nombre: alumno.nombre,
    apaterno: alumno.apaterno,
    amaterno: alumno.amaterno ?? '',
    sexo: alumno.sexo,
    carrera: alumno.carrera,
    campus: alumno.campus,
  }
}

function Formulario({ nocontrol, alumno, opciones }: PropsFormulario) {
  const navegar = useNavigate()
  const editando = Boolean(nocontrol)

  // Un estado con todo lo capturado, otro con los errores por campo y otro con el aviso general
  const [datos, setDatos] = useState<DatosAlumno>(() => datosIniciales(alumno))
  const [errores, setErrores] = useState<ErroresAlumno>({})
  const [aviso, setAviso] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Opciones de la lista de carreras: las que manda el servidor. Si tardan o fallan, al menos aparece la carrera actual
  const carreras = opciones?.carreras ?? []
  const listaCarreras = datos.carrera && !carreras.includes(datos.carrera) ? [datos.carrera, ...carreras] : carreras
  const opcionesCarrera = listaCarreras.map((c) => ({ valor: c, etiqueta: c }))

  // Cambia un campo y borra su mensaje de error (la persona ya lo está corrigiendo)
  function cambiar(campo: keyof DatosAlumno, valor: string) {
    setDatos((anteriores) => ({ ...anteriores, [campo]: valor }))
    setErrores((anteriores) => ({ ...anteriores, [campo]: undefined }))
  }

  // Manda el foco al primer campo (en el orden de la pantalla) que tenga error
  function enfocarPrimerError(lista: ErroresAlumno) {
    const primero = ORDEN_CAMPOS.find((campo) => lista[campo])
    if (primero) document.getElementById(primero)?.focus()
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setAviso('')

    // 1) Validar en el cliente. Lo capturado no se borra aunque haya errores.
    const nuevos = validarAlumno(datos, editando)
    setErrores(nuevos)
    if (Object.keys(nuevos).length > 0) {
      enfocarPrimerError(nuevos)
      return
    }

    // 2) Mandar los datos a la API
    const cuerpo = datosParaEnviar(datos)
    setEnviando(true)
    try {
      if (nocontrol) await actualizarAlumno(nocontrol, cuerpo)
      else await crearAlumno(normalizarNocontrol(datos.nocontrol), cuerpo)
      navegar('/alumnos', { state: { mensaje: editando ? 'Alumno actualizado.' : 'Alumno creado.' } })
    } catch (e) {
      if (!(e instanceof ErrorApi)) {
        setAviso('Ocurrió un error inesperado. Inténtalo de nuevo.')
      } else if (e.status === 409) {
        // Ya hay un alumno con ese número de control (el identificador no se repite)
        const duplicado: ErroresAlumno = { nocontrol: 'Ya existe un alumno con ese número de control.' }
        setErrores(duplicado)
        enfocarPrimerError(duplicado)
      } else if (e.status === 422) {
        // El servidor rechazó datos que el cliente dejó pasar: se marca cada campo y se explica arriba
        const delServidor: ErroresAlumno = {}
        for (const [campo, mensaje] of Object.entries(e.campos)) {
          if (campo in ALUMNO_VACIO) delServidor[campo as keyof DatosAlumno] = mensaje
        }
        setErrores(delServidor)
        enfocarPrimerError(delServidor)
        setAviso(e.message)
      } else {
        // 404 (el alumno ya no existe), 403, 500, sin conexión...
        setAviso(e.message)
      }
    } finally {
      setEnviando(false)
    }
  }

  return (
    <form className="formulario formulario-ancho" onSubmit={enviar} noValidate>
      <p className="campo-ayuda ancho-completo">Todos los campos son obligatorios, excepto el apellido materno.</p>

      {/* Al editar, el número de control se muestra pero no se puede cambiar (es el identificador) */}
      <CampoConLista
        id="nocontrol"
        etiqueta="Número de control"
        valor={datos.nocontrol}
        onCambio={(v) => cambiar('nocontrol', v.toUpperCase())}
        error={errores.nocontrol}
        ayuda={editando ? 'El número de control no se puede cambiar.' : '7 a 10 letras o números, sin espacios.'}
        soloLectura={editando}
      />

      <CampoFormulario id="nombre" etiqueta="Nombre" valor={datos.nombre} onCambio={(v) => cambiar('nombre', v)} error={errores.nombre} maxLength={60} />

      <CampoFormulario
        id="apaterno"
        etiqueta="Apellido paterno"
        valor={datos.apaterno}
        onCambio={(v) => cambiar('apaterno', v)}
        error={errores.apaterno}
        maxLength={60}
      />

      <CampoFormulario
        id="amaterno"
        etiqueta="Apellido materno (opcional)"
        valor={datos.amaterno}
        onCambio={(v) => cambiar('amaterno', v)}
        error={errores.amaterno}
        maxLength={60}
      />

      <CampoFormulario
        id="sexo"
        etiqueta="Sexo"
        tipo="select"
        valor={datos.sexo}
        onCambio={(v) => cambiar('sexo', v)}
        opciones={SEXOS}
        error={errores.sexo}
      />

      {/* Lista desplegable con las carreras oficiales (las manda el servidor, que también valida la elegida) */}
      <CampoFormulario
        id="carrera"
        etiqueta="Carrera"
        tipo="select"
        valor={datos.carrera}
        onCambio={(v) => cambiar('carrera', v)}
        error={errores.carrera}
        opciones={opcionesCarrera}
      />

      <CampoConLista
        id="campus"
        etiqueta="Campus"
        valor={datos.campus}
        onCambio={(v) => cambiar('campus', v)}
        error={errores.campus}
        sugerencias={opciones?.campus}
        maxLength={40}
      />

      {aviso && (
        <div role="alert" className="alerta alerta-error ancho-completo">
          <strong>No se pudo guardar el alumno</strong>
          <p>{aviso}</p>
        </div>
      )}

      <div className="acciones ancho-completo">
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Guardando…' : 'Guardar alumno'}
        </button>
        <Link to="/alumnos" className="boton boton-secundario">
          Cancelar
        </Link>
      </div>
    </form>
  )
}

interface PropsCampoConLista {
  id: string
  etiqueta: string
  valor: string
  onCambio: (valor: string) => void
  error?: string
  ayuda?: string
  sugerencias?: string[] // opciones del <datalist>
  soloLectura?: boolean
  maxLength?: number
}

// Campo de texto con etiqueta, error y (opcional) lista de sugerencias.
// CampoFormulario no admite <datalist> ni solo lectura, por eso este campo vive aquí.
function CampoConLista({ id, etiqueta, valor, onCambio, error, ayuda, sugerencias, soloLectura = false, maxLength }: PropsCampoConLista) {
  const idError = `${id}-error`
  const idAyuda = `${id}-ayuda`
  const idLista = `${id}-lista`
  const describedBy = [ayuda ? idAyuda : '', error ? idError : ''].filter(Boolean).join(' ') || undefined

  return (
    <div className="campo">
      <label htmlFor={id}>{etiqueta}</label>
      <input
        id={id}
        type="text"
        value={valor}
        maxLength={maxLength}
        readOnly={soloLectura}
        list={sugerencias ? idLista : undefined}
        autoComplete="off"
        onChange={(e) => onCambio(e.target.value)}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
      />
      {sugerencias && (
        <datalist id={idLista}>
          {sugerencias.map((s) => (
            <option key={s} value={s} />
          ))}
        </datalist>
      )}
      {ayuda && (
        <p id={idAyuda} className="campo-ayuda">
          {ayuda}
        </p>
      )}
      {error && (
        <p id={idError} className="campo-error">
          {error}
        </p>
      )}
    </div>
  )
}
