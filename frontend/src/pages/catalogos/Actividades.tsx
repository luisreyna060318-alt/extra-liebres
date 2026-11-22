import { useState } from 'react'
import { actualizarActividad, eliminarActividad, listarActividades } from '../../api/admin.ts'
import Confirmacion from '../../components/Confirmacion.tsx'
import Estado from '../../components/Estado.tsx'
import FiltrosCatalogo from '../../components/FiltrosCatalogo.tsx'
import Paginacion from '../../components/Paginacion.tsx'
import { useApi } from '../../hooks/useApi.ts'
import type { ActividadAdmin, FiltroEstado } from '../../tiposAdmin.ts'
import { nombreTipo, textoError } from '../../utils/admin.ts'
import ActividadFormulario from './ActividadFormulario.tsx'

// Pestaña de actividades extraescolares (HU-03.2). Funciona igual que la de promotores.
export default function Actividades() {
  const [q, setQ] = useState('')
  const [estado, setEstado] = useState<FiltroEstado>('activos')
  const [pagina, setPagina] = useState(1)

  // panel: 'nuevo' = formulario vacío, una actividad = editarla, null = panel cerrado
  const [panel, setPanel] = useState<'nuevo' | ActividadAdmin | null>(null)
  const [porEliminar, setPorEliminar] = useState<ActividadAdmin | null>(null)
  const [mensaje, setMensaje] = useState('')
  const [aviso, setAviso] = useState('')
  const [ocupado, setOcupado] = useState(false)

  const lista = useApi(() => listarActividades(q, estado, pagina), [q, estado, pagina])
  const total = lista.datos?.total ?? 0

  function buscar(texto: string) {
    setQ(texto)
    setPagina(1)
  }

  function cambiarEstado(nuevo: FiltroEstado) {
    setEstado(nuevo)
    setPagina(1)
  }

  function empezarAccion() {
    setMensaje('')
    setAviso('')
    setPanel(null)
    setPorEliminar(null)
  }

  function abrirPanel(valor: 'nuevo' | ActividadAdmin) {
    empezarAccion()
    setPanel(valor)
  }

  function alGuardar(texto: string) {
    setPanel(null)
    setMensaje(texto)
    lista.recargar()
  }

  // Desactivar o reactivar: PUT con los mismos datos y activo al revés
  async function cambiarActivo(a: ActividadAdmin) {
    empezarAccion()
    setOcupado(true)
    try {
      await actualizarActividad(a.idextraescolar, {
        nombreextra: a.nombreextra,
        tipo: a.tipo,
        al_aire_libre: a.al_aire_libre,
        activo: !a.activo,
      })
      setMensaje(a.activo ? 'Actividad desactivada.' : 'Actividad reactivada.')
      lista.recargar()
    } catch (e) {
      setAviso(textoError(e))
    } finally {
      setOcupado(false)
    }
  }

  // Solo se llama después de que la persona confirmó
  async function eliminar(a: ActividadAdmin) {
    setOcupado(true)
    setAviso('')
    try {
      await eliminarActividad(a.idextraescolar)
      setPorEliminar(null)
      setMensaje('Actividad eliminada.')
      if (lista.datos?.items.length === 1 && pagina > 1) setPagina(pagina - 1)
      else lista.recargar()
    } catch (e) {
      // 409: la actividad tiene grupos. Se muestra el mensaje del servidor tal cual.
      setPorEliminar(null)
      setAviso(textoError(e))
    } finally {
      setOcupado(false)
    }
  }

  return (
    <div>
      <div className="encabezado-pagina">
        <h2>Actividades</h2>
        <button type="button" className="boton" onClick={() => abrirPanel('nuevo')}>
          Nueva actividad
        </button>
      </div>

      <div role="status">{mensaje && <p className="alerta alerta-exito">{mensaje}</p>}</div>
      {aviso && (
        <div role="alert" className="alerta alerta-error">
          <p>{aviso}</p>
        </div>
      )}

      {panel && (
        <ActividadFormulario
          key={panel === 'nuevo' ? 'nuevo' : panel.idextraescolar}
          actividad={panel === 'nuevo' ? null : panel}
          onGuardado={alGuardar}
          onCancelar={() => setPanel(null)}
        />
      )}

      {porEliminar && (
        <Confirmacion
          id="confirmar-actividad"
          titulo="Eliminar actividad"
          texto={`¿Seguro que quieres eliminar la actividad "${porEliminar.nombreextra}"? Esta acción no se puede deshacer.`}
          textoConfirmar="Sí, eliminar"
          enviando={ocupado}
          onConfirmar={() => eliminar(porEliminar)}
          onCancelar={() => setPorEliminar(null)}
        />
      )}

      <FiltrosCatalogo prefijo="actividades" etiquetaBusqueda="nombre" estado={estado} onBuscar={buscar} onEstado={cambiarEstado} />

      <Estado
        cargando={lista.cargando}
        error={lista.error}
        onReintentar={lista.recargar}
        vacio={lista.datos?.items.length === 0}
        textoVacio={q || estado !== 'activos' ? 'Ninguna actividad cumple con los filtros elegidos.' : 'Todavía no hay actividades registradas.'}
      >
        {lista.datos && (
          <>
            <p aria-live="polite">
              {total} {total === 1 ? 'actividad' : 'actividades'} en total
            </p>

            <div className="tabla-contenedor">
              <table className="tabla tabla-apilable">
                <caption className="solo-lectores">Actividades registradas</caption>
                <thead>
                  <tr>
                    <th scope="col">Actividad</th>
                    <th scope="col">Tipo</th>
                    <th scope="col">Al aire libre</th>
                    <th scope="col">Estado</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {lista.datos.items.map((a) => (
                    <tr key={a.idextraescolar}>
                      <td data-etiqueta="Actividad">{a.nombreextra}</td>
                      <td data-etiqueta="Tipo">{nombreTipo(a.tipo)}</td>
                      <td data-etiqueta="Al aire libre">{a.al_aire_libre ? 'Sí' : 'No'}</td>
                      <td data-etiqueta="Estado">{a.activo ? 'Activa' : 'Inactiva'}</td>
                      <td data-etiqueta="Acciones">
                        <div className="acciones-fila">
                          <button type="button" className="boton boton-secundario" onClick={() => abrirPanel(a)} aria-label={`Editar ${a.nombreextra}`}>
                            Editar
                          </button>
                          <button
                            type="button"
                            className="boton boton-secundario"
                            disabled={ocupado}
                            onClick={() => cambiarActivo(a)}
                            aria-label={`${a.activo ? 'Desactivar' : 'Reactivar'} ${a.nombreextra}`}
                          >
                            {a.activo ? 'Desactivar' : 'Reactivar'}
                          </button>
                          <button
                            type="button"
                            className="boton boton-peligro"
                            disabled={ocupado}
                            onClick={() => {
                              empezarAccion()
                              setPorEliminar(a)
                            }}
                            aria-label={`Eliminar ${a.nombreextra}`}
                          >
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Paginacion etiqueta="Paginación de actividades" pagina={pagina} total={total} onCambiar={setPagina} />
          </>
        )}
      </Estado>
    </div>
  )
}
