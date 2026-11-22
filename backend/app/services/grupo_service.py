"""Lógica de grupos (HU-04.1, HU-04.3, HU-04.4). Aquí viven las reglas; el router solo recibe y responde."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.errores import Conflicto, NoEncontrado
from app.core.paginacion import Paginacion
from app.models import Extraescolar, Grupo, Promotor, Semestre
from app.schemas.grupo import GrupoDatos, GrupoSalida

MESES = (
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)  # fmt: skip

# Carga junto con el grupo su semestre, actividad, promotor e inscripciones (evita una consulta por grupo)
CARGAR_RELACIONES = (
    joinedload(Grupo.semestre),
    joinedload(Grupo.extraescolar),
    joinedload(Grupo.promotor),
    selectinload(Grupo.inscripciones),
)


# ---------- Ayudantes para armar la respuesta y los mensajes ----------


def _nombre_promotor(promotor: Promotor) -> str:
    return " ".join(p for p in (promotor.nombre, promotor.apaterno, promotor.amaterno) if p)


def _nombre_semestre(semestre: Semestre) -> str:
    return f"{MESES[semestre.mesinicio - 1]}-{MESES[semestre.mestermino - 1]} {semestre.anio}"


def _describir(grupo: Grupo) -> str:
    """Texto que identifica a un grupo para el usuario: 'Fútbol (grupo 3), lunes de 08:00 a 09:00'."""
    return (
        f"{grupo.extraescolar.nombreextra} (grupo {grupo.idgrupo}), {grupo.dia} "
        f"de {grupo.horainicio:%H:%M} a {grupo.horatermino:%H:%M}"
    )


def a_salida(grupo: Grupo) -> GrupoSalida:
    return GrupoSalida(
        idgrupo=grupo.idgrupo,
        idsemestre=grupo.idsemestre,
        semestre=_nombre_semestre(grupo.semestre),
        idextraescolar=grupo.idextraescolar,
        actividad=grupo.extraescolar.nombreextra,
        tipo_actividad=grupo.extraescolar.tipo,
        rfcpromotor=grupo.rfcpromotor,
        promotor=_nombre_promotor(grupo.promotor),
        dia=grupo.dia,
        horainicio=grupo.horainicio,
        horatermino=grupo.horatermino,
        aula=grupo.aula,
        inscritos=len(grupo.inscripciones),
    )


def _obtener(db: Session, idgrupo: int) -> Grupo:
    grupo = db.scalar(select(Grupo).where(Grupo.idgrupo == idgrupo).options(*CARGAR_RELACIONES))
    if grupo is None:
        raise NoEncontrado("El grupo no existe")
    return grupo


# ---------- Reglas de negocio ----------


def _validar_referencias(db: Session, datos: GrupoDatos) -> None:
    """El semestre, la actividad y el promotor elegidos deben existir."""
    if db.get(Semestre, datos.idsemestre) is None:
        raise NoEncontrado("El semestre elegido no existe")
    if db.get(Extraescolar, datos.idextraescolar) is None:
        raise NoEncontrado("La actividad elegida no existe")
    if db.get(Promotor, datos.rfcpromotor) is None:
        raise NoEncontrado("El promotor elegido no existe")


def validar_cruces(db: Session, grupo: GrupoDatos, excluir_id: int | None = None) -> None:
    """RN-03: lanza 409 si el grupo choca con otro del mismo promotor o de la misma aula,
    en el mismo semestre y el mismo día.

    excluir_id: al EDITAR se pasa el id del propio grupo, para que no choque consigo mismo.

    Dos horarios se traslapan si  inicio1 < fin2  y  inicio2 < fin1. Ejemplos:
      - 08:00-10:00 contra 09:00-11:00 -> 08 < 11 y 09 < 10 -> SÍ se traslapan.
      - 08:00-09:00 contra 09:00-10:00 -> 08 < 10, pero 09 < 09 es falso -> NO (son contiguos, se permite).
      - 08:00-12:00 contra 09:00-10:00 -> 08 < 10 y 09 < 12 -> SÍ (uno contiene al otro).
    """
    consulta = (
        select(Grupo)
        .where(
            Grupo.idsemestre == grupo.idsemestre,
            Grupo.dia == grupo.dia,
            Grupo.horainicio < grupo.horatermino,  # inicio del otro < fin del nuevo
            grupo.horainicio < Grupo.horatermino,  # inicio del nuevo < fin del otro
            # El aula se compara sin distinguir mayúsculas: "Aula 5" y "aula 5" son el mismo lugar
            or_(Grupo.rfcpromotor == grupo.rfcpromotor, func.lower(Grupo.aula) == grupo.aula.lower()),
        )
        .options(joinedload(Grupo.extraescolar), joinedload(Grupo.promotor))
        .order_by(Grupo.horainicio, Grupo.idgrupo)
    )
    if excluir_id is not None:
        consulta = consulta.where(Grupo.idgrupo != excluir_id)

    otro = db.scalars(consulta).first()
    if otro is None:
        return
    if otro.rfcpromotor == grupo.rfcpromotor:
        motivo = f"el promotor {_nombre_promotor(otro.promotor)} ya imparte"
    else:
        # "lugar" en vez de "aula": también puede ser una instalación deportiva (cancha, gimnasio...)
        motivo = f"el lugar «{otro.aula}» ya está ocupado por"
    raise Conflicto(f"Cruce de horario: {motivo} {_describir(otro)} en ese semestre")


# ---------- Operaciones del CRUD ----------


def listar_grupos(
    db: Session,
    paginacion: Paginacion,
    semestre: int | None,
    extraescolar: int | None,
    promotor: str | None,
    dia: str | None,
) -> tuple[list[GrupoSalida], int]:
    """Devuelve (grupos de la página, total de la consulta). Todos los filtros se combinan con AND."""
    consulta = select(Grupo)
    if semestre is not None:
        consulta = consulta.where(Grupo.idsemestre == semestre)
    if extraescolar is not None:
        consulta = consulta.where(Grupo.idextraescolar == extraescolar)
    if promotor:
        consulta = consulta.where(Grupo.rfcpromotor == promotor.strip().upper())
    if dia:
        consulta = consulta.where(Grupo.dia == dia.strip().lower())

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    # Primero el semestre más reciente; dentro de él, por actividad y hora
    orden = (Semestre.anio.desc(), Semestre.mesinicio.desc(), Extraescolar.nombreextra, Grupo.horainicio, Grupo.idgrupo)
    pagina = db.scalars(
        consulta.join(Grupo.semestre)
        .join(Grupo.extraescolar)
        .options(*CARGAR_RELACIONES)
        .order_by(*orden)
        .offset(paginacion.offset)
        .limit(paginacion.size)
    ).unique()
    return [a_salida(g) for g in pagina], total


def obtener_grupo(db: Session, idgrupo: int) -> GrupoSalida:
    return a_salida(_obtener(db, idgrupo))


def crear_grupo(db: Session, datos: GrupoDatos) -> GrupoSalida:
    _validar_referencias(db, datos)
    validar_cruces(db, datos)
    grupo = Grupo(**datos.model_dump())
    db.add(grupo)
    db.commit()
    return obtener_grupo(db, grupo.idgrupo)


def actualizar_grupo(db: Session, idgrupo: int, datos: GrupoDatos) -> GrupoSalida:
    grupo = _obtener(db, idgrupo)
    _validar_referencias(db, datos)
    validar_cruces(db, datos, excluir_id=idgrupo)  # sin esto, el grupo chocaría consigo mismo
    for campo, valor in datos.model_dump().items():
        setattr(grupo, campo, valor)
    db.commit()
    db.expire(grupo)  # recarga las relaciones por si cambió el semestre, la actividad o el promotor
    return obtener_grupo(db, idgrupo)


def eliminar_grupo(db: Session, idgrupo: int) -> None:
    """HU-04.4 CA2: un grupo con alumnos inscritos no se elimina (sus calificaciones son historial)."""
    grupo = _obtener(db, idgrupo)
    inscritos = len(grupo.inscripciones)
    if inscritos:
        raise Conflicto(
            f"No se puede eliminar el grupo {_describir(grupo)}: tiene {inscritos} alumno(s) inscrito(s)"
        )
    db.delete(grupo)
    db.commit()
