# Extra-Liebres — contexto del proyecto

Proyecto final de Programación Web (AEB-1055, ITCJ). Equipo de 2 estudiantes: Luis Reyna y Carlos Limones.
Rehace una app de registros históricos de actividades extraescolares como SPA + API REST.

## Stack (no cambiar)
- Frontend: React + Vite + TypeScript, react-router, fetch (sin librerías de estado), CSS externo (Flexbox/Grid).
- Backend: Python 3.12 + FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL.
- Infra: Docker, Docker Compose, GitHub Actions. Despliegue: Vercel (front) + Render (back) + Neon (BD).

## Estructura (monorepo)
frontend/  backend/app/{routers,services,models,schemas,core}  backend/tests  db/{migrations,seed.py}  infra/  docs/

## Reglas de código
- Los estudiantes deben poder EXPLICAR todo: código simple y directo, sin patrones avanzados ni abstracciones
  innecesarias. Comentarios breves en español que expliquen el porqué.
- Capas: router (HTTP) → service (lógica) → model (SQLAlchemy). Los routers no tienen lógica de negocio.
- Esquemas Pydantic distintos para entrada y salida. Nunca devolver `password_hash`.
- Códigos HTTP correctos (200/201/204/400/401/403/404/409/422). Respuestas JSON consistentes.
- Autorización por rol SIEMPRE en el servidor (dependencia `require_role`).
- Contraseñas con `bcrypt` (o `argon2-cffi`), JWT con `PyJWT`. NO usar `passlib` ni `python-jose` (sin mantenimiento).
- Configuración por variables de entorno (`.env`, nunca en el repo). CORS limitado al dominio del frontend.
- Dependencias: solo paquetes conocidos y activos. Antes de agregar uno nuevo, avisar y justificar.
- Interfaz y mensajes en español de México. HTML semántico, `label` en formularios, texto alternativo.
- Datos de ejemplo siempre FICTICIOS.

## Fuente de verdad
docs/propuesta-v2.md (historias HU-xx.x, reglas RN-xx, modelo de datos y endpoints).

## Commits
Conventional Commits en español. Los commits con código de IA terminan con `Co-Authored-By:` o `Assisted-by:`.
