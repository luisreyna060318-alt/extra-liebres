"""Lógica de alumnos (HU-02.1 a HU-02.4). Aquí viven las reglas; el router solo recibe y responde."""

from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.constantes import CARRERAS
from app.core.errores import Conflicto, NoEncontrado
from app.core.paginacion import Paginacion
from app.models import Alumno, AlumnoGrupo, Extraescolar, Grupo, Semestre
from app.schemas.alumno import (
    AlumnoActualizar,
    AlumnoCrear,
    HistorialItem,
    OpcionesAlumno,
    normalizar_nocontrol,
)

Estado = Literal["activos", "bajas", "todos"]


def _obtener(db: Session, nocontrol: str) -> Alumno:
    alumno = db.get(Alumno, normalizar_nocontrol(nocontrol))
    if alumno is None:
        raise NoEncontrado("El alumno no existe")
    return alumno


def crear_alumno(db: Session, datos: AlumnoCrear) -> Alumno:
    if db.get(Alumno, datos.nocontrol):
        raise Conflicto("Ya existe un alumno con ese número de control")
    alumno = Alumno(**datos.model_dump())
    db.add(alumno)
    try:
        db.commit()
    except IntegrityError:
        # Dos capturas simultáneas del mismo número de control: la llave primaria de la BD lo detecta
        db.rollback()
        raise Conflicto("Ya existe un alumno con ese número de control") from None
    db.refresh(alumno)
    return alumno


def obtener_alumno(db: Session, nocontrol: str) -> Alumno:
    return _obtener(db, nocontrol)


def listar_alumnos(
    db: Session,
    paginacion: Paginacion,
    q: str | None,
    carrera: str | None,
    campus: str | None,
    estado: Estado,
) -> tuple[list[Alumno], int]:
    """Devuelve (alumnos de la página, total de la consulta). Todos los filtros se combinan con AND.

    La búsqueda q parte el texto en palabras: cada palabra debe aparecer en el nombre, algún apellido o el
    número de control. Así "ana lopez" encuentra a Ana López. No distingue mayúsculas de minúsculas.
    """
    consulta = select(Alumno)
    for palabra in (q or "").split():
        # icontains + autoescape: los símbolos % y _ que escriba la persona se buscan tal cual, no como comodines
        consulta = consulta.where(
            or_(
                Alumno.nombre.icontains(palabra, autoescape=True),
                Alumno.apaterno.icontains(palabra, autoescape=True),
                Alumno.amaterno.icontains(palabra, autoescape=True),
                Alumno.nocontrol.icontains(palabra, autoescape=True),
            )
        )
    if carrera:
        consulta = consulta.where(Alumno.carrera == carrera)
    if campus:
        consulta = consulta.where(Alumno.campus == campus)
    if estado == "activos":
        consulta = consulta.where(Alumno.activo.is_(True))
    elif estado == "bajas":
        consulta = consulta.where(Alumno.activo.is_(False))

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    orden = (Alumno.apaterno, Alumno.amaterno, Alumno.nombre, Alumno.nocontrol)
    pagina = db.scalars(consulta.order_by(*orden).offset(paginacion.offset).limit(paginacion.size))
    return list(pagina), total


def actualizar_alumno(db: Session, nocontrol: str, datos: AlumnoActualizar) -> Alumno:
    alumno = _obtener(db, nocontrol)
    cambios = datos.model_dump(exclude={"activo"})
    for campo, valor in cambios.items():
        setattr(alumno, campo, valor)
    if datos.activo is not None:  # reactivar (true) o dar de baja (false) desde la edición
        alumno.activo = datos.activo
    db.commit()
    db.refresh(alumno)
    return alumno


def eliminar_alumno(db: Session, nocontrol: str) -> None:
    """Elimina de verdad, pero solo si no está inscrito en ningún grupo. Si lo está, hay que darlo de baja (PUT)."""
    alumno = _obtener(db, nocontrol)
    cuenta = select(func.count()).select_from(AlumnoGrupo).where(AlumnoGrupo.nocontrol == alumno.nocontrol)
    inscripciones = db.scalar(cuenta) or 0
    if inscripciones:
        raise Conflicto(
            f"No se puede eliminar: el alumno tiene {inscripciones} inscripción(es). Dalo de baja en su lugar"
        )
    db.delete(alumno)
    db.commit()


def historial_alumno(db: Session, nocontrol: str) -> list[HistorialItem]:
    """Actividades que cursó el alumno, del semestre más reciente al más antiguo."""
    alumno = _obtener(db, nocontrol)
    consulta = (
        select(AlumnoGrupo)
        .join(AlumnoGrupo.grupo)
        .join(Grupo.semestre)
        .join(Grupo.extraescolar)
        .where(AlumnoGrupo.nocontrol == alumno.nocontrol)
        .order_by(Semestre.anio.desc(), Semestre.mesinicio.desc(), Extraescolar.nombreextra)
        .options(
            joinedload(AlumnoGrupo.grupo).joinedload(Grupo.semestre),
            joinedload(AlumnoGrupo.grupo).joinedload(Grupo.extraescolar),
            joinedload(AlumnoGrupo.grupo).joinedload(Grupo.promotor),
        )
    )
    historial = []
    for inscripcion in db.scalars(consulta):
        grupo = inscripcion.grupo
        promotor = grupo.promotor
        historial.append(
            HistorialItem(
                idgrupo=grupo.idgrupo,
                actividad=grupo.extraescolar.nombreextra,
                semestre_anio=grupo.semestre.anio,
                semestre_mesinicio=grupo.semestre.mesinicio,
                semestre_mestermino=grupo.semestre.mestermino,
                promotor=" ".join(p for p in (promotor.nombre, promotor.apaterno, promotor.amaterno) if p),
                dia=grupo.dia,
                horainicio=grupo.horainicio,
                horatermino=grupo.horatermino,
                aula=grupo.aula,
                calificacion=inscripcion.calificacion,
                desempenio=inscripcion.desempenio,
            )
        )
    return historial


def opciones_alumnos(db: Session) -> OpcionesAlumno:
    campus = db.scalars(select(Alumno.campus).distinct().order_by(Alumno.campus))
    return OpcionesAlumno(carreras=list(CARRERAS), campus=list(campus))
