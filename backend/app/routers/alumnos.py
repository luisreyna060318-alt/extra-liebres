from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.deps import SesionDB, get_current_user
from app.core.paginacion import Paginacion
from app.schemas.alumno import (
    AlumnoActualizar,
    AlumnoCrear,
    AlumnoSalida,
    HistorialItem,
    OpcionesAlumno,
)
from app.schemas.comun import Pagina
from app.services import alumno_service
from app.services.alumno_service import Estado

# Todas las rutas de alumnos exigen sesión (administrador o capturista): 401 si no hay
router = APIRouter(
    prefix="/api/alumnos",
    tags=["Alumnos"],
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)

NO_EXISTE = {404: {"description": "El alumno no existe"}}


@router.get("", response_model=Pagina[AlumnoSalida], summary="Buscar y listar alumnos")
def listar(
    db: SesionDB,
    paginacion: Annotated[Paginacion, Depends()],
    q: Annotated[str | None, Query(description="Texto a buscar en nombre, apellidos o número de control")] = None,
    carrera: Annotated[str | None, Query(description="Carrera exacta")] = None,
    campus: Annotated[str | None, Query(description="Campus exacto")] = None,
    estado: Annotated[Estado, Query(description="activos (por defecto), bajas o todos")] = "activos",
):
    """Lista alumnos con búsqueda, filtros y paginación (10 por página por defecto).

    Los alumnos dados de baja **no aparecen por defecto**: usa `estado=bajas` o `estado=todos`."""
    alumnos, total = alumno_service.listar_alumnos(db, paginacion, q, carrera, campus, estado)
    return Pagina[AlumnoSalida](items=alumnos, total=total, page=paginacion.page, size=paginacion.size)


# Esta ruta va ANTES de "/{nocontrol}", si no FastAPI creería que "opciones" es un número de control
@router.get("/opciones", response_model=OpcionesAlumno, summary="Carreras (lista fija) y campus existentes")
def opciones(db: SesionDB):
    """Las carreras que se pueden elegir (lista fija) y los campus que ya existen.

    Sirve para llenar los filtros y el formulario."""
    return alumno_service.opciones_alumnos(db)


@router.post(
    "",
    response_model=AlumnoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Dar de alta un alumno",
    responses={409: {"description": "Ya existe un alumno con ese número de control"}},
)
def crear(datos: AlumnoCrear, db: SesionDB):
    return alumno_service.crear_alumno(db, datos)


@router.get("/{nocontrol}", response_model=AlumnoSalida, summary="Ver un alumno", responses=NO_EXISTE)
def obtener(nocontrol: str, db: SesionDB):
    return alumno_service.obtener_alumno(db, nocontrol)


@router.put("/{nocontrol}", response_model=AlumnoSalida, summary="Editar un alumno", responses=NO_EXISTE)
def actualizar(nocontrol: str, datos: AlumnoActualizar, db: SesionDB):
    """Reemplaza los datos del alumno. El número de control no cambia.

    Con `activo=true` se reactiva a un alumno dado de baja."""
    return alumno_service.actualizar_alumno(db, nocontrol, datos)


@router.delete(
    "/{nocontrol}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dar de baja a un alumno",
    responses=NO_EXISTE,
)
def dar_de_baja(nocontrol: str, db: SesionDB):
    """**Baja lógica**: el alumno queda inactivo pero no se borra, así su historial se conserva."""
    alumno_service.dar_de_baja(db, nocontrol)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{nocontrol}/historial",
    response_model=list[HistorialItem],
    summary="Historial de actividades del alumno",
    responses=NO_EXISTE,
)
def historial(nocontrol: str, db: SesionDB):
    """Actividades que cursó, con semestre, promotor, calificación y desempeño (del más reciente al más antiguo).

    Si el alumno no tiene inscripciones devuelve una lista vacía."""
    return alumno_service.historial_alumno(db, nocontrol)
