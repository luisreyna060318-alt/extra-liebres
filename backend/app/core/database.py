"""Conexión a PostgreSQL con SQLAlchemy."""

from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Nombres predecibles para índices y restricciones: así Alembic puede crearlos y borrarlos sin ambigüedad.
convencion_nombres = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Clase de la que heredan todos los modelos."""

    metadata = MetaData(naming_convention=convencion_nombres)


engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Iterator[Session]:
    """Dependencia de FastAPI: una sesión de BD por petición, que siempre se cierra."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
