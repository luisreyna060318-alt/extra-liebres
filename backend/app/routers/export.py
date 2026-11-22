from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.core.deps import SesionDB, require_role
from app.services import consulta_service, export_service

# Solo el administrador exporta: 401 si no hay sesión y 403 si la persona es capturista
router = APIRouter(
    prefix="/api/export",
    tags=["Exportar"],
    dependencies=[Depends(require_role("administrador"))],
    responses={401: {"description": "Sin sesión"}, 403: {"description": "Solo administradores"}},
)

Actividad = Annotated[int | None, Query(description="id de la actividad")]
Semestre = Annotated[int | None, Query(description="id del semestre")]


@router.get("/inscritos.csv", summary="Exportar los inscritos en CSV")
def inscritos_csv(db: SesionDB, extraescolar: Actividad = None, semestre: Semestre = None):
    """Todos los inscritos que cumplen los filtros, sin paginar, en un CSV que abre en una hoja de cálculo."""
    filas = consulta_service.todos(db, extraescolar, semestre)
    return Response(
        content=export_service.a_csv(filas).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="inscritos.csv"'},
    )


@router.get("/inscritos.xml", summary="Exportar los inscritos en XML")
def inscritos_xml(db: SesionDB, extraescolar: Actividad = None, semestre: Semestre = None):
    """Los mismos datos en XML bien formado: `<inscritos total="N">` con un `<inscrito>` por renglón."""
    filas = consulta_service.todos(db, extraescolar, semestre)
    return Response(
        content=export_service.a_xml(filas),
        media_type="application/xml",
        headers={"Content-Disposition": 'attachment; filename="inscritos.xml"'},
    )
