import { useState } from 'react'
import type { FormEvent } from 'react'
import { actualizarUsuario, listarUsuarios } from '../api/admin.ts'
import CampoFormulario from '../components/CampoFormulario.tsx'
import Confirmacion from '../components/Confirmacion.tsx'
import Estado from '../components/Estado.tsx'
import Paginacion from '../components/Paginacion.tsx'
import { useAuth } from '../context/AuthContext.tsx'
import { useApi } from '../hooks/useApi.ts'
import { useTitulo } from '../hooks/useTitulo.ts'
import type { FiltroCuentas, FiltrosUsuarios, UsuarioAdmin, UsuarioCambios } from '../tiposAdmin.ts'
import type { Rol } from '../types.ts'
import { ROLES, formatoFecha, textoError } from '../utils/admin.ts'

const SIN_FILTROS: FiltrosUsuarios = { q: '', rol: '', cuentas: 'todas' }

// Acción que espera confirmación: suspender una cuenta o quitarle el rol de administrador
interface PorConfirmar {
  usuario: UsuarioAdmin
  accion: 'suspender' | 'quitar-admin'
}

// Administración de usuarios (HU-01.4), solo administrador: buscar, cambiar rol y suspender o reactivar.
// Nunca se muestran ni se piden contraseñas.
export default function Usuarios() {
  useTitulo('Usuarios')
  const { usuario: yo } = useAuth() // para marcar "(tú)" en la propia fila

  const [texto, setTexto] = useState('') // lo que se escribe en la búsqueda (se aplica al pulsar "Buscar")
  const [filtros, setFiltros] = useState<FiltrosUsuarios>(SIN_FILTROS)
  const [pagina, setPagina] = useState(1)

  // Rol elegido en el select de cada fila, por id de usuario. Si no hay entrada, el select muestra el rol actual.
  const [rolesElegidos, setRolesElegidos] = useState<Record<number, Rol>>({})
  const [porConfirmar, setPorConfirmar] = useState<PorConfirmar | null>(null)
  const [mensaje, setMensaje] = useState('') // aviso de éxito (role="status")
  const [aviso, setAviso] = useState('') // error del servidor, por ejemplo el 409 del último administrador (role="alert")
  const [ocupado, setOcupado] = useState(false)

  const lista = useApi(() => listarUsuarios(filtros, pagina), [filtros.q, filtros.rol, filtros.cuentas, pagina])
  const total = lista.datos?.total ?? 0
  const hayFiltros = filtros.q !== '' || filtros.rol !== '' || filtros.cuentas !== 'todas'

  function buscar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setFiltros((anteriores) => ({ ...anteriores, q: texto.trim() }))
    setPagina(1)
  }

  // Al cambiar un filtro se regresa a la primera página
  function cambiarFiltro(cambios: Partial<FiltrosUsuarios>) {
    setFiltros((anteriores) => ({ ...anteriores, ...cambios }))
    setPagina(1)
  }

  function limpiarFiltros() {
    setTexto('')
    setFiltros(SIN_FILTROS)
    setPagina(1)
  }

  // Manda el cambio al servidor (PATCH). Cada acción termina con un aviso y la lista se vuelve a consultar.
  async function enviar(u: UsuarioAdmin, cambios: UsuarioCambios, textoExito: string) {
    setOcupado(true)
    setMensaje('')
    setAviso('')
    try {
      await actualizarUsuario(u.id, cambios)
      setMensaje(textoExito)
      lista.recargar()
    } catch (e) {
      // 409: dejaría al sistema sin administradores activos. Se muestra el mensaje del servidor tal cual.
      setAviso(textoError(e))
    } finally {
      setPorConfirmar(null)
      // El select de la fila vuelve a mostrar el rol real de la cuenta
      setRolesElegidos((anteriores) => {
        const copia = { ...anteriores }
        delete copia[u.id]
        return copia
      })
      setOcupado(false)
    }
  }

  function guardarRol(u: UsuarioAdmin) {
    const nuevo = rolesElegidos[u.id]
    if (!nuevo || nuevo === u.rol) return
    setMensaje('')
    setAviso('')
    // Quitar el rol de administrador pide confirmación; dar el rol de administrador, no
    if (u.rol === 'administrador') setPorConfirmar({ usuario: u, accion: 'quitar-admin' })
    else void enviar(u, { rol: nuevo }, 'Rol actualizado.')
  }

  function suspender(u: UsuarioAdmin) {
    setMensaje('')
    setAviso('')
    setPorConfirmar({ usuario: u, accion: 'suspender' })
  }

  // Texto de la confirmación según la acción; si es la propia cuenta se advierte
  function textoConfirmacion(p: PorConfirmar): string {
    const { nombre, correo } = p.usuario
    const propia = p.usuario.id === yo?.id ? ' Es tu propia cuenta.' : ''
    if (p.accion === 'suspender') {
      return `¿Suspender la cuenta de ${nombre} (${correo})? No podrá iniciar sesión hasta que se reactive.${propia}`
    }
    return `¿Quitar el rol de administrador a ${nombre}? Pasará a capturista y perderá el acceso a catálogos y usuarios.${propia}`
  }

  return (
    <section>
      <h1>Usuarios</h1>

      <div role="status">{mensaje && <p className="alerta alerta-exito">{mensaje}</p>}</div>
      {aviso && (
        <div role="alert" className="alerta alerta-error">
          <p>{aviso}</p>
        </div>
      )}

      {porConfirmar && (
        <Confirmacion
          id="confirmar-usuario"
          titulo={porConfirmar.accion === 'suspender' ? 'Suspender cuenta' : 'Quitar rol de administrador'}
          texto={textoConfirmacion(porConfirmar)}
          textoConfirmar={porConfirmar.accion === 'suspender' ? 'Sí, suspender' : 'Sí, quitar el rol'}
          enviando={ocupado}
          onConfirmar={() =>
            void enviar(
              porConfirmar.usuario,
              porConfirmar.accion === 'suspender' ? { activo: false } : { rol: 'capturista' },
              porConfirmar.accion === 'suspender' ? 'Cuenta suspendida.' : 'Rol actualizado.',
            )
          }
          onCancelar={() => setPorConfirmar(null)}
        />
      )}

      <form onSubmit={buscar}>
        <fieldset className="filtros">
          <legend>Buscar y filtrar usuarios</legend>
          <div className="filtros-campos">
            <CampoFormulario id="usuarios-q" etiqueta="Buscar por nombre o correo" valor={texto} onCambio={setTexto} />
            <div className="campo">
              <label htmlFor="usuarios-rol">Rol</label>
              <select id="usuarios-rol" value={filtros.rol} onChange={(e) => cambiarFiltro({ rol: e.target.value as FiltrosUsuarios['rol'] })}>
                <option value="">Todos</option>
                {ROLES.map((r) => (
                  <option key={r.valor} value={r.valor}>
                    {r.etiqueta}
                  </option>
                ))}
              </select>
            </div>
            <div className="campo">
              <label htmlFor="usuarios-cuentas">Estado de la cuenta</label>
              <select id="usuarios-cuentas" value={filtros.cuentas} onChange={(e) => cambiarFiltro({ cuentas: e.target.value as FiltroCuentas })}>
                <option value="todas">Todas</option>
                <option value="activas">Activas</option>
                <option value="suspendidas">Suspendidas</option>
              </select>
            </div>
          </div>
          <div className="acciones">
            <button type="submit" className="boton">
              Buscar
            </button>
            {hayFiltros && (
              <button type="button" className="boton boton-secundario" onClick={limpiarFiltros}>
                Limpiar filtros
              </button>
            )}
          </div>
        </fieldset>
      </form>

      <Estado
        cargando={lista.cargando}
        error={lista.error}
        onReintentar={lista.recargar}
        vacio={lista.datos?.items.length === 0}
        textoVacio={hayFiltros ? 'Ningún usuario cumple con los filtros elegidos.' : 'Todavía no hay usuarios registrados.'}
      >
        {lista.datos && (
          <>
            <p aria-live="polite">
              {total} {total === 1 ? 'usuario' : 'usuarios'} en total
            </p>

            <div className="tabla-contenedor">
              <table className="tabla tabla-apilable">
                <caption className="solo-lectores">Usuarios registrados</caption>
                <thead>
                  <tr>
                    <th scope="col">Nombre</th>
                    <th scope="col">Correo</th>
                    <th scope="col">Rol</th>
                    <th scope="col">Estado</th>
                    <th scope="col">Alta</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {lista.datos.items.map((u) => {
                    const rolElegido = rolesElegidos[u.id] ?? u.rol
                    return (
                      <tr key={u.id}>
                        <td data-etiqueta="Nombre">
                          {/* span: en celular la celda es flex y así el nombre y "(tú)" quedan juntos */}
                          <span>
                            {u.nombre}
                            {u.id === yo?.id && <strong> (tú)</strong>}
                          </span>
                        </td>
                        <td data-etiqueta="Correo">{u.correo}</td>
                        <td data-etiqueta="Rol">
                          <div className="acciones-fila">
                            <select
                              value={rolElegido}
                              aria-label={`Rol de ${u.nombre}`}
                              onChange={(e) => setRolesElegidos((anteriores) => ({ ...anteriores, [u.id]: e.target.value as Rol }))}
                            >
                              {ROLES.map((r) => (
                                <option key={r.valor} value={r.valor}>
                                  {r.etiqueta}
                                </option>
                              ))}
                            </select>
                            <button
                              type="button"
                              className="boton boton-secundario"
                              disabled={ocupado || rolElegido === u.rol}
                              onClick={() => guardarRol(u)}
                              aria-label={`Guardar el rol de ${u.nombre}`}
                            >
                              Guardar
                            </button>
                          </div>
                        </td>
                        <td data-etiqueta="Estado">{u.activo ? 'Activa' : 'Suspendida'}</td>
                        <td data-etiqueta="Alta">{formatoFecha(u.creado_en)}</td>
                        <td data-etiqueta="Acciones">
                          <div className="acciones-fila">
                            {u.activo ? (
                              <button
                                type="button"
                                className="boton boton-peligro"
                                disabled={ocupado}
                                onClick={() => suspender(u)}
                                aria-label={`Suspender la cuenta de ${u.nombre}`}
                              >
                                Suspender
                              </button>
                            ) : (
                              <button
                                type="button"
                                className="boton boton-secundario"
                                disabled={ocupado}
                                onClick={() => void enviar(u, { activo: true }, 'Cuenta reactivada.')}
                                aria-label={`Reactivar la cuenta de ${u.nombre}`}
                              >
                                Reactivar
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <Paginacion etiqueta="Paginación de usuarios" pagina={pagina} total={total} onCambiar={setPagina} />
          </>
        )}
      </Estado>
    </section>
  )
}
