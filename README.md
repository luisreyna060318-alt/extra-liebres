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

_Pendiente: se completa cuando exista `docker compose up`._

## Usuarios de prueba

_Pendiente: uno por rol (administrador y capturista), con datos ficticios._

## Estructura del repositorio

```
frontend/   React + Vite
backend/    FastAPI (app/, tests/)
db/         migraciones Alembic y datos semilla
infra/      docker-compose y notas de despliegue
docs/       propuesta, arquitectura, reporte y autoevaluación
.github/    flujo de CI
```
