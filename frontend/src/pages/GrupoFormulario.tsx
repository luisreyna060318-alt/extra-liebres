import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { cargarCatalogos } from '../api/catalogos.ts'
import type { Catalogos } from '../api/catalogos.ts'
import { ErrorApi } from '../api/cliente.ts'
import { actualizarGrupo, crearGrupo, obtenerGrupo } from '../api/grupos.ts'
import CampoFormulario from '../components/CampoFormulario.tsx'
import Estado from '../components/Estado.tsx'
import Pronostico from '../components/Pronostico.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import type { Grupo, GrupoEntrada } from '../types.ts'
import { DIAS, GRUPO_VACIO, INSTALACIONES, esDeportiva, nombrePromotor, nombreSemestre, recortarHora, validarGrupo } from '../utils/grupos.ts'
import type { DatosGrupo, ErroresGrupo } from '../utils/grupos.ts'

// Orden de los campos en pantalla: sirve para mandar el foco al primero que tenga error
const ORDEN_CAMPOS: (keyof DatosGrupo)[] = [
  'idextraescolar',
  'idsemestre',
  'rfcpromotor',
  'dia',
  'horainicio',
  'horatermino',
  'lugar',
]

// Aviso grande arriba del botón: errores del servidor (409 cruce de horario, 422, etc.)
interface Aviso {
  titulo: string
  texto: string
}

// --- Pantalla: carga los catálogos (y el grupo, si se edita) y luego muestra el formulario ---
export default function GrupoFormulario() {
  const { id } = useParams() // sin id = grupo nuevo; con id = editar
  useTitulo(id ? 'Editar grupo' : 'Nuevo grupo')

  const catalogos = useApi(cargarCatalogos)
  const grupo = useApi(() => (id ? obtenerGrupo(id) : Promise.resolve(null)), [id])

  function reintentar() {
    catalogos.recargar()
    grupo.recargar()
  }

  return (
    <section>
      <h1>{id ? 'Editar grupo' : 'Nuevo grupo'}</h1>

      <Estado
        cargando={catalogos.cargando || grupo.cargando}
        error={catalogos.error ?? grupo.error}
        onReintentar={reintentar}
      >
        {/* key: al cambiar de grupo se crea un formulario nuevo con sus datos iniciales */}
        {catalogos.datos && <Formulario key={id ?? 'nuevo'} id={id} catalogos={catalogos.datos} grupo={grupo.datos} />}
      </Estado>
    </section>
  )
}

interface PropsFormulario {
  id: string | undefined
  catalogos: Catalogos
  grupo: Grupo | null // el grupo a editar (null al crear)
}

// Convierte el grupo que devuelve la API en los textos que usan los campos
function datosIniciales(grupo: Grupo | null): DatosGrupo {
  if (!grupo) return GRUPO_VACIO
  return {
    idsemestre: String(grupo.idsemestre),
    idextraescolar: String(grupo.idextraescolar),
    rfcpromotor: grupo.rfcpromotor,
    dia: grupo.dia,
    horainicio: recortarHora(grupo.horainicio),
    horatermino: recortarHora(grupo.horatermino),
    lugar: grupo.aula,
  }
}

