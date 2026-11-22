"""Lógica del catálogo de promotores (HU-03.1). Aquí viven las reglas; el router solo recibe y responde."""

from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, NoEncontrado
from app.core.paginacion import Paginacion
from app.models import Grupo, Promotor
from app.schemas.promotor import PromotorActualizar, PromotorCrear, normalizar_rfc

Estado = Literal["activos", "bajas", "todos"]


def _obtener(db: Session, rfc: str) -> Promotor:
    promotor = db.get(Promotor, normalizar_rfc(rfc))
    if promotor is None:
        raise NoEncontrado("El promotor no existe")
    return promotor


def crear_promotor(db: Session, datos: PromotorCrear) -> Promotor:
    if db.get(Promotor, datos.rfc):
        raise Conflicto("Ya existe un promotor con ese RFC")
    promotor = Promotor(**datos.model_dump())
    db.add(promotor)
    try:
        db.commit()
    except IntegrityError:
        # Dos capturas simultáneas del mismo RFC: la llave primaria de la BD lo detecta
        db.rollback()
        raise Conflicto("Ya existe un promotor con ese RFC") from None
    db.refresh(promotor)
    return promotor


def obtener_promotor(db: Session, rfc: str) -> Promotor:
    return _obtener(db, rfc)


def listar_promotores(
    db: Session, paginacion: Paginacion, q: str | None, estado: Estado
) -> tuple[list[Promotor], int]:
    """Devuelve (promotores de la página, total de la consulta).

    La búsqueda q parte el texto en palabras: cada palabra debe aparecer en el nombre, algún apellido o el RFC.
    """
    consulta = select(Promotor)
    for palabra in (q or "").split():
        # icontains + autoescape: los símbolos % y _ que escriba la persona se buscan tal cual, no como comodines
        consulta = consulta.where(
            or_(
                Promotor.nombre.icontains(palabra, autoescape=True),
                Promotor.apaterno.icontains(palabra, autoescape=True),
                Promotor.amaterno.icontains(palabra, autoescape=True),
                Promotor.rfc.icontains(palabra, autoescape=True),
            )
        )
    if estado == "activos":
        consulta = consulta.where(Promotor.activo.is_(True))
    elif estado == "bajas":
        consulta = consulta.where(Promotor.activo.is_(False))

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    orden = (Promotor.apaterno, Promotor.amaterno, Promotor.nombre, Promotor.rfc)
    pagina = db.scalars(consulta.order_by(*orden).offset(paginacion.offset).limit(paginacion.size))
    return list(pagina), total


def actualizar_promotor(db: Session, rfc: str, datos: PromotorActualizar) -> Promotor:
    promotor = _obtener(db, rfc)
    for campo, valor in datos.model_dump(exclude={"activo"}).items():
        setattr(promotor, campo, valor)
    if datos.activo is not None:  # desactivar (false) o reactivar (true) desde la edición
        promotor.activo = datos.activo
    db.commit()
    db.refresh(promotor)
    return promotor


def eliminar_promotor(db: Session, rfc: str) -> None:
    """Elimina de verdad, pero solo si no tiene grupos (RN-08). Si los tiene, hay que desactivarlo."""
    promotor = _obtener(db, rfc)
    grupos = db.scalar(select(func.count()).select_from(Grupo).where(Grupo.rfcpromotor == promotor.rfc)) or 0
    if grupos:
        raise Conflicto(
            f"No se puede eliminar: el promotor tiene {grupos} grupo(s). "
            "Desactívalo en su lugar"
        )
    db.delete(promotor)
    db.commit()
