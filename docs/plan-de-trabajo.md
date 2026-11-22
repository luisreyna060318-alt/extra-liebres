# 03 · Plan de trabajo, flujo de Git y commits

Decisiones del equipo: rebanadas verticales (cada quien hace funciones de punta a punta), TypeScript,
Open-Meteo como API externa y Vercel + Render + Neon para el despliegue. **Luis** = L, **Carlos** = C.

## 1. Estructura del repositorio

Nombre: `extra-liebres` · fuera de OneDrive (p. ej. `C:\dev\extra-liebres`).

```
extra-liebres/
├── frontend/            # React + Vite (+TS), Dockerfile
│   └── src/ (components/, pages/, api/, hooks/, styles/)
├── backend/             # FastAPI
│   ├── app/ (routers/, services/, models/, schemas/, core/)   # capas: rutas → servicios → modelos
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── db/                  # migraciones Alembic, seed, diagrama ER
├── infra/               # docker-compose.yml, notas de despliegue
├── docs/                # arquitectura.png, REPORTE.pdf, AUTOEVALUACION.md, propuesta
├── .github/workflows/ci.yml
├── .env.example
├── CLAUDE.md            # contexto para el asistente de IA (se declara en AI_USAGE.md)
├── AI_USAGE.md
└── README.md
```

> Los PDF/Word del profesor y de la tarea **no** se suben al repo (se quedan en la carpeta de la tarea).

## 2. Flujo de Git (el que pide el profesor)

- `main` solo recibe cambios por **pull request revisado por la otra persona**.
- Ramas: `feature/<área>-<tema>`, por ejemplo `feature/backend-auth`, `feature/front-grupos`.
- **Conventional Commits** en español: `feat(backend): …`, `fix: …`, `docs: …`, `test: …`, `chore: …`, `ci: …`.
- Cada quien commitea con **su** nombre/correo y **su** cuenta de GitHub.
- Commits con código generado por IA terminan con una línea (se declara también en `AI_USAGE.md`):
  - Claude Code → `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`
  - Otra herramienta → `Assisted-by: <herramienta/modelo>`
- PRs chicos (≤ 1 funcionalidad), idealmente uno o dos por día por persona.
- Tablero (GitHub Projects): columnas *Por hacer / En curso / En revisión / Hecho*. Se mueve la tarjeta
  **cuando se hace el trabajo**, no al final (criterio 1).
- Etiqueta final: `git tag v1.0.0` la noche del miércoles 25 (antes de la hora de entrega).

### Cómo haré yo (Claude) los commits de Luis

1. Antes de cada commit te muestro: `git status`, `git diff --stat` y un **resumen** de qué entra y por qué.
2. Reviso que **no** entren `.env`, llaves, contraseñas, datos reales ni los documentos del profesor.
3. Solo hago el commit si **tú** lo apruebas. No hago `push` sin que lo pidas.
4. Uso la identidad de Git de Luis en este repo (correo `noreply` de GitHub, porque GitHub rechaza el push con el correo privado) y la línea `Co-Authored-By` de arriba.

## 3. Cronograma — todo termina el **domingo 22 en la noche**; el lunes solo se entrega

> Replanteado el 21-nov: la entrega es el **lunes 23 (≈ 5–6 pm)**, pero ambos trabajan ese día, así que
> **el lunes no se trabaja en el proyecto**. Se construye **hoy sábado 21 y mañana domingo 22**; el
> domingo en la noche se congela, se etiqueta `v1.0.0` y el lunes solo se entrega.
> Hay que confirmar con el profesor que la entrega del lunes sea válida (su documento fija el jueves 26)
> y si el lunes habrá demo en vivo (ver nota abajo).

| Bloque | Luis | Carlos |
|---|---|---|
| **Sáb 21 mañana** | Repo en GitHub (público) · primer issue (propuesta) · issues HU · compose con PostgreSQL · esqueleto FastAPI · **modelos SQLAlchemy** (empujar temprano) | Instalar herramientas · clonar · Vite + React, rutas y layout semántico · estilos responsivos · cliente `fetch` + contexto de autenticación |
| **Sáb 21 tarde** | Migración Alembic + **seed** · **auth** (registro, login JWT, hash) · `require_role` · **alumnos** (back) | Login/registro con validación · **grupos** (back, con cruces) · empezar CI |
| **Sáb 21 noche** | Pruebas de auth y permisos · pantallas de **alumnos** | **Inscripción y evaluación** · consulta de inscritos · **cliente del clima** |
| **Dom 22 mañana** | Catálogos + usuarios/admin (back + front) · Dockerfile backend y compose completo | Pantallas de **grupos** con formulario dinámico · endpoint del **tablero** · pruebas de sus endpoints |
| **Dom 22 tarde** | **Desplegar** (Neon + Render) y CORS · `docker compose up` desde cero | Pantalla del **tablero** · pantallas de inscripción/consulta · Dockerfile frontend · **desplegar** (Vercel) |
| **Dom 22 noche (1)** | `AI_USAGE.md` · seguridad (OWASP A01/A02) · revisión de PRs | Lighthouse y accesibilidad · diagrama de arquitectura |
| **Dom 22 noche (2)** | **Reporte** (versión corta: 4 fases, figuras y referencias) · **autoevaluación** con evidencias · prueba final del compose | **Reporte** (su mitad) · prueba final en la URL pública · ensayo cruzado rápido |
| **Dom 22 cierre** | **Congelar → `git tag v1.0.0`** y verificar que el repo público se ve bien | |
| **Lun 23 (sin trabajo)** | Solo entregar el enlace (≈ 5–6 pm) | Idem |

