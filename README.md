# Extra-Liebres

> Proyecto final de **Programación Web (AEB-1055)** · Instituto Tecnológico de Ciudad Juárez · Ago–Dic 2026

[![CI](https://github.com/luisreyna060318-alt/extra-liebres/actions/workflows/ci.yml/badge.svg)](https://github.com/luisreyna060318-alt/extra-liebres/actions/workflows/ci.yml)

## Problema

El Departamento de Actividades Extraescolares del ITCJ guardó en papel, hasta 2022, los registros de los
alumnos que cursaron actividades extraescolares. Desde 2023 usa SIISAE, pero los registros anteriores nunca
se migraron y no se pueden consultar. Extra-Liebres es una aplicación web (SPA en React + API REST en FastAPI +
PostgreSQL) para capturar, consultar y mantener esos registros: alumnos, promotores, actividades, semestres,
grupos e inscripciones con su desempeño.

## Integrantes y roles

| Integrante | Responsable de |
|---|---|
| Luis David Reyna Morisco | Cuentas y acceso, alumnos, catálogos, base de datos e infraestructura |
| Carlos Limones Ayala | Grupos, inscripciones, tablero, servicio de clima, CI y diseño |

## URL pública

| Qué | Dirección |
|---|---|
| **Aplicación** (frontend, en Vercel) | <https://extra-liebres.vercel.app> |
| API (backend, en Render) | <https://extra-liebres.onrender.com> |
| Documentación interactiva de la API | <https://extra-liebres.onrender.com/docs> |

> El backend gratuito de Render **se duerme tras 15 minutos sin uso**: la primera petición tarda de 30 a 60 segundos en
> despertarlo. Es normal; conviene abrir la aplicación unos minutos antes de una demostración.
>
> Las contraseñas del sitio público **no son** las de la tabla de abajo (esas son solo para correr el proyecto en tu
> computadora): las define quien despliega y se entregan al profesor junto con el reporte.

## Cómo correr el proyecto

Solo necesitas **Docker Desktop encendido** (con **Docker Compose 2.24 o más nuevo**: compruébalo con
`docker compose version`) y Git. Desde la raíz del repositorio:

```powershell
copy .env.example .env
docker compose up --build
```

Levanta los tres servicios (base de datos, backend y frontend). La primera vez tarda menos de 2 minutos (descarga las
imágenes y construye el backend y el frontend); las siguientes, unos segundos. Para correrlo en segundo plano y
esperar a que todo esté sano: `docker compose up --build -d --wait`. Cuando termina:

| Qué | Dónde |
|---|---|
| Aplicación (frontend) | <http://localhost:5173> |
| API (backend) | <http://localhost:8000> |
| Documentación interactiva de la API (OpenAPI) | <http://localhost:8000/docs> |
| Estado del servicio | <http://localhost:8000/api/health> |

El backend aplica las migraciones y carga los datos de ejemplo (**todos ficticios**) por sí solo. Para apagarlo: `Ctrl+C`
o `docker compose down`. Para empezar de cero (borra los datos): `docker compose down -v`.

> La URL de la API que usa el frontend (`VITE_API_URL`) se escribe en el código al construir la imagen: si la
> cambias en `.env`, vuelve a correr `docker compose up --build`. Para desarrollar el frontend con recarga
> automática usa `npm run dev` dentro de `frontend/`; para el backend sin Docker, mira `backend/README.md`.

**Si `docker compose up` falla con "port is already allocated" (o "address already in use") en el 5432**, ya tienes
un PostgreSQL instalado en tu computadora. Agrega a tu `.env` la línea `DB_HOST_PORT=5433` (o cualquier puerto libre)
y vuelve a correr el comando. Solo cambia el puerto por el que tú miras la base; el backend no se ve afectado.

Para publicarlo en internet (Neon + Render + Vercel) sigue `infra/DEPLOY.md`.

## Usuarios de prueba

Con el `.env` copiado de `.env.example` (solo para correr en tu computadora; en el despliegue público las claves son otras):

| Rol | Correo | Contraseña | Qué puede hacer |
|---|---|---|---|
| Administrador | `admin@ejemplo.com` | `cambia-esta-clave-admin1` | Todo, incluidos los usuarios y los catálogos |
| Capturista | `capturista@ejemplo.com` | `cambia-esta-clave-capt1` | Alumnos, grupos e inscripciones; no puede administrar usuarios ni catálogos (el servidor responde 403) |

Se pueden cambiar en `.env` (variables `SEED_*`) antes de la primera vez que se levanta el proyecto.

## Estructura del repositorio

```
frontend/   React + Vite
backend/    FastAPI (app/, tests/)
db/         migraciones Alembic y datos semilla
infra/      docker-compose y guía de despliegue
docs/       propuesta, arquitectura, reporte y autoevaluación
.github/    flujo de CI
```
