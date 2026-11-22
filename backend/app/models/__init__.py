"""Importa todos los modelos para que SQLAlchemy y Alembic los conozcan."""

from app.models.alumno import Alumno
from app.models.alumno_grupo import AlumnoGrupo
from app.models.extraescolar import Extraescolar
from app.models.grupo import Grupo
from app.models.promotor import Promotor
from app.models.semestre import Semestre
from app.models.usuario import Usuario

__all__ = [
    "Alumno",
    "AlumnoGrupo",
    "Extraescolar",
    "Grupo",
    "Promotor",
    "Semestre",
    "Usuario",
]
