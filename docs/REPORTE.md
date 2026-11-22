# Reporte técnico · Extra-Liebres

> **Borrador.** Lo preparó el agente de documentación de Carlos (Claude Code, Claude Opus 5.5) con datos que se pueden
> comprobar en el repositorio. Luis y Carlos lo revisan, completan lo marcado como _pendiente_ y lo ajustan con sus
> palabras antes de la entrega.

## Portada

| | |
|---|---|
| **Institución** | Tecnológico Nacional de México, Instituto Tecnológico de Ciudad Juárez (ITCJ) |
| **Materia** | Programación Web (AEB-1055) |
| **Docente** | Dr. Roberto Contreras Masse |
| **Proyecto** | Extra-Liebres: registros históricos de actividades extraescolares |
| **Periodo** | Agosto–diciembre de 2026 |
| **Repositorio** | <https://github.com/luisreyna060318-alt/extra-liebres> |
| **Despliegue** | _pendiente: aún no desplegado_ |

| Integrante | Número de control | Rol en el proyecto |
|---|---|---|
| Luis David Reyna Morisco | 22111443 | Cuentas y acceso, alumnos, catálogos, base de datos e infraestructura del backend |
| Carlos Limones Ayala | 22111415 | Grupos, inscripciones, tablero, servicio de clima, CI, frontend e infraestructura del frontend |

---

## 1. Fundamentación

### 1.1 Problema

Hasta 2022 el Departamento de Actividades Extraescolares del ITCJ guardó en papel los registros de los alumnos que
cursaron actividades extraescolares. Desde 2023 se usa SIISAE, pero los registros anteriores nunca se migraron y no se
pueden consultar. En 2024 se hizo una primera versión de Extra-Liebres en PHP y MySQL que funciona, pero tiene la lógica
de consulta dispersa en scripts ligados a las páginas, no tiene una API, los datos no están bien normalizados y a veces
responde lento.

### 1.2 Propuesta

Rehacer Extra-Liebres como una **SPA en React** que consume una **API REST en FastAPI** con **PostgreSQL**, para dar de
alta, consultar, editar y dar de baja alumnos, promotores, actividades, semestres, grupos e inscripciones con su
desempeño. Se agregan inicio de sesión con dos roles (administrador y capturista), un tablero de resumen y un aviso de
clima para las actividades al aire libre. El detalle está en [`propuesta-v2.md`](propuesta-v2.md): 8 épicas, 23 historias
de usuario (19 indispensables y 4 deseables), 11 reglas de negocio (RN-01 a RN-11) y 9 requerimientos no funcionales.

### 1.3 Por qué este stack

| Decisión | Justificación |
|---|---|
| API REST separada del frontend | El problema de la versión anterior era la lógica mezclada con las páginas. Con capas (router → servicio → modelo) cada regla de negocio vive en un solo lugar y se puede probar sin interfaz |
| React + Vite + TypeScript | SPA con rutas (`react-router-dom`), sin librerías de estado: `fetch`, `useState` y un contexto de autenticación bastan. TypeScript detecta al compilar los errores de contrato con la API |
| FastAPI + Pydantic v2 | Validación de entrada con esquemas (422 automático) y documentación OpenAPI en `/docs`, que además sirve para demostrar el `403` del capturista |
| SQLAlchemy 2 + Alembic + PostgreSQL | El modelo tiene restricciones que conviene que cuide la base de datos: `CHECK (horainicio < horatermino)`, `CHECK (calificacion BETWEEN 0 AND 100)`, `UNIQUE (anio, mesinicio)` y la llave compuesta de `alumno_grupo` (RN-03 a RN-05). Alembic deja el esquema versionado |
| `bcrypt` y `PyJWT` | Se evitaron a propósito `passlib` y `python-jose` porque ya no tienen mantenimiento (OWASP A03) |
| Open-Meteo | API de clima sin llave, así que no hay secreto que proteger; se consulta solo desde el backend con caché de 1 hora (RN-10) |
| Docker Compose; Vercel + Render + Neon | `docker compose up` levanta todo en una computadora (plan B de la demo, RNF-04); los tres servicios en la nube tienen plan gratuito |

