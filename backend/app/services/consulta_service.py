"""Consultas transversales (HU-06.1): alumnos inscritos por actividad y/o semestre."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.paginacion import Paginacion
from app.models import Alumno, AlumnoGrupo, Extraescolar, Grupo, Semestre
from app.schemas.consulta import InscritoConsulta
from app.services.grupo_service import _nombre_promotor, _nombre_semestre
from app.services.inscripcion_service import nombre_alumno


def _a_salida(inscripcion: AlumnoGrupo) -> InscritoConsulta:
    alumno, grupo = inscripcion.alumno, inscripcion.grupo
    return InscritoConsulta(
        nocontrol=alumno.nocontrol,
        alumno=nombre_alumno(alumno),
        carrera=alumno.carrera,
        idgrupo=grupo.idgrupo,
        idextraescolar=grupo.idextraescolar,
        actividad=grupo.extraescolar.nombreextra,
        idsemestre=grupo.idsemestre,
        semestre=_nombre_semestre(grupo.semestre),
        promotor=_nombre_promotor(grupo.promotor),
        calificacion=inscripcion.calificacion,
        desempenio=inscripcion.desempenio,
    )


def _filtrada(extraescolar: int | None, semestre: int | None):
    """Consulta base con los filtros opcionales, que se combinan con AND."""
    consulta = select(AlumnoGrupo).join(AlumnoGrupo.grupo)
    if extraescolar is not None:
        consulta = consulta.where(Grupo.idextraescolar == extraescolar)
    if semestre is not None:
        consulta = consulta.where(Grupo.idsemestre == semestre)
    return consulta


def _con_datos_y_orden(consulta):
    """Agrega los datos que muestra cada renglón y el orden: semestre más reciente primero; dentro de él,
    por actividad, grupo y apellidos del alumno."""
    orden = (
        Semestre.anio.desc(), Semestre.mesinicio.desc(), Extraescolar.nombreextra, Grupo.idgrupo,
        Alumno.apaterno, Alumno.amaterno, Alumno.nombre, Alumno.nocontrol,
    )  # fmt: skip
    return (
        consulta.join(Grupo.semestre)
        .join(Grupo.extraescolar)
        .join(AlumnoGrupo.alumno)
        .options(
            joinedload(AlumnoGrupo.alumno),
            joinedload(AlumnoGrupo.grupo).joinedload(Grupo.semestre),
            joinedload(AlumnoGrupo.grupo).joinedload(Grupo.extraescolar),
            joinedload(AlumnoGrupo.grupo).joinedload(Grupo.promotor),
        )
        .order_by(*orden)
    )


def inscritos(
    db: Session, paginacion: Paginacion, extraescolar: int | None, semestre: int | None
) -> tuple[list[InscritoConsulta], int]:
    """Devuelve (renglones de la página, total)."""
    consulta = _filtrada(extraescolar, semestre)
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    pagina = db.scalars(_con_datos_y_orden(consulta).offset(paginacion.offset).limit(paginacion.size))
    return [_a_salida(i) for i in pagina], total


def todos(db: Session, extraescolar: int | None, semestre: int | None) -> list[InscritoConsulta]:
    """Todos los renglones, sin paginar: es lo que se exporta (HU-07.2)."""
    return [_a_salida(i) for i in db.scalars(_con_datos_y_orden(_filtrada(extraescolar, semestre)))]
