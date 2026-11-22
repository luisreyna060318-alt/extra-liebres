#!/bin/sh
# Arranque del contenedor del backend:
#   1) crea o actualiza las tablas (migraciones de Alembic),
#   2) opcionalmente carga los datos de ejemplo (SEED_ON_START=true),
#   3) arranca la API.
set -e

echo "Aplicando migraciones..."
alembic -c /app/db/alembic.ini upgrade head

# El seed se puede ejecutar varias veces: si una tabla ya tiene datos, la omite
if [ "${SEED_ON_START:-false}" = "true" ]; then
    echo "Cargando datos de ejemplo..."
    python /app/db/seed.py
fi

echo "Arrancando la API..."
# PORT lo define Render; en Docker Compose se usa 8000. --proxy-headers: detrás del proxy de Render
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers
