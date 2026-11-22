"""Búsqueda global (HU-06.2): coincidencias en alumnos y en grupos con un solo texto."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Alumno, Extraescolar, Grupo, Promotor, Semestre
from app.schemas.busqueda import AlumnoCoincidencia, Busqueda, GrupoCoincidencia
from app.services.grupo_service import _describir, _nombre_promotor, _nombre_semestre
from app.services.inscripcion_service import nombre_alumno

MAXIMO = 10  # coincidencias por tipo


def _alumnos(db: Session, palabras: list[str]) -> tuple[list[AlumnoCoincidencia], bool]:
    consulta = select(Alumno).where(Alumno.activo.is_(True))
    for palabra in palabras:
        # Cada palabra debe aparecer en alguno de los campos; autoescape: % y _ se buscan tal cual
        consulta = consulta.where(
            or_(
                Alumno.nombre.icontains(palabra, autoescape=True),
                Alumno.apaterno.icontains(palabra, autoescape=True),
                Alumno.amaterno.icontains(palabra, autoescape=True),
                Alumno.nocontrol.icontains(palabra, autoescape=True),
            )
        )
    # Se pide uno de más: si llega, sabemos que hay más resultados que los que mostramos
    filas = list(db.scalars(consulta.order_by(Alumno.apaterno, Alumno.amaterno, Alumno.nombre).limit(MAXIMO + 1)))
    salida = [
        AlumnoCoincidencia(nocontrol=a.nocontrol, alumno=nombre_alumno(a), carrera=a.carrera) for a in filas[:MAXIMO]
    ]
    return salida, len(filas) > MAXIMO


def _grupos(db: Session, palabras: list[str]) -> tuple[list[GrupoCoincidencia], bool]:
    consulta = (
        select(Grupo)
        .join(Grupo.extraescolar)
        .join(Grupo.promotor)
        .join(Grupo.semestre)
        .options(joinedload(Grupo.extraescolar), joinedload(Grupo.promotor), joinedload(Grupo.semestre))
    )
    for palabra in palabras:
        consulta = consulta.where(
            or_(
                Extraescolar.nombreextra.icontains(palabra, autoescape=True),
                Grupo.aula.icontains(palabra, autoescape=True),
                Grupo.dia.icontains(palabra, autoescape=True),
                Promotor.nombre.icontains(palabra, autoescape=True),
                Promotor.apaterno.icontains(palabra, autoescape=True),
                Promotor.amaterno.icontains(palabra, autoescape=True),
            )
        )
    orden = (Semestre.anio.desc(), Semestre.mesinicio.desc(), Extraescolar.nombreextra, Grupo.idgrupo)
    filas = list(db.scalars(consulta.order_by(*orden).limit(MAXIMO + 1)))
    salida = [
        GrupoCoincidencia(
            idgrupo=g.idgrupo,
            descripcion=_describir(g),
            semestre=_nombre_semestre(g.semestre),
            promotor=_nombre_promotor(g.promotor),
        )
        for g in filas[:MAXIMO]
    ]
    return salida, len(filas) > MAXIMO


def buscar(db: Session, q: str) -> Busqueda:
    palabras = q.split()
    alumnos, alumnos_hay_mas = _alumnos(db, palabras)
    grupos, grupos_hay_mas = _grupos(db, palabras)
    return Busqueda(
        q=" ".join(palabras),
        alumnos=alumnos,
        alumnos_hay_mas=alumnos_hay_mas,
        grupos=grupos,
        grupos_hay_mas=grupos_hay_mas,
    )
