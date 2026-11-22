import { useState } from 'react'
import { actualizarPromotor, eliminarPromotor, listarPromotores } from '../../api/admin.ts'
import Confirmacion from '../../components/Confirmacion.tsx'
import Estado from '../../components/Estado.tsx'
import FiltrosCatalogo from '../../components/FiltrosCatalogo.tsx'
import Paginacion from '../../components/Paginacion.tsx'
import { useApi } from '../../hooks/useApi.ts'
import type { FiltroEstado, PromotorAdmin } from '../../tiposAdmin.ts'
import { textoError } from '../../utils/admin.ts'
import { nombrePromotor } from '../../utils/grupos.ts'
import PromotorFormulario from './PromotorFormulario.tsx'

// Pestaña de promotores (HU-03.1): lista con búsqueda y filtro, y alta, edición, baja y eliminación
export default function Promotores() {
  const [q, setQ] = useState('')
  const [estado, setEstado] = useState<FiltroEstado>('activos')
  const [pagina, setPagina] = useState(1)

  // panel: 'nuevo' = formulario vacío, un promotor = editarlo, null = panel cerrado
  const [panel, setPanel] = useState<'nuevo' | PromotorAdmin | null>(null)
  const [porEliminar, setPorEliminar] = useState<PromotorAdmin | null>(null) // espera confirmación
  const [mensaje, setMensaje] = useState('') // aviso de éxito (role="status")
  const [aviso, setAviso] = useState('') // error de una acción, por ejemplo el 409 "tiene grupos" (role="alert")
  const [ocupado, setOcupado] = useState(false) // hay una acción enviándose

  const lista = useApi(() => listarPromotores(q, estado, pagina), [q, estado, pagina])
  const total = lista.datos?.total ?? 0

  function buscar(texto: string) {
    setQ(texto)
    setPagina(1)
  }

  function cambiarEstado(nuevo: FiltroEstado) {
    setEstado(nuevo)
    setPagina(1)
  }

  // Cada acción empieza limpiando los avisos anteriores y cerrando lo que estuviera abierto
  function empezarAccion() {
    setMensaje('')
    setAviso('')
    setPanel(null)
    setPorEliminar(null)
  }

  function abrirPanel(valor: 'nuevo' | PromotorAdmin) {
    empezarAccion()
    setPanel(valor)
  }

  // El formulario ya guardó: se cierra el panel, se avisa y se vuelve a consultar la lista
  function alGuardar(texto: string) {
    setPanel(null)
    setMensaje(texto)
    lista.recargar()
  }

  // Desactivar o reactivar: PUT con los mismos datos y activo al revés
  async function cambiarActivo(p: PromotorAdmin) {
    empezarAccion()
    setOcupado(true)
    try {
      await actualizarPromotor(p.rfc, { nombre: p.nombre, apaterno: p.apaterno, amaterno: p.amaterno, activo: !p.activo })
      setMensaje(p.activo ? 'Promotor desactivado.' : 'Promotor reactivado.')
      lista.recargar()
    } catch (e) {
      setAviso(textoError(e))
    } finally {
      setOcupado(false)
    }
  }

  // Solo se llama después de que la persona confirmó
  async function eliminar(p: PromotorAdmin) {
    setOcupado(true)
    setAviso('')
    try {
      await eliminarPromotor(p.rfc)
      setPorEliminar(null)
      setMensaje('Promotor eliminado.')
      // Si era el único de la última página, se regresa una página para no quedar en una vacía
      if (lista.datos?.items.length === 1 && pagina > 1) setPagina(pagina - 1)
      else lista.recargar()
    } catch (e) {
      // 409: el promotor tiene grupos. Se muestra el mensaje del servidor tal cual.
      setPorEliminar(null)
      setAviso(textoError(e))
    } finally {
      setOcupado(false)
    }
  }

  return (
    <div>
      <div className="encabezado-pagina">
        <h2>Promotores</h2>
        <button type="button" className="boton" onClick={() => abrirPanel('nuevo')}>
          Nuevo promotor
        </button>
      </div>

      {/* El contenedor de role="status" siempre está en la página para que se anuncie el texto cuando aparece */}
      <div role="status">{mensaje && <p className="alerta alerta-exito">{mensaje}</p>}</div>
      {aviso && (
        <div role="alert" className="alerta alerta-error">
          <p>{aviso}</p>
        </div>
      )}

      {panel && (
        // key: al pasar de un promotor a otro se crea un formulario nuevo con sus datos
        <PromotorFormulario
          key={panel === 'nuevo' ? 'nuevo' : panel.rfc}
          promotor={panel === 'nuevo' ? null : panel}
          onGuardado={alGuardar}
          onCancelar={() => setPanel(null)}
        />
      )}

      {porEliminar && (
        <Confirmacion
          id="confirmar-promotor"
          titulo="Eliminar promotor"
          texto={`¿Seguro que quieres eliminar a ${nombrePromotor(porEliminar)} (${porEliminar.rfc})? Esta acción no se puede deshacer.`}
          textoConfirmar="Sí, eliminar"
          enviando={ocupado}
          onConfirmar={() => eliminar(porEliminar)}
          onCancelar={() => setPorEliminar(null)}
        />
      )}

      <FiltrosCatalogo prefijo="promotores" etiquetaBusqueda="RFC o nombre" estado={estado} onBuscar={buscar} onEstado={cambiarEstado} />

      <Estado
        cargando={lista.cargando}
        error={lista.error}
        onReintentar={lista.recargar}
        vacio={lista.datos?.items.length === 0}
        textoVacio={q || estado !== 'activos' ? 'Ningún promotor cumple con los filtros elegidos.' : 'Todavía no hay promotores registrados.'}
      >
        {lista.datos && (
          <>
            <p aria-live="polite">
              {total} {total === 1 ? 'promotor' : 'promotores'} en total
            </p>

            <div className="tabla-contenedor">
              <table className="tabla tabla-apilable">
                <caption className="solo-lectores">Promotores registrados</caption>
                <thead>
                  <tr>
                    <th scope="col">RFC</th>
                    <th scope="col">Nombre</th>
                    <th scope="col">Estado</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {lista.datos.items.map((p) => (
                    <tr key={p.rfc}>
                      <td data-etiqueta="RFC">{p.rfc}</td>
                      <td data-etiqueta="Nombre">{nombrePromotor(p)}</td>
                      <td data-etiqueta="Estado">{p.activo ? 'Activo' : 'Inactivo'}</td>
                      <td data-etiqueta="Acciones">
                        <div className="acciones-fila">
                          <button type="button" className="boton boton-secundario" onClick={() => abrirPanel(p)} aria-label={`Editar a ${nombrePromotor(p)}`}>
                            Editar
                          </button>
                          <button
                            type="button"
                            className="boton boton-secundario"
                            disabled={ocupado}
                            onClick={() => cambiarActivo(p)}
                            aria-label={`${p.activo ? 'Desactivar' : 'Reactivar'} a ${nombrePromotor(p)}`}
                          >
                            {p.activo ? 'Desactivar' : 'Reactivar'}
                          </button>
                          <button
                            type="button"
                            className="boton boton-peligro"
                            disabled={ocupado}
                            onClick={() => {
                              empezarAccion()
                              setPorEliminar(p)
                            }}
                            aria-label={`Eliminar a ${nombrePromotor(p)}`}
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

            <Paginacion etiqueta="Paginación de promotores" pagina={pagina} total={total} onCambiar={setPagina} />
          </>
        )}
      </Estado>
    </div>
  )
}
