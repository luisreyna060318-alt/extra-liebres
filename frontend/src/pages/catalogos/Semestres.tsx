import { useState } from 'react'
import { eliminarSemestre, listarSemestres } from '../../api/admin.ts'
import Confirmacion from '../../components/Confirmacion.tsx'
import Estado from '../../components/Estado.tsx'
import Paginacion from '../../components/Paginacion.tsx'
import { useApi } from '../../hooks/useApi.ts'
import type { SemestreAdmin } from '../../tiposAdmin.ts'
import { nombreMes, textoError } from '../../utils/admin.ts'
import { nombreSemestre } from '../../utils/grupos.ts'
import SemestreFormulario from './SemestreFormulario.tsx'

// Pestaña de semestres (HU-03.3): del más reciente al más antiguo (el servidor ya los ordena), sin filtros.
// Los semestres no se desactivan: solo se crean, editan y eliminan.
export default function Semestres() {
  const [pagina, setPagina] = useState(1)

  // panel: 'nuevo' = formulario vacío, un semestre = editarlo, null = panel cerrado
  const [panel, setPanel] = useState<'nuevo' | SemestreAdmin | null>(null)
  const [porEliminar, setPorEliminar] = useState<SemestreAdmin | null>(null)
  const [mensaje, setMensaje] = useState('')
  const [aviso, setAviso] = useState('')
  const [ocupado, setOcupado] = useState(false)

  const lista = useApi(() => listarSemestres(pagina), [pagina])
  const total = lista.datos?.total ?? 0

  function empezarAccion() {
    setMensaje('')
    setAviso('')
    setPanel(null)
    setPorEliminar(null)
  }

  function abrirPanel(valor: 'nuevo' | SemestreAdmin) {
    empezarAccion()
    setPanel(valor)
  }

  function alGuardar(texto: string) {
    setPanel(null)
    setMensaje(texto)
    lista.recargar()
  }

  // Solo se llama después de que la persona confirmó
  async function eliminar(s: SemestreAdmin) {
    setOcupado(true)
    setAviso('')
    try {
      await eliminarSemestre(s.idsemestre)
      setPorEliminar(null)
      setMensaje('Semestre eliminado.')
      if (lista.datos?.items.length === 1 && pagina > 1) setPagina(pagina - 1)
      else lista.recargar()
    } catch (e) {
      // 409: el semestre tiene grupos. Se muestra el mensaje del servidor tal cual.
      setPorEliminar(null)
      setAviso(textoError(e))
    } finally {
      setOcupado(false)
    }
  }

  return (
    <div>
      <div className="encabezado-pagina">
        <h2>Semestres</h2>
        <button type="button" className="boton" onClick={() => abrirPanel('nuevo')}>
          Nuevo semestre
        </button>
      </div>

      <div role="status">{mensaje && <p className="alerta alerta-exito">{mensaje}</p>}</div>
      {aviso && (
        <div role="alert" className="alerta alerta-error">
          <p>{aviso}</p>
        </div>
      )}

      {panel && (
        <SemestreFormulario
          key={panel === 'nuevo' ? 'nuevo' : panel.idsemestre}
          semestre={panel === 'nuevo' ? null : panel}
          onGuardado={alGuardar}
          onCancelar={() => setPanel(null)}
        />
      )}

      {porEliminar && (
        <Confirmacion
          id="confirmar-semestre"
          titulo="Eliminar semestre"
          texto={`¿Seguro que quieres eliminar el semestre ${nombreSemestre(porEliminar)}? Esta acción no se puede deshacer.`}
          textoConfirmar="Sí, eliminar"
          enviando={ocupado}
          onConfirmar={() => eliminar(porEliminar)}
          onCancelar={() => setPorEliminar(null)}
        />
      )}

      <Estado
        cargando={lista.cargando}
        error={lista.error}
        onReintentar={lista.recargar}
        vacio={lista.datos?.items.length === 0}
        textoVacio="Todavía no hay semestres registrados."
      >
        {lista.datos && (
          <>
            <p aria-live="polite">
              {total} {total === 1 ? 'semestre' : 'semestres'} en total
            </p>

            <div className="tabla-contenedor">
              <table className="tabla tabla-apilable">
                <caption className="solo-lectores">Semestres registrados, del más reciente al más antiguo</caption>
                <thead>
                  <tr>
                    <th scope="col">Semestre</th>
                    <th scope="col">Año</th>
                    <th scope="col">Mes de inicio</th>
                    <th scope="col">Mes de término</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {lista.datos.items.map((s) => (
                    <tr key={s.idsemestre}>
                      <td data-etiqueta="Semestre">{nombreSemestre(s)}</td>
                      <td data-etiqueta="Año">{s.anio}</td>
                      <td data-etiqueta="Mes de inicio">{nombreMes(s.mesinicio)}</td>
                      <td data-etiqueta="Mes de término">{nombreMes(s.mestermino)}</td>
                      <td data-etiqueta="Acciones">
                        <div className="acciones-fila">
                          <button type="button" className="boton boton-secundario" onClick={() => abrirPanel(s)} aria-label={`Editar el semestre ${nombreSemestre(s)}`}>
                            Editar
                          </button>
                          <button
                            type="button"
                            className="boton boton-peligro"
                            disabled={ocupado}
                            onClick={() => {
                              empezarAccion()
                              setPorEliminar(s)
                            }}
                            aria-label={`Eliminar el semestre ${nombreSemestre(s)}`}
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

            <Paginacion etiqueta="Paginación de semestres" pagina={pagina} total={total} onCambiar={setPagina} />
          </>
        )}
      </Estado>
    </div>
  )
}