**Con 2 días el alcance se recorta:** las historias **deseables** (HU-04.4, 05.3, 06.2, 07.2) **no se
implementan** (quedan en el backlog como "deseables"). Sin puntos extra. Si el tiempo aprieta, orden de
recorte: pruebas del frontend → reporte más corto (≈ 8–10 páginas) → historias menos esenciales como el
historial detallado del alumno. **Nunca** se recorta auth, CRUD, clima, tablero, Docker, CI ni
`AI_USAGE.md`.

> **Actualización (22-nov):** al final sí se implementaron las cuatro historias deseables (HU-04.4, HU-05.3, HU-06.2
> y HU-07.2); ver `REPORTE.pdf`. Este plan se conserva tal como se escribió.

> **Aviso:** el domingo en la noche concentra reporte, autoevaluación, `AI_USAGE.md`, Lighthouse y la
> etiqueta; es la parte más cargada. Conviene ir **llenando `AI_USAGE.md` y la bitácora mientras se programa**
> (no al final) y terminar el despliegue el domingo a más tardar a media tarde.
>
> **Si el lunes hay demo en vivo:** el backend gratuito de Render se duerme tras 15 min sin tráfico y tarda
> 30–60 s en despertar; basta abrir la URL ~10 minutos antes. Es el único "trabajo" del lunes.
> El plan B (`docker compose up` en una laptop) debe quedar probado el domingo.

> Los commits de las secciones 4 y 5 se mantienen; los días se leen así: «21–22» = sábado y domingo,
> «23–25» = domingo en la noche (los de documentación).

## 4. Plan de commits — Luis (los hago yo, con tu aprobación)

| # | Día | Rama / PR | Mensaje | Qué incluye |
|---|---|---|---|---|
| L01 | 21 | `main` (inicial) | `chore: estructura inicial del monorepo` | carpetas, `.gitignore`, `.env.example`, README mínimo |
| L02 | 21 | `docs/propuesta` | `docs: agrega propuesta ampliada y plan de trabajo` | `docs/propuesta-v2.md`, plan |
| L03 | 21 | `feature/infra-compose-db` | `chore(infra): compose con PostgreSQL y variables de entorno` | `infra/docker-compose.yml`, `.env.example` |
| L04 | 21 | `feature/backend-base` | `feat(backend): esqueleto de FastAPI con configuración y /health` | `backend/app/main.py`, `core/config.py`, `requirements.txt` |
| L05 | 21 | `feature/db-modelos` | `feat(db): modelos SQLAlchemy de usuario, alumno, grupo y catálogos` | `backend/app/models/` |
| L06 | 22 | `feature/db-migraciones` | `feat(db): migración inicial con Alembic y restricciones` | `db/migrations/`, `alembic.ini` |
| L07 | 22 | `feature/db-seed` | `feat(db): datos semilla ficticios y usuarios de prueba` | `db/seed.py` |
| L08 | 22 | `feature/backend-auth` | `feat(backend): registro y login con JWT y hash de contraseñas` | `routers/auth.py`, `core/security.py`, `schemas/` |
| L09 | 22 | `feature/backend-auth` | `feat(backend): autorización por rol con require_role` | `core/deps.py` |
| L10 | 22 | `feature/backend-alumnos` | `feat(backend): CRUD de alumnos con búsqueda, filtros y paginación` | router, servicio, esquemas |
| L11 | 23 | `feature/backend-alumnos` | `feat(backend): historial de inscripciones del alumno` | endpoint + consulta |
| L12 | 23 | `feature/backend-catalogos` | `feat(backend): CRUD de promotores, actividades y semestres (solo admin)` | 3 routers |
| L13 | 23 | `feature/backend-usuarios` | `feat(backend): administración de usuarios y roles` | router usuarios |
| L14 | 23 | `feature/tests-auth` | `test(backend): pruebas de auth, alumnos y permisos 401/403` | `backend/tests/` |
| L15 | 23 | `feature/front-alumnos` | `feat(frontend): pantallas de alumnos (lista, formulario e historial)` | `pages/Alumnos*` |
| L16 | 23 | `feature/front-admin` | `feat(frontend): pantallas de catálogos y usuarios para administrador` | `pages/Catalogos`, `Usuarios` |
| L17 | 24 | `feature/infra-docker` | `chore(infra): Dockerfile del backend y compose completo` | `backend/Dockerfile`, compose |
| L18 | 24 | `feature/infra-deploy` | `docs: notas de despliegue en Render y Neon, CORS y URL pública` | `infra/DEPLOY.md`, README |
| L19 | 25 | `docs/ai-usage` | `docs: declaración de uso de IA y bitácora de prompts` | `AI_USAGE.md`, `CLAUDE.md` |
| L20 | 25 | `docs/seguridad` | `docs: sección de seguridad con revisión OWASP A01 y A02` | `docs/seguridad.md` |
| L21 | 25 | `docs/autoevaluacion` | `docs: autoevaluación con evidencias` | `docs/AUTOEVALUACION.md` |
| — | 25 | tag | `git tag v1.0.0` (con aprobación) | — |

