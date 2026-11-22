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

_Pendiente de desplegar._

## Cómo correr el proyecto

Solo necesitas **Docker Desktop encendido** y Git. Desde la raíz del repositorio:

```powershell
copy .env.example .env
docker compose up --build
```

La primera vez tarda 2 minutos aproximadamente (descarga las imágenes y construye el backend); las siguientes, unos segundos.
Cuando termina:

| Qué | Dónde |
|---|---|
| API (backend) | <http://localhost:8000> |
| Documentación interactiva de la API (OpenAPI) | <http://localhost:8000/docs> |
| Estado del servicio | <http://localhost:8000/api/health> |

El backend aplica las migraciones y carga los datos de ejemplo (**todos ficticios**) por sí solo. Para apagarlo: `Ctrl+C`
o `docker compose down`. Para empezar de cero (borra los datos): `docker compose down -v`.

> El frontend se agrega a este comando cuando su Dockerfile esté en el repositorio. Mientras tanto se corre con
> `npm run dev` dentro de `frontend/`. Si quieres desarrollar el backend sin Docker, mira `backend/README.md`.

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
