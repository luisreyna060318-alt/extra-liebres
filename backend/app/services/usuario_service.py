"""Lógica de administración de usuarios (HU-01.4)."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, NoEncontrado
from app.core.paginacion import Paginacion
from app.models import Usuario
from app.schemas.usuario import UsuarioActualizar


def listar_usuarios(
    db: Session, paginacion: Paginacion, q: str | None, rol: str | None, activo: bool | None
) -> tuple[list[Usuario], int]:
    """Devuelve (usuarios de la página, total de la consulta). Todos los filtros se combinan con AND."""
    consulta = select(Usuario)
    if q:
        patron = f"%{q.strip()}%"
        consulta = consulta.where(or_(Usuario.nombre.ilike(patron), Usuario.correo.ilike(patron)))
    if rol:
        consulta = consulta.where(Usuario.rol == rol)
    if activo is not None:
        consulta = consulta.where(Usuario.activo == activo)

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    pagina = db.scalars(consulta.order_by(Usuario.nombre, Usuario.id).offset(paginacion.offset).limit(paginacion.size))
    return list(pagina), total


def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioActualizar) -> Usuario:
    """Cambia el rol y/o suspende o reactiva una cuenta, sin dejar al sistema sin administradores (RN-06)."""
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise NoEncontrado("El usuario no existe")

    nuevo_rol = datos.rol if datos.rol is not None else usuario.rol
    nuevo_activo = datos.activo if datos.activo is not None else usuario.activo

    deja_de_ser_admin_activo = usuario.rol == "administrador" and usuario.activo and (
        nuevo_rol != "administrador" or not nuevo_activo
    )
    if deja_de_ser_admin_activo:
        administradores_activos = db.scalar(
            select(func.count()).select_from(Usuario).where(Usuario.rol == "administrador", Usuario.activo.is_(True))
        )
        if administradores_activos <= 1:
            raise Conflicto("Debe existir al menos un administrador activo")

    usuario.rol = nuevo_rol
    usuario.activo = nuevo_activo
    db.commit()
    db.refresh(usuario)
    return usuario
