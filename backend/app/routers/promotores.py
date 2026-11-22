from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.deps import SesionDB, get_current_user, require_role
from app.core.paginacion import Paginacion
from app.schemas.comun import Pagina
from app.schemas.promotor import PromotorActualizar, PromotorCrear, PromotorSalida
from app.services import promotor_service
from app.services.promotor_service import Estado

# Leer (GET): cualquier usuario con sesión. Escribir (POST, PUT, DELETE): solo administrador (RN-06).
# Por eso cada ruta declara su dependencia y no el router completo.
router = APIRouter(
    prefix="/api/promotores",
    tags=["Promotores"],
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)

SOLO_ADMIN = Depends(require_role("administrador"))
NO_EXISTE = {404: {"description": "El promotor no existe"}}
PERMISO = {403: {"description": "Solo administradores"}}


@router.get(
    "",
    response_model=Pagina[PromotorSalida],
    summary="Buscar y listar promotores",
    dependencies=[Depends(get_current_user)],
)
def listar(
    db: SesionDB,
    paginacion: Annotated[Paginacion, Depends()],
    q: Annotated[str | None, Query(description="Texto a buscar en nombre, apellidos o RFC")] = None,
    estado: Annotated[Estado, Query(description="activos (por defecto), bajas o todos")] = "activos",
):
    """Lista promotores con búsqueda y paginación (10 por página por defecto).

    Los promotores desactivados **no aparecen por defecto**: usa `estado=bajas` o `estado=todos`."""
    promotores, total = promotor_service.listar_promotores(db, paginacion, q, estado)
    return Pagina[PromotorSalida](items=promotores, total=total, page=paginacion.page, size=paginacion.size)


@router.post(
    "",
    response_model=PromotorSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Dar de alta un promotor",
    dependencies=[SOLO_ADMIN],
    responses={**PERMISO, 409: {"description": "Ya existe un promotor con ese RFC"}},
)
def crear(datos: PromotorCrear, db: SesionDB):
    """El RFC se guarda en mayúsculas y debe tener 12 o 13 caracteres con el formato oficial."""
    return promotor_service.crear_promotor(db, datos)


@router.get(
    "/{rfc}",
    response_model=PromotorSalida,
    summary="Ver un promotor",
    dependencies=[Depends(get_current_user)],
    responses=NO_EXISTE,
)
def obtener(rfc: str, db: SesionDB):
    return promotor_service.obtener_promotor(db, rfc)


@router.put(
    "/{rfc}",
    response_model=PromotorSalida,
    summary="Editar, desactivar o reactivar un promotor",
    dependencies=[SOLO_ADMIN],
    responses={**NO_EXISTE, **PERMISO},
)
def actualizar(rfc: str, datos: PromotorActualizar, db: SesionDB):
    """Reemplaza los datos del promotor. El RFC no cambia.

    Con `activo=false` se desactiva (deja de ofrecerse al crear grupos) y con `activo=true` se reactiva."""
    return promotor_service.actualizar_promotor(db, rfc, datos)


@router.delete(
    "/{rfc}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un promotor",
    dependencies=[SOLO_ADMIN],
    responses={
        **NO_EXISTE,
        **PERMISO,
        409: {"description": "Tiene grupos asociados: solo se puede desactivar"},
    },
)
def eliminar(rfc: str, db: SesionDB):
    """Elimina al promotor **solo si no tiene grupos** (RN-08). Si tiene, responde 409: desactívalo con PUT."""
    promotor_service.eliminar_promotor(db, rfc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
