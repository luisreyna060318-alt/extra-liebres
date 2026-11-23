from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.constantes import ROLES_DE_PERSONAL
from app.core.deps import SesionDB, get_current_user, require_role
from app.core.paginacion import Paginacion
from app.schemas.comun import Pagina
from app.schemas.grupo import GrupoActualizar, GrupoCrear, GrupoSalida
from app.services import grupo_service

# Ver grupos exige sesión (cualquier rol, también el lector): 401 si no hay.
# Crear, editar y eliminar es solo de administrador y capturista: 403 si es lector
router = APIRouter(
    prefix="/api/grupos",
    tags=["Grupos"],
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)

SOLO_PERSONAL = Depends(require_role(*ROLES_DE_PERSONAL))
# Se documenta en /docs el 403 que responde SOLO_PERSONAL cuando la persona es lector
PERMISO = {403: {"description": "Los lectores no pueden crear, editar ni eliminar grupos"}}
NO_EXISTE = {404: {"description": "El grupo no existe"}}
CRUCE = {409: {"description": "Cruce de horario con otro grupo del mismo promotor o lugar"}}
# 422 de negocio (además de los de Pydantic): actividad deportiva con un lugar fuera de la lista de instalaciones
LUGAR = {422: {"description": "Datos inválidos, o lugar que no es una instalación deportiva permitida"}}


@router.get("", response_model=Pagina[GrupoSalida], summary="Listar y filtrar grupos")
def listar(
    db: SesionDB,
    paginacion: Annotated[Paginacion, Depends()],
    semestre: Annotated[int | None, Query(description="id del semestre")] = None,
    extraescolar: Annotated[int | None, Query(description="id de la actividad")] = None,
    promotor: Annotated[str | None, Query(description="RFC del promotor")] = None,
    dia: Annotated[str | None, Query(description="lunes, martes, miercoles, jueves, viernes o sabado")] = None,
):
    """Lista grupos con filtros (se combinan todos) y paginación (10 por página por defecto)."""
    grupos, total = grupo_service.listar_grupos(db, paginacion, semestre, extraescolar, promotor, dia)
    return Pagina[GrupoSalida](items=grupos, total=total, page=paginacion.page, size=paginacion.size)


@router.post(
    "",
    response_model=GrupoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un grupo",
    dependencies=[SOLO_PERSONAL],
    responses={**PERMISO, 404: {"description": "El semestre, la actividad o el promotor no existe"}, **CRUCE, **LUGAR},
)
def crear(datos: GrupoCrear, db: SesionDB):
    """Crea el grupo si no se cruza con otro del mismo promotor o lugar (mismo semestre y día)."""
    return grupo_service.crear_grupo(db, datos)


@router.get("/{idgrupo}", response_model=GrupoSalida, summary="Ver un grupo", responses=NO_EXISTE)
def obtener(idgrupo: int, db: SesionDB):
    return grupo_service.obtener_grupo(db, idgrupo)


@router.put(
    "/{idgrupo}",
    response_model=GrupoSalida,
    summary="Editar un grupo",
    dependencies=[SOLO_PERSONAL],
    responses={**PERMISO, **NO_EXISTE, **CRUCE, **LUGAR},
)
def actualizar(idgrupo: int, datos: GrupoActualizar, db: SesionDB):
    """Reemplaza los datos del grupo y vuelve a validar los cruces (sin compararlo consigo mismo)."""
    return grupo_service.actualizar_grupo(db, idgrupo, datos)


@router.delete(
    "/{idgrupo}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un grupo",
    dependencies=[SOLO_PERSONAL],
    responses={**PERMISO, **NO_EXISTE, 409: {"description": "El grupo tiene alumnos inscritos"}},
)
def eliminar(idgrupo: int, db: SesionDB):
    """Solo se puede eliminar un grupo **sin alumnos inscritos**."""
    grupo_service.eliminar_grupo(db, idgrupo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
