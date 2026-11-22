from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import SesionDB, require_role
from app.core.paginacion import Paginacion
from app.schemas.comun import Pagina
from app.schemas.usuario import UsuarioActualizar, UsuarioSalida
from app.services import usuario_service

# Todo este router es solo para administradores. La comprobación se hace en el servidor:
# 401 si no hay sesión y 403 si la persona no es administrador.
router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios (administrador)"],
    dependencies=[Depends(require_role("administrador"))],
    responses={401: {"description": "Sin sesión"}, 403: {"description": "Solo administradores"}},
)


@router.get("", response_model=Pagina[UsuarioSalida], summary="Listar usuarios")
def listar(
    db: SesionDB,
    paginacion: Annotated[Paginacion, Depends()],
    q: Annotated[str | None, Query(description="Busca en nombre o correo")] = None,
    rol: Annotated[str | None, Query(description="administrador o capturista")] = None,
    activo: Annotated[bool | None, Query(description="true = activas, false = suspendidas")] = None,
):
    """Lista las cuentas con búsqueda, filtros y paginación (10 por página por defecto)."""
    usuarios, total = usuario_service.listar_usuarios(db, paginacion, q, rol, activo)
    return Pagina[UsuarioSalida](items=usuarios, total=total, page=paginacion.page, size=paginacion.size)


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioSalida,
    summary="Cambiar el rol o suspender una cuenta",
    responses={
        404: {"description": "El usuario no existe"},
        409: {"description": "Dejaría al sistema sin administradores"},
    },
)
def actualizar(usuario_id: int, datos: UsuarioActualizar, db: SesionDB):
    """Cambia el rol y/o suspende (`activo=false`) o reactiva (`activo=true`) una cuenta.

    No se puede quitar el rol ni suspender al **último administrador activo**.
    Los cambios se aplican en la siguiente petición de esa persona."""
    return usuario_service.actualizar_usuario(db, usuario_id, datos)
