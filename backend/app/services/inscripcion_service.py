"""Lógica de inscripciones y evaluación (HU-05.1 a HU-05.3, RN-04, RN-05).

Flujo de una evaluación: el router recibe {"calificacion": 90} ya validado (entero de 0 a 100) →
evaluar() busca la inscripción → calcula el desempeño con calcular_desempenio() → guarda ambos.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.errores import Conflicto, NoEncontrado
from app.models import Alumno, AlumnoGrupo, Grupo
from app.schemas.alumno import normalizar_nocontrol
from app.schemas.inscripcion import InscritoSalida
from app.services.desempeno import calcular_desempenio


def nombre_alumno(alumno: Alumno) -> str:
    """'López García Ana': apellidos primero, como en las listas de la escuela."""
    return " ".join(p for p in (alumno.apaterno, alumno.amaterno, alumno.nombre) if p)


def _a_salida(inscripcion: AlumnoGrupo) -> InscritoSalida:
    alumno = inscripcion.alumno
    return InscritoSalida(
        nocontrol=alumno.nocontrol,
        alumno=nombre_alumno(alumno),
        carrera=alumno.carrera,
        activo=alumno.activo,
        calificacion=inscripcion.calificacion,
        desempenio=inscripcion.desempenio,
    )


def _obtener_grupo(db: Session, idgrupo: int) -> Grupo:
    grupo = db.get(Grupo, idgrupo)
    if grupo is None:
        raise NoEncontrado("El grupo no existe")
    return grupo


def _obtener_inscripcion(db: Session, idgrupo: int, nocontrol: str) -> AlumnoGrupo:
    _obtener_grupo(db, idgrupo)  # primero el grupo, para dar el mensaje correcto
    inscripcion = db.get(AlumnoGrupo, (normalizar_nocontrol(nocontrol), idgrupo))
    if inscripcion is None:
        raise NoEncontrado("El alumno no está inscrito en este grupo")
    return inscripcion


def listar_inscritos(db: Session, idgrupo: int) -> list[InscritoSalida]:
    """Alumnos del grupo ordenados por apellidos y nombre."""
    _obtener_grupo(db, idgrupo)
    consulta = (
        select(AlumnoGrupo)
        .join(AlumnoGrupo.alumno)
        .where(AlumnoGrupo.idgrupo == idgrupo)
        .options(joinedload(AlumnoGrupo.alumno))
        .order_by(Alumno.apaterno, Alumno.amaterno, Alumno.nombre, Alumno.nocontrol)
    )
    return [_a_salida(i) for i in db.scalars(consulta)]


def inscribir(db: Session, idgrupo: int, nocontrol: str) -> InscritoSalida:
    """RN-04: el alumno debe existir y estar activo, y no puede inscribirse dos veces al mismo grupo."""
    _obtener_grupo(db, idgrupo)
    alumno = db.get(Alumno, nocontrol)
    if alumno is None:
        raise NoEncontrado("El alumno no existe")
    if not alumno.activo:
        raise Conflicto("El alumno está dado de baja; reactívalo antes de inscribirlo")
    if db.get(AlumnoGrupo, (nocontrol, idgrupo)) is not None:
        raise Conflicto("El alumno ya está inscrito en este grupo")

    inscripcion = AlumnoGrupo(nocontrol=nocontrol, idgrupo=idgrupo)
    db.add(inscripcion)
    try:
        db.commit()
    except IntegrityError:
        # Dos capturas simultáneas: la llave primaria compuesta (nocontrol, idgrupo) lo detecta
        db.rollback()
        raise Conflicto("El alumno ya está inscrito en este grupo") from None
    db.refresh(inscripcion)
    return _a_salida(inscripcion)


def evaluar(db: Session, idgrupo: int, nocontrol: str, calificacion: int) -> InscritoSalida:
    """Guarda la calificación y el desempeño CALCULADO (RN-05). Corregir es lo mismo que capturar:
    el desempeño se vuelve a calcular siempre, así nunca queda desfasado de la calificación."""
    inscripcion = _obtener_inscripcion(db, idgrupo, nocontrol)
    inscripcion.calificacion = calificacion
    inscripcion.desempenio = calcular_desempenio(calificacion)
    db.commit()
    db.refresh(inscripcion)
    return _a_salida(inscripcion)


def eliminar_inscripcion(db: Session, idgrupo: int, nocontrol: str, confirmar: bool) -> None:
    """HU-05.3: quitar al alumno del grupo. Si ya tiene calificación se pide confirmación explícita
    (?confirmar=true), porque se perdería parte de su historial."""
    inscripcion = _obtener_inscripcion(db, idgrupo, nocontrol)
    if inscripcion.calificacion is not None and not confirmar:
        raise Conflicto(
            "El alumno ya tiene calificación; confirma que quieres quitarlo del grupo (confirmar=true)"
        )
    db.delete(inscripcion)
    db.commit()
