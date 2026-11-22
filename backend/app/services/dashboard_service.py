"""Lógica del tablero de resumen (HU-07.1).

Todas las cifras salen de consultas agregadas (COUNT, GROUP BY, AVG): la base de datos cuenta,
Python no recorre filas para sumar.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.constantes import DESEMPENOS
from app.core.errores import NoEncontrado
from app.models import Alumno, AlumnoGrupo, Extraescolar, Grupo, Semestre


def _semestre_a_mostrar(db: Session, idsemestre: int | None) -> int | None:
    """Devuelve el id del semestre pedido, o el más reciente si no se envió (mayor año y luego mayor mes).

    Devuelve None si no hay ningún semestre en la base. Lanza 404 si el pedido no existe."""
    if idsemestre is not None:
        if db.get(Semestre, idsemestre) is None:
            raise NoEncontrado("El semestre no existe")
        return idsemestre
    return db.scalar(select(Semestre.idsemestre).order_by(Semestre.anio.desc(), Semestre.mesinicio.desc()).limit(1))


def obtener_resumen(db: Session, idsemestre: int | None) -> dict:
    idsemestre = _semestre_a_mostrar(db, idsemestre)

    # Los alumnos activos son globales (un alumno no pertenece a un semestre)
    alumnos_activos = db.scalar(select(func.count()).select_from(Alumno).where(Alumno.activo.is_(True)))

    if idsemestre is None:
        # Base sin semestres: todo en cero, sin errores ni divisiones entre cero
        return {
            "totales": {"alumnos_activos": alumnos_activos, "grupos": 0, "inscripciones": 0},
            "inscritos_por_actividad": [],
            "distribucion_desempenio": [{"desempenio": d, "total": 0} for d in DESEMPENOS],
            "promedio_calificacion": None,
        }

    grupos = db.scalar(select(func.count()).select_from(Grupo).where(Grupo.idsemestre == idsemestre))

    # Inscripciones del semestre: alumno_grupo unido con grupo, filtrado por semestre
    inscripciones = db.scalar(
        select(func.count())
        .select_from(AlumnoGrupo)
        .join(Grupo, Grupo.idgrupo == AlumnoGrupo.idgrupo)
        .where(Grupo.idsemestre == idsemestre)
    )

    # Inscritos por actividad (GROUP BY nombre de la actividad); la más concurrida primero
    filas_actividad = db.execute(
        select(Extraescolar.nombreextra, func.count())
        .select_from(AlumnoGrupo)
        .join(Grupo, Grupo.idgrupo == AlumnoGrupo.idgrupo)
        .join(Extraescolar, Extraescolar.idextraescolar == Grupo.idextraescolar)
        .where(Grupo.idsemestre == idsemestre)
        .group_by(Extraescolar.nombreextra)
        .order_by(func.count().desc(), Extraescolar.nombreextra)
    ).all()

    # Distribución del desempeño y promedio: solo cuentan las inscripciones ya calificadas
    filas_desempenio = db.execute(
        select(AlumnoGrupo.desempenio, func.count())
        .join(Grupo, Grupo.idgrupo == AlumnoGrupo.idgrupo)
        .where(Grupo.idsemestre == idsemestre, AlumnoGrupo.calificacion.is_not(None))
        .group_by(AlumnoGrupo.desempenio)
    ).all()
    por_desempenio = dict(filas_desempenio)

    # AVG ignora los NULL; si no hay calificaciones devuelve NULL (None)
    promedio = db.scalar(
        select(func.avg(AlumnoGrupo.calificacion))
        .join(Grupo, Grupo.idgrupo == AlumnoGrupo.idgrupo)
        .where(Grupo.idsemestre == idsemestre)
    )

    return {
        "totales": {"alumnos_activos": alumnos_activos, "grupos": grupos, "inscripciones": inscripciones},
        "inscritos_por_actividad": [{"actividad": nombre, "total": total} for nombre, total in filas_actividad],
        # Siempre las cinco categorías, en orden de mejor a peor, aunque alguna tenga 0
        "distribucion_desempenio": [{"desempenio": d, "total": por_desempenio.get(d, 0)} for d in DESEMPENOS],
        "promedio_calificacion": None if promedio is None else round(float(promedio), 2),
    }