---

## 2. Planeación

- **Backlog:** 24 issues en GitHub; 23 son las historias `HU-xx.x` de la propuesta y el otro es la propuesta misma.
- **Reparto en rebanadas verticales:** cada quien hizo sus funciones de punta a punta (backend, pruebas y pantalla), para
  que ninguno dependiera de que el otro terminara una capa completa. El reparto está en
  [`plan-de-trabajo.md`](plan-de-trabajo.md) (commits L01–L21 de Luis y C01–C18 de Carlos).
- **Alcance:** con dos días de trabajo (sábado 21 y domingo 22 de noviembre) se decidió dejar en el backlog las 4 historias
  deseables (HU-04.4, HU-05.3, HU-06.2 y HU-07.2); de HU-04.4 y HU-05.3 el backend ya cubre una parte. Lo que nunca se
  recortaba: autenticación, CRUD, clima, tablero, Docker, CI y la declaración de IA.
- **Flujo de Git:** `main` solo recibe cambios por pull request revisado por la otra persona; ramas `feature/<área>-<tema>`,
  Conventional Commits en español y una línea `Co-Authored-By:` en los commits hechos con IA.
- **Contexto para la IA:** [`CLAUDE.md`](../CLAUDE.md) fija el stack y las reglas de código, y
  [`prompts.md`](prompts.md) guarda las plantillas de prompts (P1–P13) que se usaron.

---

## 3. Ejecución

### 3.1 Arquitectura

> **Figura 1.** Diagrama de arquitectura: `docs/arquitectura.png` (**se agrega con el PR de diagramas**).

El navegador carga la SPA (Vercel o el contenedor `frontend` con nginx) y esta llama a la API (Render o el contenedor
`backend`), que es la única que habla con PostgreSQL (Neon o el contenedor `db`) y con Open-Meteo.

Estructura del monorepo:

```
frontend/   React + Vite + TypeScript (src/pages, components, api, context, hooks, utils, styles)
backend/    FastAPI: app/{routers, services, models, schemas, core} y tests/
db/         migraciones de Alembic y seed.py (datos ficticios)
infra/      docker-compose.yml y guía de despliegue (DEPLOY.md)
docs/       propuesta, plan, prompts, seguridad y este reporte
.github/    flujo de CI
```

### 3.2 Frontend

- **15 rutas** en `frontend/src/App.tsx`: `/login`, `/registro`, `/` (tablero), `/alumnos`, `/alumnos/nuevo`,
  `/alumnos/:nocontrol`, `/alumnos/:nocontrol/editar`, `/grupos`, `/grupos/nuevo`, `/grupos/:id`, `/grupos/:id/editar`,
  `/consultas`, `/catalogos` y `/usuarios` (estas dos, solo administrador) y una página de "no encontrada".
- **Cliente de API** (`src/api/cliente.ts`): un envoltorio de `fetch` que agrega el token, convierte los errores HTTP en
  mensajes legibles y cierra la sesión ante un `401`. Cada recurso tiene su archivo en `src/api/`.
- **Estados de carga, error y vacío** en toda vista que consulta la API (componente `Estado` y hook `useApi`).
- **Formulario dinámico de grupos** (HU-04.2): si la actividad es deportiva pide una instalación de una lista; si es
  cultural o cívica, un aula de texto; si es al aire libre muestra el pronóstico del clima.
- **Tablero** (HU-07.1): totales, dos gráficas de barras con Recharts (la única dependencia agregada además de la
  plantilla de Vite y `react-router-dom`) y el pronóstico. Cada gráfica tiene una tabla con los mismos datos.