function Formulario({ id, catalogos, grupo }: PropsFormulario) {
  const navegar = useNavigate()

  // Un solo estado con todo lo capturado, otro con los errores por campo y otro con el aviso del servidor
  const [datos, setDatos] = useState<DatosGrupo>(() => datosIniciales(grupo))
  const [errores, setErrores] = useState<ErroresGrupo>({})
  const [aviso, setAviso] = useState<Aviso | null>(null)
  const [enviando, setEnviando] = useState(false)

  // La actividad elegida (con su tipo y si es al aire libre) decide qué campos se muestran
  const actividad = catalogos.actividades.find((a) => String(a.idextraescolar) === datos.idextraescolar)
  const deportiva = esDeportiva(actividad)

  // Cambia un campo y borra su mensaje de error (la persona ya lo está corrigiendo)
  function cambiar(campo: keyof DatosGrupo, valor: string) {
    setDatos((anteriores) => ({ ...anteriores, [campo]: valor }))
    setErrores((anteriores) => ({ ...anteriores, [campo]: undefined }))
  }

  // Al cambiar de actividad, si el tipo de lugar ya no aplica (instalación <-> aula) se limpia lo capturado
  function cambiarActividad(valor: string) {
    const nueva = catalogos.actividades.find((a) => String(a.idextraescolar) === valor)
    const cambiaElLugar = esDeportiva(nueva) !== deportiva
    setDatos((anteriores) => ({
      ...anteriores,
      idextraescolar: valor,
      lugar: cambiaElLugar ? '' : anteriores.lugar,
    }))
    setErrores((anteriores) => ({
      ...anteriores,
      idextraescolar: undefined,
      lugar: cambiaElLugar ? undefined : anteriores.lugar,
    }))
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setAviso(null)

    // 1) Validar en el cliente. Lo capturado no se borra aunque haya errores.
    const nuevos = validarGrupo(datos, actividad)
    setErrores(nuevos)
    const primerError = ORDEN_CAMPOS.find((campo) => nuevos[campo])
    if (primerError) {
      document.getElementById(primerError)?.focus()
      return
    }

    // 2) Mandar los datos a la API. El campo "lugar" viaja como "aula" (así lo llama el backend).
    const cuerpo: GrupoEntrada = {
      idsemestre: Number(datos.idsemestre),
      idextraescolar: Number(datos.idextraescolar),
      rfcpromotor: datos.rfcpromotor,
      dia: datos.dia,
      horainicio: datos.horainicio,
      horatermino: datos.horatermino,
      aula: datos.lugar.trim(),
    }

    setEnviando(true)
    try {
      if (id) await actualizarGrupo(id, cuerpo)
      else await crearGrupo(cuerpo)
      navegar('/grupos', { state: { mensaje: id ? 'Grupo actualizado.' : 'Grupo creado.' } })
    } catch (e) {
      if (!(e instanceof ErrorApi)) {
        setAviso({ titulo: 'No se pudo guardar el grupo', texto: 'Ocurrió un error inesperado.' })
      } else if (e.status === 409) {
        // Cruce de horario con otro grupo del mismo promotor o lugar (RN-03). El mensaje dice cuál grupo.
        setAviso({ titulo: 'Hay un cruce de horario', texto: e.message })
      } else if (e.status === 422) {
        // El servidor rechazó datos que el cliente dejó pasar: se marca cada campo y se explica arriba
        const delServidor: ErroresGrupo = {}
        for (const [campo, mensaje] of Object.entries(e.campos)) {
          const nombre = campo === 'aula' ? 'lugar' : campo // el backend le llama "aula" al lugar
          if (nombre in GRUPO_VACIO) delServidor[nombre as keyof DatosGrupo] = mensaje
        }
        setErrores(delServidor)
        setAviso({ titulo: 'El servidor no aceptó los datos', texto: e.message })
      } else {
        // 404 (algo ya no existe), 403, 500, sin conexión...
        setAviso({ titulo: 'No se pudo guardar el grupo', texto: e.message })
      }
    } finally {
      setEnviando(false)
    }
  }

  // --- Opciones de los selects ---
  // Solo se ofrecen actividades y promotores activos (más el que ya tiene el grupo que se edita)
  const opcionesActividad = catalogos.actividades
    .filter((a) => a.activo !== false || String(a.idextraescolar) === datos.idextraescolar)
    .map((a) => ({ valor: String(a.idextraescolar), etiqueta: a.nombreextra }))
  const opcionesSemestre = catalogos.semestres.map((s) => ({ valor: String(s.idsemestre), etiqueta: nombreSemestre(s) }))
  const opcionesPromotor = catalogos.promotores
    .filter((p) => p.activo !== false || p.rfc === datos.rfcpromotor)
    .map((p) => ({ valor: p.rfc, etiqueta: nombrePromotor(p) }))
  const opcionesDia = DIAS.map((d) => ({ valor: d.valor, etiqueta: d.etiqueta }))

  // Si el grupo guardado tiene un lugar que ya no está en la lista, se conserva como opción para no perderlo en silencio
  const lugares = datos.lugar && !INSTALACIONES.includes(datos.lugar) ? [...INSTALACIONES, datos.lugar] : INSTALACIONES
  const opcionesLugar = lugares.map((l) => ({ valor: l, etiqueta: l }))

  return (
    <div className="grupo-disposicion">
      <form className="formulario formulario-ancho" onSubmit={enviar} noValidate>
        <p className="campo-ayuda ancho-completo">Todos los campos son obligatorios.</p>

        <CampoFormulario
          id="idextraescolar"
          etiqueta="Actividad"
          tipo="select"
          valor={datos.idextraescolar}
          onCambio={cambiarActividad}
          opciones={opcionesActividad}
          error={errores.idextraescolar}
          ayuda={actividad ? undefined : 'Según la actividad se pedirá una instalación o un aula.'}
        />

        <CampoFormulario
          id="idsemestre"
          etiqueta="Semestre"
          tipo="select"
          valor={datos.idsemestre}
          onCambio={(v) => cambiar('idsemestre', v)}
          opciones={opcionesSemestre}
          error={errores.idsemestre}
        />

        <CampoFormulario
          id="rfcpromotor"
          etiqueta="Promotor"
          tipo="select"
          valor={datos.rfcpromotor}
          onCambio={(v) => cambiar('rfcpromotor', v)}
          opciones={opcionesPromotor}
          error={errores.rfcpromotor}
        />

        <CampoFormulario
          id="dia"
          etiqueta="Día"
          tipo="select"
          valor={datos.dia}
          onCambio={(v) => cambiar('dia', v)}
          opciones={opcionesDia}
          error={errores.dia}
        />

        <CampoFormulario
          id="horainicio"
          etiqueta="Hora de inicio"
          tipo="time"
          valor={datos.horainicio}
          onCambio={(v) => cambiar('horainicio', v)}
          error={errores.horainicio}
        />

        <CampoFormulario
          id="horatermino"
          etiqueta="Hora de término"
          tipo="time"
          valor={datos.horatermino}
          onCambio={(v) => cambiar('horatermino', v)}
          error={errores.horatermino}
        />

        {/* Formulario dinámico (HU-04.2): deportiva = lista de instalaciones; cultural o cívica = aula escrita */}
        {actividad &&
          (deportiva ? (
            <CampoFormulario
              id="lugar"
              etiqueta="Lugar"
              tipo="select"
              valor={datos.lugar}
              onCambio={(v) => cambiar('lugar', v)}
              opciones={opcionesLugar}
              error={errores.lugar}
            />
          ) : (
            <CampoFormulario
              id="lugar"
              etiqueta="Aula"
              valor={datos.lugar}
              onCambio={(v) => cambiar('lugar', v)}
              maxLength={60}
              error={errores.lugar}
            />
          ))}

        {aviso && (
          <div role="alert" className="alerta alerta-error ancho-completo">
            <strong>{aviso.titulo}</strong>
            <p>{aviso.texto}</p>
          </div>
        )}

        <div className="acciones ancho-completo">
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar grupo'}
          </button>
          <Link to="/grupos" className="boton boton-secundario">
            Cancelar
          </Link>
        </div>
      </form>

      {/* Al aire libre: el pronóstico se ve junto al formulario */}
      {actividad?.al_aire_libre && <Pronostico />}
    </div>
  )
}
