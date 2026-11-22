from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.deps import SesionDB, get_current_user, require_role
from app.core.paginacion import Paginacion
from app.schemas.comun import Pagina
from app.schemas.semestre import SemestreActualizar, SemestreCrear, SemestreSalida
from app.services import semestre_service

# Leer (GET): cualquier usuario con sesión. Escribir (POST, PUT, DELETE): solo administrador (RN-06).
router = APIRouter(
    prefix="/api/semestres",
    tags=["Semestres"],
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)

SOLO_ADMIN = Depends(require_role("administrador"))
NO_EXISTE = {404: {"description": "El semestre no existe"}}
PERMISO = {403: {"description": "Solo administradores"}}
REPETIDO = {409: {"description": "Ya existe un semestre con ese año y mes de inicio"}}


@router.get(
    "",
    response_model=Pagina[SemestreSalida],
    summary="Listar semestres",
    dependencies=[Depends(get_current_user)],
)
def listar(db: SesionDB, paginacion: Annotated[Paginacion, Depends()]):
    """Lista los semestres, el más reciente primero, con paginación (10 por página por defecto)."""
    semestres, total = semestre_service.listar_semestres(db, paginacion)
    return Pagina[SemestreSalida](items=semestres, total=total, page=paginacion.page, size=paginacion.size)


@router.post(
    "",
    response_model=SemestreSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un semestre",
    dependencies=[SOLO_ADMIN],
    responses={**PERMISO, **REPETIDO},
)
def crear(datos: SemestreCrear, db: SesionDB):
    return semestre_service.crear_semestre(db, datos)


@router.get(
    "/{idsemestre}",
    response_model=SemestreSalida,
    summary="Ver un semestre",
    dependencies=[Depends(get_current_user)],
    responses=NO_EXISTE,
)
def obtener(idsemestre: int, db: SesionDB):
    return semestre_service.obtener_semestre(db, idsemestre)


@router.put(
    "/{idsemestre}",
    response_model=SemestreSalida,
    summary="Editar un semestre",
    dependencies=[SOLO_ADMIN],
    responses={**NO_EXISTE, **PERMISO, **REPETIDO},
)
def actualizar(idsemestre: int, datos: SemestreActualizar, db: SesionDB):
    return semestre_service.actualizar_semestre(db, idsemestre, datos)


@router.delete(
    "/{idsemestre}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un semestre",
    dependencies=[SOLO_ADMIN],
    responses={**NO_EXISTE, **PERMISO, 409: {"description": "Tiene grupos asociados"}},
)
def eliminar(idsemestre: int, db: SesionDB):
    """Elimina el semestre **solo si no tiene grupos** (RN-08). Si tiene, responde 409."""
    semestre_service.eliminar_semestre(db, idsemestre)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