## 5. Plan de commits — Carlos (los hace él, con su cuenta)

> Es una guía de tareas ordenadas para que su historial quede coherente. Cada mensaje debe reflejar
> lo que **realmente** hizo. Si usa un asistente de IA, agrega la línea `Assisted-by:`/`Co-Authored-By:`.

| # | Día | Rama / PR | Mensaje | Qué incluye |
|---|---|---|---|---|
| C01 | 21 | `feature/front-base` | `chore(frontend): proyecto Vite con React, rutas y layout semántico` | `frontend/` base, `header/nav/main/footer` |
| C02 | 21 | `feature/front-estilos` | `feat(frontend): estilos globales responsivos con Flexbox y Grid` | `styles/*.css` (≥ 2 breakpoints) |
| C03 | 21 | `feature/front-auth` | `feat(frontend): cliente de API y contexto de autenticación` | `api/`, `AuthContext`, rutas protegidas |
| C04 | 22 | `feature/front-auth` | `feat(frontend): pantallas de login y registro con validación` | `pages/Login`, `Registro` |
| C05 | 22 | `feature/backend-grupos` | `feat(backend): CRUD de grupos con validación de cruces de horario y aula` | router, servicio, esquemas |
| C06 | 22 | `feature/ci` | `ci: workflow de GitHub Actions con lint, pruebas y build` | `.github/workflows/ci.yml` |
| C07 | 23 | `feature/backend-inscripciones` | `feat(backend): inscripción y evaluación con desempeño calculado` | servicio + endpoints |
| C08 | 23 | `feature/backend-consultas` | `feat(backend): consulta de inscritos por actividad y semestre` | endpoint paginado |
| C09 | 23 | `feature/backend-clima` | `feat(backend): cliente de Open-Meteo con caché y manejo de fallos` | `services/clima.py` |
| C10 | 23 | `feature/front-grupos` | `feat(frontend): pantallas de grupos con formulario dinámico` | `pages/Grupos*` |
| C11 | 23 | `feature/tests-grupos` | `test(backend): pruebas de grupos, inscripciones y clima simulado` | `backend/tests/` |
| C12 | 24 | `feature/backend-tablero` | `feat(backend): endpoint de resumen para el tablero` | `routers/dashboard.py` |
| C13 | 24 | `feature/front-tablero` | `feat(frontend): tablero con gráficas y aviso de clima` | `pages/Tablero` |
| C14 | 24 | `feature/front-inscripciones` | `feat(frontend): inscripción, evaluación y consulta de inscritos` | páginas y componentes |
| C15 | 24 | `feature/infra-front` | `chore(infra): Dockerfile del frontend y despliegue en Vercel` | `frontend/Dockerfile`, notas |
| C16 | 25 | `fix/accesibilidad` | `fix(frontend): correcciones de accesibilidad según Lighthouse` | etiquetas, contraste, `alt` |
| C17 | 25 | `docs/arquitectura` | `docs: diagrama de arquitectura y modelo entidad-relación` | `docs/arquitectura.png`, `db/er.png` |
| C18 | 25 | `docs/reporte` | `docs: secciones de fundamentación, planeación y evaluación del reporte` | `docs/REPORTE` |

**Revisión cruzada:** Luis revisa los PRs de Carlos y Carlos los de Luis (comentarios reales, no solo
"aprobado"). Esa evidencia también cuenta en la tabla de contribución.

## 6. Tabla de contribución (para el reporte)

Se llena con datos reales al final (`git shortlog -sn`, PRs por persona). Acuerdo entre ustedes del
porcentaje; el profesor lo contrasta con el historial y la coevaluación.

| Integrante | Rol | Tareas principales | Commits | PRs | % acordado |
|---|---|---|---|---|---|
| Luis David Reyna Morisco | Cuentas, alumnos, catálogos, BD e infraestructura | _(pendiente)_ | | | |
| Carlos Limones Ayala | Grupos, inscripciones, tablero, clima, CI y diseño | _(pendiente)_ | | | |
