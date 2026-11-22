"""Configuración común de las pruebas.

Las pruebas usan SQLite en memoria (rápido y sin tocar la base real) y no necesitan un archivo .env:
se ponen valores de prueba antes de importar la aplicación.
"""

import os
from datetime import time

os.environ.setdefault("SECRET_KEY", "clave-solo-para-pruebas-0123456789abcdef")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import models  # noqa: E402,F401  (registra las tablas en Base.metadata)
from app.core.database import Base, get_db  # noqa: E402
from app.core.security import crear_token, hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Alumno, AlumnoGrupo, Extraescolar, Grupo, Promotor, Semestre, Usuario  # noqa: E402

PASSWORD_PRUEBA = "Clave1234"
# Calcular un hash bcrypt tarda ~0.2 s; se calcula una sola vez y se reutiliza en todos los usuarios de prueba
HASH_PRUEBA = hash_password(PASSWORD_PRUEBA)


@pytest.fixture()
def db():
    """Una base de datos SQLite nueva y vacía para cada prueba."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, autoflush=False)() as sesion:
        yield sesion
    engine.dispose()


@pytest.fixture()
def client(db):
    """Cliente HTTP de pruebas que usa la base de datos de prueba en lugar de PostgreSQL."""

    def get_db_de_prueba():
        yield db

    app.dependency_overrides[get_db] = get_db_de_prueba
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


@pytest.fixture()
def crear_usuario(db):
    """Fábrica de usuarios: crear_usuario("ana@correo.com", rol="administrador")."""

    def _crear(correo: str, rol: str = "capturista", activo: bool = True, nombre: str = "Usuario de prueba"):
        usuario = Usuario(nombre=nombre, correo=correo, password_hash=HASH_PRUEBA, rol=rol, activo=activo)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    return _crear


def encabezado_de(usuario: Usuario) -> dict[str, str]:
    """Encabezado Authorization con un token válido de ese usuario."""
    return {"Authorization": f"Bearer {crear_token(usuario.id)}"}


@pytest.fixture()
def admin(crear_usuario):
    return crear_usuario("admin@correo.com", rol="administrador", nombre="Admin Prueba")


@pytest.fixture()
def capturista(crear_usuario):
    return crear_usuario("capturista@correo.com", rol="capturista", nombre="Capturista Prueba")


@pytest.fixture()
def crear_alumno(db):
    """Fábrica de alumnos: crear_alumno("19110001", nombre="Ana", activo=False)."""

    def _crear(nocontrol="19110001", nombre="Ana", apaterno="López", amaterno="García", sexo="F",
               carrera="Ingeniería Industrial", campus="Campus I", activo=True):
        alumno = Alumno(nocontrol=nocontrol, nombre=nombre, apaterno=apaterno, amaterno=amaterno, sexo=sexo,
                        carrera=carrera, campus=campus, activo=activo)
        db.add(alumno)
        db.commit()
        return alumno

    return _crear


@pytest.fixture()
def crear_grupo(db):
    """Fábrica de grupos. Crea (o reutiliza) el semestre, la actividad y el promotor que necesite."""

    def _crear(anio=2026, mesinicio=1, mestermino=6, actividad="Fútbol", tipo="deportiva", rfc="AAAA000101AAA",
               dia="lunes", inicio=time(8), fin=time(9), aula="Cancha de fútbol"):
        semestre = db.query(Semestre).filter_by(anio=anio, mesinicio=mesinicio).first()
        if semestre is None:
            semestre = Semestre(anio=anio, mesinicio=mesinicio, mestermino=mestermino)
            db.add(semestre)
        extraescolar = db.query(Extraescolar).filter_by(nombreextra=actividad).first()
        if extraescolar is None:
            extraescolar = Extraescolar(nombreextra=actividad, tipo=tipo)
            db.add(extraescolar)
        promotor = db.get(Promotor, rfc)
        if promotor is None:
            promotor = Promotor(rfc=rfc, nombre="Pedro", apaterno="Ruiz", amaterno="Soto")
            db.add(promotor)
        db.flush()
        grupo = Grupo(dia=dia, horainicio=inicio, horatermino=fin, aula=aula, idsemestre=semestre.idsemestre,
                      idextraescolar=extraescolar.idextraescolar, rfcpromotor=promotor.rfc)
        db.add(grupo)
        db.commit()
        return grupo

    return _crear


@pytest.fixture()
def inscribir(db):
    """inscribir(alumno, grupo, calificacion=90, desempenio="Notable")"""

    def _inscribir(alumno, grupo, calificacion=None, desempenio=None):
        inscripcion = AlumnoGrupo(nocontrol=alumno.nocontrol, idgrupo=grupo.idgrupo,
                                  calificacion=calificacion, desempenio=desempenio)
        db.add(inscripcion)
        db.commit()
        return inscripcion

    return _inscribir
