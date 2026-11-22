from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.constantes import ROLES_DE_PERSONAL
from app.core.deps import SesionDB, require_role
from app.schemas.inscripcion import EvaluacionDatos, InscripcionCrear, InscritoSalida
from app.services import inscripcion_service

# Las inscripciones cuelgan de un grupo. Son para administrador y capturista: 401 sin sesión, 403 si es lector
router = APIRouter(
    prefix="/api/grupos/{idgrupo}",
    tags=["Inscripciones"],
    dependencies=[Depends(require_role(*ROLES_DE_PERSONAL))],
    responses={
        401: {"description": "Sin sesión o sesión expirada"},
        403: {"description": "Los lectores no tienen acceso"},
    },
)

NO_EXISTE = {404: {"description": "El grupo no existe o el alumno no está inscrito"}}


@router.get(
    "/inscritos",
    response_model=list[InscritoSalida],
    summary="Alumnos inscritos en el grupo",
    responses={404: {"description": "El grupo no existe"}},
)
def listar(idgrupo: int, db: SesionDB):
    """Lista los inscritos con su calificación y desempeño (nulos si aún no se evalúan)."""
    return inscripcion_service.listar_inscritos(db, idgrupo)


@router.post(
    "/inscripciones",
    response_model=InscritoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Inscribir un alumno al grupo",
    responses={
        404: {"description": "El grupo o el alumno no existe"},
        409: {"description": "El alumno está dado de baja o ya está inscrito en el grupo"},
    },
)
def inscribir(idgrupo: int, datos: InscripcionCrear, db: SesionDB):
    return inscripcion_service.inscribir(db, idgrupo, datos.nocontrol)


@router.put(
    "/inscripciones/{nocontrol}",
    response_model=InscritoSalida,
    summary="Evaluar (o corregir la calificación de) un alumno",
    responses=NO_EXISTE,
)
def evaluar(idgrupo: int, nocontrol: str, datos: EvaluacionDatos, db: SesionDB):
    """Recibe solo `calificacion` (entero de 0 a 100). El **desempeño lo calcula el servidor**:
    si el cuerpo trae `desempenio` u otro campo, se rechaza con 422."""
    return inscripcion_service.evaluar(db, idgrupo, nocontrol, datos.calificacion)


@router.delete(
    "/inscripciones/{nocontrol}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar a un alumno del grupo",
    responses={**NO_EXISTE, 409: {"description": "Ya tiene calificación y falta confirmar"}},
)
def eliminar(
    idgrupo: int,
    nocontrol: str,
    db: SesionDB,
    confirmar: Annotated[bool, Query(description="Obligatorio si el alumno ya tiene calificación")] = False,
):
    inscripcion_service.eliminar_inscripcion(db, idgrupo, nocontrol, confirmar)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