- **Estilos:** CSS externo, *mobile first*, con breakpoints en 600 px y 1024 px, Flexbox y Grid, foco visible y enlace
  "Saltar al contenido". Las pantallas se revisaron a 360 px sin desplazamiento horizontal (PR #36, #39 y #41).

### 3.3 Backend

- **24 rutas y 40 operaciones** (contadas desde el esquema OpenAPI de la aplicación), repartidas en 12 routers: auth,
  usuarios, alumnos, promotores, extraescolares, semestres, grupos, inscripciones, consultas, dashboard, clima y health.
- **Capas:** los routers solo traducen HTTP; la lógica está en `services/` (por ejemplo `grupo_service.validar_cruces` y
  `desempeno.calcular_desempenio`) y los modelos en `models/`. Los esquemas de entrada y de salida son distintos y
  ninguno expone `password_hash`.
- **Reglas de negocio en el servidor:** cruces de horario de promotor y de lugar (409 con el grupo en conflicto, RN-03),
  inscripción única y solo de alumnos activos (RN-04), desempeño calculado por el servidor a partir de la calificación
  (RN-05; si el cliente manda `desempenio` la respuesta es 422), baja lógica (RN-02, RN-08) y lugar válido según el tipo
  de actividad.
- **Clima:** `services/clima.py` consulta Open-Meteo con un tiempo límite de 5 s y guarda la respuesta 1 hora; si el
  servicio falla, responde `{"disponible": false, "mensaje": "Pronóstico no disponible"}` y el resto sigue funcionando.
- **Códigos HTTP:** 200/201/204 en éxito, 401 sin sesión, 403 sin permiso, 404 si no existe, 409 en conflicto y 422 en
  validación.

### 3.4 Base de datos

> **Figura 2.** Modelo entidad-relación: `docs/er.png` (**se agrega con el PR de diagramas**).

Siete tablas: `usuario`, `alumno`, `promotor`, `extraescolar`, `semestre`, `grupo` y `alumno_grupo` (la relación N:M
entre alumno y grupo, que guarda calificación y desempeño). El esquema se crea con una sola migración de Alembic
(`db/migrations/versions/20261121_0001_esquema_inicial.py`). `db/seed.py` genera datos **ficticios**: 200 alumnos,
10 promotores, 6 semestres (2024 a 2026), grupos sin cruces y una cuenta por rol.

### 3.5 Seguridad

La revisión completa está en [`seguridad.md`](seguridad.md) (OWASP Top 10:2025: A01, A02 y A03). En resumen:

- La autorización se valida **siempre en el servidor** con las dependencias `get_current_user` y `require_role`. De las
  40 operaciones, 3 son públicas, 26 piden sesión y 11 son solo de administrador; una prueba automática
  (`backend/tests/test_matriz_permisos.py`) las recorre todas y falla si alguna nueva queda sin proteger.
- Contraseñas con `bcrypt`, JWT con `PyJWT` y expiración de 60 minutos; el rol se lee de la base en cada petición.
- Configuración por variables de entorno; con `ENTORNO=produccion` el backend no arranca con las claves de ejemplo.
  CORS limitado a los orígenes de `CORS_ORIGINS`.
- Limitaciones conocidas (sin límite de intentos de login, token en `localStorage`, sin revocación de tokens):
  documentadas en la misma página.

### 3.6 Contenedores y despliegue

- `docker compose up --build` levanta tres servicios: `db` (`postgres:16-alpine`), `backend` (`python:3.12-slim`; corre
  como usuario sin privilegios, aplica migraciones y carga el seed) y `frontend` (construido con `node:22-alpine` y
  servido por `nginxinc/nginx-unprivileged:1.28-alpine`).
- Según el PR #40, el arranque desde cero tardó 46 s y con caché 19 s (límite de la materia: 180 s); este borrador no
  volvió a medirlo.
- Despliegue planeado: backend en Render (`render.yaml`), base en Neon y frontend en Vercel (`frontend/vercel.json`); los
  pasos están en [`DEPLOY.md`](../infra/DEPLOY.md). **Estado:** _pendiente: aún no desplegado_.

---

## 4. Evaluación

### 4.1 Pruebas

| Qué | Resultado | Cómo se obtuvo |
|---|---|---|
| Pruebas del backend (pytest) | **318 pruebas, 318 pasan**, en 17 archivos de `backend/tests/` | `python -m pytest -q` desde `backend/`, sobre `main` en `698c691` |
| Estilo del backend (ruff) | Sin errores | `ruff check backend db` |
| Endpoints cubiertos | Las 40 operaciones se llaman en la matriz de permisos | `backend/tests/test_matriz_permisos.py` |
| Pruebas de frontend | No hay pruebas automáticas; las pantallas se probaron a mano en el navegador | PR #36, #39, #41 y #43 |
| Lighthouse (accesibilidad ≥ 90, RNF-02) | _pendiente_ | — |

Pruebas por archivo: alumnos 49, promotores 37, extraescolares 34, semestres 29, inscripciones 27, grupos 20, auth 18,
desempeño 16, usuarios 16, dashboard 14, matriz de permisos 14, grupos (lugar) 13, clima 12, consultas 8, config 6,
security 3 y health 2. Usan SQLite en memoria y simulan Open-Meteo, así que no necesitan red.

### 4.2 Integración continua

`.github/workflows/ci.yml` corre en cada `push` y en cada pull request con tres trabajos: **backend** (Python 3.12,
`ruff` y `pytest`), **frontend** (Node 22, `npm ci`, lint y build) e **imágenes de Docker** (valida `docker compose config`
y construye las imágenes del backend y del frontend sin publicarlas). Las tres corridas más recientes sobre `main`
terminaron en verde (`gh run list --branch main`).

### 4.3 Problemas encontrados

1. **Marcas de conflicto subidas a una rama.** Al fusionar `main` en la rama del tablero, el commit `774eaee` llevó
   `<<<<<<<` dentro de `backend/app/main.py`; la CI falló en `ruff` con `invalid-syntax` y se corrigió en `1ceea02`.
2. **Una clase CSS definida tres veces.** `.boton-peligro` tenía estilos distintos en `alumnos.css`, `admin.css` e
   `inscripciones.css`, y el botón "Dar de baja" quedó como un bloque rojo sin texto. Build, lint y pruebas pasaban; se
   vio en el navegador y se corrigió en `2ef8618`.
3. **Catálogos sin los registros inactivos.** El servidor oculta por defecto los promotores y actividades desactivados,
   y un grupo viejo perdía el nombre de su promotor; el frontend los pide con `estado=todos` (`63a4de2`).
4. **Puerto 5432 ocupado** por un PostgreSQL local: se hizo configurable con `DB_HOST_PORT` (PR #40).
5. **Tamaño del bundle:** con Recharts, `npm run build` avisa de un archivo de 660 kB (PR #39); no se dividió para no
   agregar complejidad.

### 4.4 Lecciones

- "Las pruebas pasan" no significa que la pantalla se vea bien ni que la prueba detecte el error: hay que revisar en el
  navegador y, a veces, romper el código a propósito para comprobar que la prueba falla.
- Los pasos que modifican el repositorio no se encadenan sin detenerse al primer error, y se revisa antes de subir.
- Un contrato escrito en un solo lugar (por ejemplo `INSTALACIONES` en `core/constantes.py`) evita que cliente y servidor
  se contradigan.

_Pendiente: Luis y Carlos agregan sus propias lecciones._

### 4.5 Trabajo futuro

- Implementar las historias deseables: editar y eliminar grupos desde el frontend (HU-04.4), búsqueda global (HU-06.2) y
  exportación CSV/XML (HU-07.2).
- Límite de intentos de inicio de sesión, token en cookie `HttpOnly` y revocación de tokens (ver `seguridad.md`).
- Pruebas automáticas del frontend y medición con Lighthouse en la CI.
- Búsqueda de alumnos que no distinga acentos.
- Dividir el bundle del frontend (cargar el tablero aparte).

---

## 5. Uso de IA (resumen)

La declaración completa está en [`AI_USAGE.md`](../AI_USAGE.md). Ambos integrantes usamos **Claude Code** en la app de
escritorio de Claude, como agente que edita archivos y ejecuta comandos en el repositorio:

- **Luis** trabajó con Claude Sonnet 5.5 y con subagentes para tareas acotadas (revisión independiente, catálogos y
  pantallas), verificando cada resultado antes de comitear.
- **Carlos** trabajó con un orquestador (Claude Sonnet 5.5) que repartió las tareas a subagentes: Claude Sonnet 5.5
  (frontend, clima, tablero e infraestructura del frontend), Claude Opus 5.5 (grupos, inscripciones y consultas en
  backend y frontend, y esta documentación) y Claude Haiku 5.5 (CI).
- Los commits hechos con IA llevan `Co-Authored-By:`; la medición por carpeta está en la sección 6 de `AI_USAGE.md` y la
  reflexión crítica de cada integrante, en la sección 7.

La IA no es autora (política de autoría de la ACM): los integrantes respondemos por todo el contenido y debemos poder
explicarlo en la demo.

---

## 6. Contribución individual

Datos tomados del repositorio el 21 de noviembre de 2026, sobre `main` en `698c691`.

| Integrante | Tareas principales | Commits (`git shortlog -sn --all`) | Commits sin fusiones | PR fusionados como autor | Revisiones de PR | % acordado |
|---|---|---|---|---|---|---|
| Luis David Reyna Morisco | Modelos, migración y seed; auth y roles; alumnos; catálogos; usuarios; Docker del backend y despliegue; pantallas de alumnos, catálogos y usuarios; seguridad | 28 | 27 | 8 | 8 | _pendiente: lo acuerdan Luis y Carlos_ |
| Carlos Limones Ayala | Base del frontend y auth; grupos; inscripciones y consultas; tablero; clima; CI; Docker del frontend; detalle de grupo y consultas | 50 (31 como "Carlos Limones Ayala" y 19 como "LimonesCarlos") | 23 | 11 | 8 | _pendiente: lo acuerdan Luis y Carlos_ |

Notas para leer la tabla:

- Los 19 commits de "LimonesCarlos" son las fusiones de pull requests hechas en GitHub: la cuenta de Carlos fusionó los
  19 PR, incluidos los 8 de Luis. Por eso la columna "commits sin fusiones" (`git shortlog -sn --no-merges`) refleja
  mejor el trabajo de cada uno.
- PR fusionados por autor: `gh pr list --state merged --json author`. Revisiones: `gh pr list --state all --json reviews`.

_Pendiente: Luis y Carlos revisan esta tabla y acuerdan el porcentaje._

---

## 7. Coevaluación

_Plantilla: cada integrante evalúa al otro._

| Evaluador | Evaluado | Cumplimiento (1–5) | Calidad (1–5) | Comunicación (1–5) | Comentario |
|---|---|---|---|---|---|
| Luis David Reyna Morisco | Carlos Limones Ayala | | | | |
| Carlos Limones Ayala | Luis David Reyna Morisco | | | | |

---

## 8. Autoevaluación

Ver `docs/AUTOEVALUACION.md` (se agrega en otro PR).

---

## 9. Referencias

Alembic. (s. f.). *Alembic documentation*. https://alembic.sqlalchemy.org/

Association for Computing Machinery. (s. f.). *ACM policy on authorship*.
https://www.acm.org/publications/policies/new-acm-policy-on-authorship

Conventional Commits. (s. f.). *Conventional Commits 1.0.0*. https://www.conventionalcommits.org/es/v1.0.0/

Docker. (s. f.). *Docker Compose*. https://docs.docker.com/compose/

FastAPI. (s. f.). *FastAPI documentation*. https://fastapi.tiangolo.com/

Meta Open Source. (s. f.). *React documentation*. https://react.dev/

Open-Meteo. (s. f.). *Weather forecast API*. https://open-meteo.com/en/docs

OWASP Foundation. (s. f.). *OWASP Top 10:2025*. https://owasp.org/Top10/2025/

SQLAlchemy. (s. f.). *SQLAlchemy 2.1 documentation*. https://docs.sqlalchemy.org/en/21/

The PostgreSQL Global Development Group. (s. f.). *PostgreSQL 16 documentation*. https://www.postgresql.org/docs/16/

Wiggins, A. (s. f.). *The twelve-factor app*. https://12factor.net/
