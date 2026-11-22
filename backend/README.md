# Backend (FastAPI)

API REST de Extra-Liebres. Estructura en capas: **routers** (HTTP) → **services** (lógica) → **models** (SQLAlchemy).

```
backend/
├── app/
│   ├── core/       configuración (.env), conexión a la BD, seguridad, constantes
│   ├── models/     tablas de la base de datos (SQLAlchemy)
│   ├── schemas/    esquemas Pydantic de entrada y salida
│   ├── routers/    rutas de la API
│   ├── services/   lógica de negocio
│   └── main.py     aplicación FastAPI
└── tests/          pruebas con pytest
```

## Correrlo en tu computadora (sin Docker para el backend)

Requisitos: Python 3.12 y Docker Desktop encendido. Todos los comandos se ejecutan desde la **raíz del repositorio**.

```powershell
# 1. Variables de entorno (una sola vez). Edita .env si quieres otras contraseñas.
copy .env.example .env

# 2. Entorno virtual e instalación de dependencias (una sola vez)
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt

# 3. Base de datos PostgreSQL en Docker
docker compose -f infra/docker-compose.yml up -d db

# 4. Desde fuera de Docker el host de la BD es 127.0.0.1 (en .env dice "db", que solo existe dentro de Docker)
$env:POSTGRES_HOST = "127.0.0.1"

# 5. Crear las tablas y cargar los datos de ejemplo (ficticios)
backend\.venv\Scripts\alembic.exe -c db/alembic.ini upgrade head
backend\.venv\Scripts\python.exe db/seed.py

# 6. Arrancar la API (desde la carpeta backend)
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

Después abre <http://127.0.0.1:8000/docs> para ver la documentación interactiva (OpenAPI).

> `$env:POSTGRES_HOST` solo vale para la terminal donde lo escribes; hay que repetirlo en cada terminal nueva.

## Comandos útiles

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q          # pruebas
cd ..
backend\.venv\Scripts\ruff.exe check backend db  # estilo (lo mismo que revisa CI)

# Nueva migración después de cambiar un modelo (revisa el archivo generado antes de aplicarlo)
backend\.venv\Scripts\alembic.exe -c db/alembic.ini revision --autogenerate -m "describe el cambio"
backend\.venv\Scripts\alembic.exe -c db/alembic.ini upgrade head

# Ver las tablas
docker compose -f infra/docker-compose.yml exec db psql -U extra_liebres -d extra_liebres -c "\dt"

# Empezar de cero (borra los datos): apaga el contenedor y su volumen
docker compose -f infra/docker-compose.yml down -v
```

## Valores guardados en la base de datos

Los valores "de máquina" se guardan sin acentos; la interfaz muestra la etiqueta con acentos.

| Campo | Valores |
|---|---|
| `usuario.rol` | `administrador`, `capturista` |
| `alumno.sexo` | `M`, `F` |
| `extraescolar.tipo` | `deportiva`, `cultural`, `civica` |
| `grupo.dia` | `lunes`, `martes`, `miercoles`, `jueves`, `viernes`, `sabado` |
| `alumno_grupo.desempenio` | `Excelente`, `Notable`, `Bueno`, `Suficiente`, `Insuficiente` |

Están definidos una sola vez en `app/core/constantes.py` y las restricciones `CHECK` de la BD salen de ahí.

## Restricciones de la base de datos que van más allá del modelo de la propuesta

- `extraescolar.nombreextra` es único (no puede haber dos actividades con el mismo nombre).
- `promotor.rfc` debe tener 12 o 13 caracteres.
- `usuario.correo` es único; el servicio de registro lo guarda siempre en minúsculas.

## Limitaciones conocidas

- **La búsqueda de alumnos distingue los acentos**: `Chávez` se encuentra escribiendo `chávez` o `CHÁVEZ`, pero no
  `chavez`. PostgreSQL ignora los acentos solo con la extensión `unaccent`, que no se activó para no complicar las
  pruebas (SQLite no la tiene). Es una mejora posible si sobra tiempo.

## Datos de ejemplo

Todo es **ficticio**. Los números de control empiezan con `99` (`99000001` a `99000200`) para que nunca
coincidan con los de alumnos reales.

## Producción

Con `ENTORNO=produccion` el backend se niega a arrancar si `SECRET_KEY` es la del ejemplo o tiene menos de
32 caracteres, y el seed se niega a crear usuarios con las contraseñas de ejemplo. Genera la clave con:
`python -c "import secrets; print(secrets.token_urlsafe(48))"`.
