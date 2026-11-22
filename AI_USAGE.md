# Declaración de uso de IA

> Este documento declara cómo usamos asistentes de IA en el proyecto, como pide la materia
> (Programación Web, AEB-1055). La IA no es autora: los autores humanos respondemos por la exactitud de
> todo el material, incluido el generado por la herramienta. Si no podemos explicar un fragmento en la
> demo, no cuenta como nuestro.
>
> **Estado:** actualizado el 22 de noviembre de 2026 (commits de `main` hasta `8155d67`). Las celdas marcadas
> como _pendiente_ las completa cada integrante antes de la etiqueta `v1.0.0`.

## 1. Herramientas y modelos

| Herramienta | Modelo(s) | Quién la usó | Para qué |
|---|---|---|---|
| Claude Code (app de escritorio de Claude) | Claude Sonnet 5.5 | Luis David Reyna Morisco | Análisis de requisitos, documentos de planeación, estructura del repositorio, código, seguridad, despliegue, prueba de humo y reporte técnico |
| Claude Code, subagentes (copias aisladas del repositorio) | Claude Sonnet 5.5 | Luis | Revisión independiente del código base (solo lectura), catálogos del backend, pantallas de alumnos y pantallas de catálogos y usuarios del frontend |
| Claude Code (app de escritorio de Claude), agente que edita archivos y ejecuta comandos | Claude Sonnet 5.5 (orquestador) | Carlos Limones Ayala | Recibe las tareas de Carlos, las reparte a subagentes, fusiona `main` en las ramas y resuelve los conflictos |
| Claude Code, subagentes | Claude Sonnet 5.5 | Carlos | Frontend base y autenticación, servicio de clima, backend del tablero, frontend de grupos, frontend del tablero, infraestructura del frontend, diagramas y backlog |
| Claude Code, subagentes | Claude Opus 5.5 | Carlos | Grupos del backend (cruces de horario y lugar); inscripciones, consulta de inscritos y validación del lugar por tipo de actividad; frontend del detalle de grupo y de la consulta; agente de documentación (esta bitácora y el borrador del reporte) |
| Claude Code, subagentes | Claude Haiku 5.5 | Carlos | Integración continua (CI) con GitHub Actions |

## 2. Harness y modo de uso

- **Luis:** Claude Code en la app de escritorio de Claude, como **agente que edita archivos y ejecuta
  comandos** (Git, Docker, `gh`, Python, Node) sobre el repositorio local. Cada commit lo aprueba Luis
  antes de hacerse y cada cambio se revisa antes de subirlo. El agente principal lanza subagentes para tareas
  acotadas, **verifica su trabajo** (corre las pruebas por su cuenta, lee el código, hace pruebas de mutación y pruebas
  contra PostgreSQL) y solo entonces se prepara el commit. Las revisiones de los PR de Carlos también se hicieron con
  Claude Code y así se dice en cada comentario.
- **Carlos:** Claude Code en la app de escritorio de Claude, como **agente que edita archivos y ejecuta
  comandos** (Git, `gh`, Node y Python) sobre el repositorio local. Un agente orquestador (Claude Sonnet 5.5)
  reparte las tareas a subagentes, cada uno con su modelo (ver sección 1), que trabajan en ramas separadas
  y abren PRs con la cuenta de Carlos. Carlos revisa cada cambio antes de fusionarlo.

## 3. Archivos de contexto e instrucciones

| Archivo | Para qué sirve |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Contexto fijo para el asistente: stack, estructura, reglas de código y de seguridad |
| [`docs/propuesta-v2.md`](docs/propuesta-v2.md) | Fuente de verdad de los requisitos (historias, reglas, modelo y endpoints) |
| [`docs/prompts.md`](docs/prompts.md) | Plantillas de prompts estructurados (P1–P13) que usamos y corregimos |
| [`docs/plan-de-trabajo.md`](docs/plan-de-trabajo.md) | Cronograma, flujo de Git y plan de commits |

