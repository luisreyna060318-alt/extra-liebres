"""Lógica del catálogo de semestres (HU-03.3)."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, NoEncontrado
from app.core.paginacion import Paginacion
from app.models import Grupo, Semestre
from app.schemas.semestre import SemestreActualizar, SemestreCrear

REPETIDO = "Ya existe un semestre con ese año y mes de inicio"


def _obtener(db: Session, idsemestre: int) -> Semestre:
    semestre = db.get(Semestre, idsemestre)
    if semestre is None:
        raise NoEncontrado("El semestre no existe")
    return semestre


def _repetido(db: Session, anio: int, mesinicio: int, excepto_id: int | None = None) -> bool:
    """¿Hay otro semestre que empiece el mismo mes del mismo año?"""
    consulta = select(Semestre.idsemestre).where(Semestre.anio == anio, Semestre.mesinicio == mesinicio)
    if excepto_id is not None:
        consulta = consulta.where(Semestre.idsemestre != excepto_id)
    return db.scalar(consulta) is not None


def crear_semestre(db: Session, datos: SemestreCrear) -> Semestre:
    if _repetido(db, datos.anio, datos.mesinicio):
        raise Conflicto(REPETIDO)
    semestre = Semestre(**datos.model_dump())
    db.add(semestre)
    try:
        db.commit()
    except IntegrityError:
        # Dos capturas simultáneas: la restricción unique (anio, mesinicio) de la BD lo detecta
        db.rollback()
        raise Conflicto(REPETIDO) from None
    db.refresh(semestre)
    return semestre


def obtener_semestre(db: Session, idsemestre: int) -> Semestre:
    return _obtener(db, idsemestre)


def listar_semestres(db: Session, paginacion: Paginacion) -> tuple[list[Semestre], int]:
    """Devuelve (semestres de la página, total). El más reciente va primero."""
    total = db.scalar(select(func.count()).select_from(Semestre)) or 0
    consulta = select(Semestre).order_by(Semestre.anio.desc(), Semestre.mesinicio.desc())
    pagina = db.scalars(consulta.offset(paginacion.offset).limit(paginacion.size))
    return list(pagina), total


def actualizar_semestre(db: Session, idsemestre: int, datos: SemestreActualizar) -> Semestre:
    semestre = _obtener(db, idsemestre)
    if _repetido(db, datos.anio, datos.mesinicio, excepto_id=semestre.idsemestre):
        raise Conflicto(REPETIDO)
    for campo, valor in datos.model_dump().items():
        setattr(semestre, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflicto(REPETIDO) from None
    db.refresh(semestre)
    return semestre


def eliminar_semestre(db: Session, idsemestre: int) -> None:
    """Elimina de verdad, pero solo si no tiene grupos (RN-08). Los semestres no se desactivan."""
    semestre = _obtener(db, idsemestre)
    grupos = db.scalar(select(func.count()).select_from(Grupo).where(Grupo.idsemestre == semestre.idsemestre)) or 0
    if grupos:
        raise Conflicto(f"No se puede eliminar: el semestre tiene {grupos} grupo(s) asociado(s)")
    db.delete(semestre)
    db.commit()
