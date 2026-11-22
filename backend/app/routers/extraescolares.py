from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.deps import SesionDB, get_current_user, require_role
from app.core.paginacion import Paginacion
from app.schemas.comun import Pagina
from app.schemas.extraescolar import ExtraescolarActualizar, ExtraescolarCrear, ExtraescolarSalida
from app.services import extraescolar_service
from app.services.extraescolar_service import Estado

# Leer (GET): cualquier usuario con sesión. Escribir (POST, PUT, DELETE): solo administrador (RN-06).
router = APIRouter(
    prefix="/api/extraescolares",
    tags=["Actividades extraescolares"],
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)

SOLO_ADMIN = Depends(require_role("administrador"))
NO_EXISTE = {404: {"description": "La actividad no existe"}}
PERMISO = {403: {"description": "Solo administradores"}}


@router.get(
    "",
    response_model=Pagina[ExtraescolarSalida],
    summary="Buscar y listar actividades",
    dependencies=[Depends(get_current_user)],
)
def listar(
    db: SesionDB,
    paginacion: Annotated[Paginacion, Depends()],
    q: Annotated[str | None, Query(description="Texto a buscar en el nombre de la actividad")] = None,
    estado: Annotated[Estado, Query(description="activos (por defecto), bajas o todos")] = "activos",
):
    """Lista actividades con búsqueda por nombre y paginación (10 por página por defecto).

    Las actividades desactivadas **no aparecen por defecto**: usa `estado=bajas` o `estado=todos`."""
    actividades, total = extraescolar_service.listar_actividades(db, paginacion, q, estado)
    return Pagina[ExtraescolarSalida](items=actividades, total=total, page=paginacion.page, size=paginacion.size)


@router.post(
    "",
    response_model=ExtraescolarSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una actividad",
    dependencies=[SOLO_ADMIN],
    responses={**PERMISO, 409: {"description": "Ya existe una actividad con ese nombre"}},
)
def crear(datos: ExtraescolarCrear, db: SesionDB):
    """El tipo es `deportiva`, `cultural` o `civica`. Si es al aire libre se mostrará el clima."""
    return extraescolar_service.crear_actividad(db, datos)


@router.get(
    "/{idextraescolar}",
    response_model=ExtraescolarSalida,
    summary="Ver una actividad",
    dependencies=[Depends(get_current_user)],
    responses=NO_EXISTE,
)
def obtener(idextraescolar: int, db: SesionDB):
    return extraescolar_service.obtener_actividad(db, idextraescolar)


@router.put(
    "/{idextraescolar}",
    response_model=ExtraescolarSalida,
    summary="Editar, desactivar o reactivar una actividad",
    dependencies=[SOLO_ADMIN],
    responses={**NO_EXISTE, **PERMISO, 409: {"description": "Ya existe otra actividad con ese nombre"}},
)
def actualizar(idextraescolar: int, datos: ExtraescolarActualizar, db: SesionDB):
    """Reemplaza los datos de la actividad.

    Con `activo=false` se desactiva (deja de ofrecerse al crear grupos) y con `activo=true` se reactiva."""
    return extraescolar_service.actualizar_actividad(db, idextraescolar, datos)


@router.delete(
    "/{idextraescolar}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una actividad",
    dependencies=[SOLO_ADMIN],
    responses={
        **NO_EXISTE,
        **PERMISO,
        409: {"description": "Tiene grupos asociados: solo se puede desactivar"},
    },
)
def eliminar(idextraescolar: int, db: SesionDB):
    """Elimina la actividad **solo si no tiene grupos** (RN-08). Si tiene, responde 409: desactívala con PUT."""
    extraescolar_service.eliminar_actividad(db, idextraescolar)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
