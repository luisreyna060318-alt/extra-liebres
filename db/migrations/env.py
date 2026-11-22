"""Entorno de Alembic: conecta las migraciones con nuestros modelos y nuestra base de datos.

Se ejecuta con (desde la raíz del repositorio):
    alembic -c db/alembic.ini upgrade head
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

# Para poder importar "app" (que vive en backend/) desde esta carpeta
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app import models  # noqa: E402,F401  (importar los modelos los registra en Base.metadata)
from app.core.config import settings  # noqa: E402
from app.core.database import Base, engine  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic compara esta metadata con la base de datos para generar las migraciones
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse a la base de datos (alembic upgrade head --sql)."""
    context.configure(
        url=settings.sqlalchemy_url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones conectándose a la base de datos."""
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