Servidores MCP o *skills* adicionales: _pendiente: cada integrante confirma si usó alguno_. Para el reporte técnico se usaron herramientas locales
fuera del repositorio (python-docx, PyMuPDF y puppeteer-core en carpetas temporales, Microsoft Word y Edge); no se agregó ninguna dependencia al proyecto.
En el caso de Carlos, los subagentes de frontend probaron las pantallas en el navegador integrado de la app de
Claude (lo dicen los PR #36, #39 y #41) y usaron `gh` para abrir los PR.

## 4. Bitácora de prompts significativos

| Fecha | Integrante | Herramienta / modelo | Prompt (resumen fiel) | Archivos afectados | Ajustes humanos |
|---|---|---|---|---|---|
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | Se entregó la propuesta (Tarea 1), el ejemplo de requerimientos del profesor, los requisitos del proyecto final y el manual del curso; se pidió detectar lo que falta, dar opciones de implementación, estructurar prompts y planear los commits de ambos integrantes | `docs/propuesta-v2.md`, `docs/plan-de-trabajo.md`, `docs/prompts.md` | _Pendiente: Luis anota aquí lo que corrigió o decidió al revisar_ |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | Crear la estructura inicial del monorepo, `.gitignore`, `.env.example` y README, y publicar el repositorio | `.gitignore`, `.env.example`, `README.md`, carpetas base | _Pendiente_ |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | Copiar la planeación al repositorio y generar `CLAUDE.md` y este documento | `CLAUDE.md`, `AI_USAGE.md`, `docs/` | _Pendiente_ |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | P1: modelos SQLAlchemy, migración inicial con Alembic y datos semilla ficticios | `backend/app/models/`, `db/migrations/`, `db/seed.py` | Aprobó los commits tras ver el resumen. Se aplicaron los hallazgos confirmados de la revisión independiente (ver fila siguiente) |
| 2026-11-21 | Luis | Claude Code, subagente de solo lectura / Claude Sonnet 5.5 | Revisión independiente del código base contra la especificación, buscando incoherencias, fallas de seguridad, errores del seed y dependencias riesgosas | (ninguno: solo lectura) | Informó 14 hallazgos. El agente principal los verificó en el código: se aplicaron 11 (clave de producción, números de control ficticios, lugares coherentes, `CHECK` del RFC, entre otros) y 3 se pospusieron |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | P2: registro, inicio de sesión con JWT y autorización por rol; administración de usuarios | `backend/app/core/security.py`, `deps.py`, `routers/auth.py`, `routers/usuarios.py` | Se comprobó con 3 pruebas de mutación y una prueba de extremo a extremo contra PostgreSQL. Al revisar el diff se detectó y corrigió un commit con saltos de línea de Windows (CRLF) |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | P3: CRUD de alumnos con búsqueda, filtros, paginación, baja lógica e historial | `backend/app/routers/alumnos.py`, `services/alumno_service.py`, `schemas/alumno.py` | 6 pruebas de mutación y 19 comprobaciones contra PostgreSQL. Se documentó una limitación detectada: la búsqueda distingue acentos |
| 2026-11-21 | Luis | Claude Code, subagente de catálogos / Claude Sonnet 5.5 | Implementar los catálogos de promotores, actividades y semestres siguiendo el patrón de alumnos | `backend/app/routers/{promotores,extraescolares,semestres}.py`, servicios, esquemas y pruebas | El agente principal no aceptó el reporte: corrió las 209 pruebas, leyó todo el código, hizo 6 pruebas de mutación y 28 comprobaciones contra PostgreSQL antes de comitear |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | Docker y despliegue: Dockerfile del backend, `docker compose up`, `render.yaml` y guía de despliegue | `backend/Dockerfile`, `backend/entrypoint.sh`, `compose.yaml`, `infra/`, `render.yaml` | Probado desde cero (128 s). Se corrigió una fuga de secretos en los mensajes de error de la configuración y una prueba mía que no detectaba esa fuga (ver reflexión) |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | Revisión de los PR #29 a #36 de Carlos: leer cada diff, correr pruebas, `npm ci`, lint y build en copias limpias y simular la fusión en orden | comentarios en los PR | Se publicaron los comentarios con la línea "revisión hecha con ayuda de Claude Code" |
| 2026-11-21 | Luis | Claude Code, 2 subagentes en paralelo / Claude Sonnet 5.5 | Pantallas del frontend: alumnos (lista con búsqueda, filtros y paginación, formulario y historial) y catálogos (3 pestañas) y usuarios (administrador), con validación en el cliente y estados de carga, error y vacío | `frontend/src/pages/Alumno*.tsx`, `Alumnos.tsx`, `Catalogos.tsx`, `catalogos/`, `Usuarios.tsx`, `api/alumnos.ts`, `api/admin.ts`, `components/` | Ambos subagentes reportaron "lint y build limpios" sin poder probar en un navegador. El agente principal las probó en el navegador contra el backend real y encontró un error (cancelar la confirmación de baja dejaba la pantalla desfasada y ya no se podía volver a abrir), que corrigió |
| 2026-11-21 | Carlos | Claude Code (subagente de frontend) / Claude Sonnet 5.5 | Prompt P8: crear la base del frontend (commits C01 a C04 del plan): proyecto Vite + React + TypeScript con react-router, rutas y layout semántico con navegación por rol; estilos globales responsivos (Flexbox y Grid, 2 breakpoints, variables y foco visible); cliente de API con token y manejo de errores, contexto de autenticación, hook `useApi`, componente `Estado` y rutas protegidas; pantallas de login y registro con validación en cliente. Además, completar mis filas de esta declaración. Se pidió respetar los contratos de `/api/auth/*` del backend, no agregar dependencias sin justificar y que el token nunca se imprima | `frontend/` (C01 y C02 en el PR #32 `feature/front-base`; `src/api/`, `AuthContext`, `useApi`, `Estado`, `pages/Login` y `pages/Registro` en el PR #33 `feature/front-auth`), `AI_USAGE.md` | Las ramas se fusionaron sin commits extra. Login y registro se probaron solo contra una API simulada, no contra el backend real. _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de CI) / Claude Haiku 5.5 | PR #29 (C06): workflow de GitHub Actions con un job de backend (Python 3.12, `ruff check backend db` y `pytest`) y uno de frontend (Node 22, `npm ci`, lint y build) que se omite si aún no existe `frontend/package.json`; permisos mínimos y sin secretos | `.github/workflows/ci.yml` | Se fusionó sin commits extra. _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de clima) / Claude Sonnet 5.5 | PR #30 (HU-08.1, RN-10, P6): `GET /api/clima` que consulta Open-Meteo para Ciudad Juárez con `httpx` y timeout de 5 s, caché de 1 hora (las fallas no se guardan) y respuesta `disponible: false` si el servicio falla; pruebas sin red | `backend/app/{services/clima.py, routers/clima.py, schemas/clima.py, main.py}`, `backend/tests/test_clima.py` | El orquestador fusionó `main` en la rama y resolvió el conflicto de `main.py` dejando los dos routers (commit `8a5a7dc`). _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de grupos) / Claude Opus 5.5 | PR #31 (P4: HU-04.1, HU-04.3, HU-04.4, RN-03, RN-08): CRUD de grupos con validación de cruces de promotor y de lugar (409 con el grupo en conflicto), 422 si la hora de término no es posterior, 404 de catálogos inexistentes y 409 al borrar un grupo con inscritos | `backend/app/{schemas/grupo.py, services/grupo_service.py, routers/grupos.py, main.py}`, `backend/tests/test_grupos.py` | El orquestador fusionó `main` dos veces y resolvió los conflictos de `main.py` conservando todos los routers (`ba90bd7`, `b078c10`). Quedó abierta la pregunta del PR: ¿se bloquean grupos con promotor o actividad inactivos? _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente del tablero, backend) / Claude Sonnet 5.5 | PR #34, parte backend del P7 (HU-07.1): `GET /api/dashboard/resumen?semestre=<id>` con consultas agregadas de SQLAlchemy (COUNT, GROUP BY, AVG), semestre por omisión el más reciente, 404 si no existe, caso sin semestres con promedio null, distribución con las 5 categorías y pruebas con totales exactos. No incluye `GET /api/semestres` | `backend/app/{schemas/dashboard.py, services/dashboard_service.py, routers/dashboard.py, main.py}`, `backend/tests/test_dashboard.py` | Al fusionar `main`, el orquestador subió un commit con marcas de conflicto en `main.py` (`774eaee`); la CI falló y se corrigió en `1ceea02` (ver reflexión, sección 7). _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de inscripciones) / Claude Opus 5.5 | PR #35 (P5 y P9 punto 3): endpoints de inscripción, evaluación con desempeño calculado en el servidor (RN-04, RN-05) y consulta de inscritos paginada por actividad y semestre (HU-06.1); validar en el servidor que el lugar de un grupo deportivo esté en la lista de instalaciones (422). Con pruebas pytest | `backend/app/{schemas/inscripcion.py, schemas/consulta.py, services/inscripcion_service.py, services/consulta_service.py, services/grupo_service.py, routers/inscripciones.py, routers/consultas.py, routers/grupos.py, core/errores.py, core/constantes.py, main.py}`, `backend/tests/{test_inscripciones.py, test_consultas.py, test_grupos_lugar.py}` | El orquestador le dio una lista de 4 instalaciones; el agente leyó `INSTALACIONES` en `core/constantes.py` (6) y usó la real. El orquestador fusionó `main` y resolvió el conflicto de `main.py` (`2e9269b`). _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de grupos, frontend) / Claude Sonnet 5.5 | PR #36, P9 lado cliente: pantallas de grupos (lista con filtros y paginación; formulario de alta y edición dinámico según tipo de actividad y al aire libre, con pronóstico; componente `CampoFormulario`; validación en cliente y avisos para 409 y 422; estados de carga, error y vacío), usando los contratos de las ramas de backend y dejando las llamadas a catálogos aisladas | `frontend/src/pages/{Grupos,GrupoFormulario}.tsx`, `frontend/src/components/{CampoFormulario,Pronostico}.tsx`, `frontend/src/api/{grupos,catalogos}.ts`, `frontend/src/utils/grupos.ts`, `frontend/src/types.ts`, `frontend/src/App.tsx`, `frontend/src/styles/{grupos,componentes,index}.css` | Se probó solo contra una API simulada. Al fusionar `main`, el orquestador cambió `api/catalogos.ts` para pedir promotores y actividades con `estado=todos`, porque el servidor oculta los inactivos y un grupo viejo perdía el nombre de su promotor (`63a4de2`). _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente del tablero, frontend) / Claude Sonnet 5.5 | PR #39: reemplazar el placeholder del tablero con selector de semestre, tarjetas de totales, gráficas de barras (inscritos por actividad y desempeño) con Recharts y pronóstico del clima con aviso de lluvia, usando `/api/dashboard/resumen`, `/api/semestres` y `/api/clima`; bloques independientes con carga/error/vacío, accesibilidad (título, texto alternativo y tabla), responsive desde 360 px. Verificado contra el backend real | `frontend/package.json`, `frontend/package-lock.json`, `frontend/src/pages/Tablero.tsx`, `frontend/src/api/{dashboard,catalogos}.ts`, `frontend/src/types.ts`, `frontend/src/components/{TarjetaIndicador,GraficaBarras,Estado,Pronostico}.tsx`, `frontend/src/styles/{tablero,index}.css` | Única dependencia nueva: `recharts`, justificada en el PR. Se fusionó sin commits extra; queda el aviso de tamaño del bundle (660 kB). _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de infraestructura del frontend) / Claude Sonnet 5.5 | PR #40 (C15): Dockerfile y nginx del frontend, `vercel.json`, servicio en compose, `DB_HOST_PORT`, job de CI que construye imágenes, docs de despliegue | `frontend/{Dockerfile, nginx.conf, .dockerignore, vercel.json}`, `infra/docker-compose.yml`, `.github/workflows/ci.yml`, `infra/DEPLOY.md`, `README.md`, `.env.example`, `.gitattributes` | Se aceptó la estructura de dos etapas con nginx-unprivileged; se verificó con `docker compose up --build -d --wait` y `curl` (46 s en frío, 19 s con caché). Vercel no se probó. _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de detalle de grupo y consultas) / Claude Opus 5.5 | PR #41 (C14): implementar el detalle de grupo `/grupos/:id` (datos, inscritos, inscribir con buscador y 409, evaluar 0–100 con el desempeño calculado por el servidor, quitar con confirmación `confirmar=true`) y la consulta `/consultas` con filtros y paginación; accesible y responsive desde 360 px; probar contra el backend real en Docker | `frontend/src/App.tsx`, `frontend/src/pages/{GrupoDetalle,Consultas,Grupos}.tsx`, `frontend/src/components/{FilaInscrito,InscribirAlumno}.tsx`, `frontend/src/api/{inscripciones,consultas}.ts`, `frontend/src/utils/inscripciones.ts`, `frontend/src/styles/{inscripciones,grupos}.css` | Se fusionó sin commits extra. Su `inscripciones.css` define `.boton-peligro` con fondo rojo, lo que más tarde chocó con `alumnos.css` (ver la fila siguiente). _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (orquestador) / Claude Sonnet 5.5 | Revisión del PR #43 de Luis en el navegador: el botón "Dar de baja" de Alumnos se veía como un bloque rojo sin texto | `frontend/src/pages/Alumnos.tsx`, `frontend/src/styles/alumnos.css` (commit `2ef8618`) | La causa era `.boton-peligro` definida tres veces con estilos distintos; el enlace de Alumnos pasó a `.boton-texto-peligro`. Build, lint y pruebas pasaban antes del arreglo (ver reflexión). _pendiente: Carlos revisa_ |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | PR #42: revisión de seguridad con el OWASP Top 10:2025 (A01, A02 y A03), matriz de permisos de las 40 rutas generada por una prueba automática y `AI_USAGE.md` al día | `docs/seguridad.md`, `backend/tests/test_matriz_permisos.py`, `AI_USAGE.md` | Se verificó rompiendo la protección a propósito de tres maneras distintas (pruebas de mutación) |
| 2026-11-21 | Carlos | Claude Code (subagente de diagramas) / Claude Sonnet 5.5 | PR #44: diagrama de arquitectura, modelo entidad-relación generado desde la migración y borrador de la autoevaluación | `docs/arquitectura.png`, `db/er.png`, `docs/diagramas/`, `docs/AUTOEVALUACION.md` | _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (agente de documentación) / Claude Opus 5.5 | PR #45: bitácora de IA y reflexión crítica de Carlos, y borrador del reporte técnico | `AI_USAGE.md`, `docs/REPORTE.md` | _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de accesibilidad) / Claude Sonnet 5.5 | PR #46: correcciones de accesibilidad y reporte de Lighthouse con puntajes antes y después, más comprobaciones con axe-core | `docs/lighthouse.md`, `docs/lighthouse/`, `frontend/public/robots.txt`, `frontend/src/components/{Confirmacion,Layout}.tsx` y estilos | El reporte aclara que las diferencias de rendimiento son ruido de la medición y que no se presume una mejora. _pendiente: Carlos revisa_ |
| 2026-11-21 | Carlos | Claude Code (subagente de frontend) / Claude Sonnet 5.5 | PR #47: eliminar un grupo desde la lista (HU-04.4) | `frontend/src/api/grupos.ts`, `frontend/src/components/Confirmacion.tsx`, `frontend/src/pages/Grupos.tsx`, `frontend/src/styles/grupos.css` | _pendiente: Carlos revisa_ |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | PR #48: documentar las URLs públicas del despliegue (Vercel, Render y Neon) y los pasos de Render y Neon que sí funcionaron | `README.md`, `infra/DEPLOY.md` | Los pasos se corrigieron con lo que funcionó al desplegar; después se corrigió el formato de la sección de Render (`8d640d0`) |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | PR #49: script de prueba de humo del sistema desplegado | `infra/prueba_humo.py`, `infra/DEPLOY.md` | Se corrigió que la prueba quitara las inscripciones antes de limpiar y que rechazara una URL `http://` ajena (`9f3d311`). Luis la corrió el 22 de noviembre contra producción: 41 de 41 comprobaciones correctas |
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | PR #50: cabeceras de seguridad HTTP en el backend y en Vercel, con una política de contenido (CSP) estricta (OWASP A02) | `backend/app/main.py`, `backend/tests/test_cabeceras.py`, `frontend/vercel.json`, `docs/seguridad.md` | La prueba de cabeceras se verificó con una mutación y la CSP se probó en el navegador en las 8 pantallas y el tablero con gráficas, sin violaciones (ver `docs/seguridad.md`) |
| 2026-11-22 | Luis | Claude Code / Claude Sonnet 5.5 | Reporte técnico: auditar el borrador contra el repositorio, verificar cifras (pruebas, operaciones, PR, commits y CI), armar las figuras y generar `docs/REPORTE.docx` y `docs/REPORTE.pdf` con el formato de la práctica de Luis; actualizar el tablero de GitHub Projects y esta declaración | `docs/REPORTE.pdf`, `docs/REPORTE.docx`, `docs/AUTOEVALUACION.md`, `AI_USAGE.md` | Luis aportó las capturas de Vercel, Render y Neon, la fecha de la prueba de humo, el porcentaje de contribución acordado con Carlos y la coevaluación, y revisó el resultado antes de subirlo |

_(Se agregan filas con cada prompt importante: fecha, quién, herramienta y modelo, resumen fiel del
prompt, archivos y qué cambiamos nosotros después.)_

## 5. Marcado en commits

Los commits con código o texto generado por IA terminan con una línea final:

- `Co-Authored-By: Claude <modelo> <noreply@anthropic.com>` (la agrega Claude Code, con el modelo que se usó), o
- `Assisted-by: <herramienta/modelo>` para cualquier otra herramienta.

Para ver cuáles son: `git log --grep="Co-Authored-By\|Assisted-by"`.

## 6. Estimación de código generado por IA por carpeta

Medido con el historial de Git (líneas añadidas en commits marcados con `Co-Authored-By` o `Assisted-by`) al 22 de noviembre de 2026, con los commits de `main` hasta `8155d67`:

| Carpeta | % con IA | Líneas añadidas | Nota |
|---|---|---|---|
| `backend/` | ~100 % | 5 662 | Todo el código lo escribió el asistente; las personas dirigen, revisan, prueban y aprueban cada commit |
| `frontend/` | ~100 % | 9 377 | Incluye `package-lock.json` (generado por npm) |
| `db/` | ~100 % | 560 | Modelos, migración y datos semilla |
| `infra/` y raíz | ~100 % | 1 142 | Docker, compose, `render.yaml`, CI y configuración (`infra/` 557 y raíz 585) |
| `docs/` | ~100 % | 3 007 | La planeación fue redactada con IA y revisada por el equipo |

67 de 67 commits sin fusiones llevan la marca de IA. **Ningún commit se hizo sin asistente.** La contribución humana está en
decidir el alcance, dirigir el trabajo, revisar los cambios, probarlos, corregirlos y poder explicarlos en la demo.

## 7. Reflexión crítica

**Un error que la IA introdujo y cómo lo detectamos.** Al blindar la configuración, el asistente agregó una opción para
que los errores de configuración no imprimieran la clave secreta ni la contraseña de la base de datos en los logs, y
escribió una prueba para comprobarlo. La prueba pasó, y aun así **no servía**: la desactivamos a propósito quitando el
arreglo (una "prueba de mutación") y seguía pasando. La causa era que pydantic recorta los valores largos con `...`, así que
el secreto completo nunca aparecía y la prueba buscaba lo equivocado. La reescribimos para buscar `input_value`, que es la
señal real, y entonces sí falló sin el arreglo. Dos errores parecidos aparecieron antes: un commit intermedio se guardó con
saltos de línea de Windows y lo notamos porque el diff mostraba 38 líneas borradas en un archivo donde solo cambiaban 2; y una
revisión independiente de un segundo agente encontró que las claves de ejemplo del repositorio público habrían funcionado
tal cual en producción, por lo que agregamos una variable `ENTORNO` que obliga a usar claves seguras.

Un cuarto caso apareció con las pantallas del frontend: el subagente informó que el lint y el build estaban limpios, pero al usar la pantalla en un navegador contra el backend real, cancelar la confirmación de baja dejaba su estado desfasado y el siguiente clic en "Dar de baja" ya no abría el diálogo. Ninguna herramienta automática lo habría detectado; lo corregimos haciendo que *Cancelar* limpie su propio estado en lugar de esperar un evento del navegador.

**Qué aprendimos que no habríamos aprendido sin ella.** Que *"las pruebas pasan"* no significa *"las pruebas detectan el
error"*: hay que romper el código a propósito para comprobarlo. Que el asistente es rápido pero seguro de sí mismo y puede
equivocarse en cosas pequeñas y silenciosas, así que revisar el diff, correr todo por cuenta propia y desconfiar de los
reportes de otros agentes es parte del trabajo. Y que podemos explicar el código porque lo revisamos línea por línea, no porque
lo escribimos nosotros.

### Reflexión de Carlos

> **Borrador: Carlos lo reescribe con sus palabras.**

**Un error que la IA introdujo y cómo lo detectamos.** Para fusionar `main` en la rama del tablero (PR #34), el
orquestador usó un script que resolvía los conflictos de `backend/app/main.py`. El script no supo manejar el `import`
de varias líneas (`from app.routers import (...)`) y el comando siguiente se ejecutó de todos modos, porque los pasos
estaban encadenados sin detenerse al primer error. Resultado: se subió a la rama del PR el commit `774eaee` con las
marcas `<<<<<<< HEAD`, `=======` y `>>>>>>> origin/main` dentro de `main.py`. Nadie lo revisó antes del `push`; lo
detectó la CI, que falló en el paso de `ruff` con `invalid-syntax` (las pruebas ni siquiera llegaron a correr). Se
corrigió en el commit `1ceea02`, que dejó un solo `import` con todos los routers, y la CI volvió a verde.

La lección no es "el script tenía un error", sino cómo se trabajó: se encadenaron pasos que cambian el repositorio sin
detenerse al primer fallo y se subió sin verificar. Una revisión de un segundo, `git diff --check` o buscar
`<<<<<<<` antes del `push`, lo habría evitado. Desde entonces, las instrucciones a los agentes piden revisar
`git status` y buscar marcas de conflicto después de cada fusión, antes de subir.

**Otro caso, más corto.** Al revisar en el navegador el PR #43 de Luis, el botón "Dar de baja" de Alumnos se veía como un
bloque rojo sin texto. La clase `.boton-peligro` estaba definida tres veces con estilos distintos (`alumnos.css`: texto
rojo; `admin.css` e `inscripciones.css`: fondo rojo), y al cargarse todas las hojas quedaba texto rojo sobre fondo rojo.
`npm run build`, el lint y las pruebas pasaban; el agente no lo vio porque el navegador estaba oculto. Se corrigió en
`2ef8618` con una clase propia, `.boton-texto-peligro`. La IA verificó lo que podía medir, no lo que se ve.

También hubo un acierto: el orquestador le dijo al agente del backend de inscripciones que las instalaciones deportivas
eran 4 (cancha, gimnasio, pista y alberca), pero el agente leyó `INSTALACIONES` en `backend/app/core/constantes.py`,
encontró 6 y usó las reales. Con la lista corta, crear o editar un grupo con los lugares que usa el seed (por ejemplo
"Cancha de fútbol") habría respondido 422.

**Qué aprendí que no habría aprendido sin la IA.** _Pregunta guía para Carlos (respóndela tú):_ ¿qué entendí de Git,
de la CI o de la revisión de código gracias a estos errores, que no habría visto si yo hubiera escrito todo a mano?

## Reglas de seguridad que seguimos

- No pegamos en ningún asistente contraseñas, cadenas de conexión ni llaves de API reales.
- Los datos de ejemplo del repositorio son ficticios; no se suben registros reales de alumnos.
- Revisamos que la IA no agregue dependencias inexistentes o abandonadas (OWASP A03). Por eso se evitan
  `passlib` y `python-jose` y se usan `bcrypt` y `PyJWT`.
- El archivo `.env` real nunca se sube; solo `.env.example`.
