"""Lógica del catálogo de actividades extraescolares (HU-03.2)."""

from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, NoEncontrado
from app.core.paginacion import Paginacion
from app.models import Extraescolar, Grupo
from app.schemas.extraescolar import ExtraescolarActualizar, ExtraescolarCrear

Estado = Literal["activos", "bajas", "todos"]

NOMBRE_REPETIDO = "Ya existe una actividad con ese nombre"


def _obtener(db: Session, idextraescolar: int) -> Extraescolar:
    actividad = db.get(Extraescolar, idextraescolar)
    if actividad is None:
        raise NoEncontrado("La actividad no existe")
    return actividad


def _nombre_repetido(db: Session, nombre: str, excepto_id: int | None = None) -> bool:
    """¿Hay otra actividad con ese nombre? Compara sin distinguir mayúsculas ("Fútbol" = "fútbol")."""
    consulta = select(Extraescolar.idextraescolar).where(func.lower(Extraescolar.nombreextra) == nombre.lower())
    if excepto_id is not None:
        consulta = consulta.where(Extraescolar.idextraescolar != excepto_id)
    return db.scalar(consulta) is not None


def crear_actividad(db: Session, datos: ExtraescolarCrear) -> Extraescolar:
    if _nombre_repetido(db, datos.nombreextra):
        raise Conflicto(NOMBRE_REPETIDO)
    actividad = Extraescolar(**datos.model_dump())
    db.add(actividad)
    try:
        db.commit()
    except IntegrityError:
        # Dos capturas simultáneas del mismo nombre: la restricción unique de la BD lo detecta
        db.rollback()
        raise Conflicto(NOMBRE_REPETIDO) from None
    db.refresh(actividad)
    return actividad


def obtener_actividad(db: Session, idextraescolar: int) -> Extraescolar:
    return _obtener(db, idextraescolar)


def listar_actividades(
    db: Session, paginacion: Paginacion, q: str | None, estado: Estado
) -> tuple[list[Extraescolar], int]:
    """Devuelve (actividades de la página, total de la consulta). q busca por nombre."""
    consulta = select(Extraescolar)
    for palabra in (q or "").split():
        # icontains + autoescape: los símbolos % y _ que escriba la persona se buscan tal cual
        consulta = consulta.where(Extraescolar.nombreextra.icontains(palabra, autoescape=True))
    if estado == "activos":
        consulta = consulta.where(Extraescolar.activo.is_(True))
    elif estado == "bajas":
        consulta = consulta.where(Extraescolar.activo.is_(False))

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    orden = (Extraescolar.nombreextra, Extraescolar.idextraescolar)
    pagina = db.scalars(consulta.order_by(*orden).offset(paginacion.offset).limit(paginacion.size))
    return list(pagina), total


def actualizar_actividad(db: Session, idextraescolar: int, datos: ExtraescolarActualizar) -> Extraescolar:
    actividad = _obtener(db, idextraescolar)
    if _nombre_repetido(db, datos.nombreextra, excepto_id=actividad.idextraescolar):
        raise Conflicto(NOMBRE_REPETIDO)
    for campo, valor in datos.model_dump(exclude={"activo"}).items():
        setattr(actividad, campo, valor)
    if datos.activo is not None:  # desactivar (false) o reactivar (true) desde la edición
        actividad.activo = datos.activo
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflicto(NOMBRE_REPETIDO) from None
    db.refresh(actividad)
    return actividad


def eliminar_actividad(db: Session, idextraescolar: int) -> None:
    """Elimina de verdad, pero solo si no tiene grupos (RN-08). Si los tiene, hay que desactivarla."""
    actividad = _obtener(db, idextraescolar)
    cuenta = select(func.count()).select_from(Grupo).where(Grupo.idextraescolar == actividad.idextraescolar)
    grupos = db.scalar(cuenta) or 0
    if grupos:
        raise Conflicto(
            f"No se puede eliminar: la actividad tiene {grupos} grupo(s). "
            "Desactívala en su lugar"
        )
    db.delete(actividad)
    db.commit()
