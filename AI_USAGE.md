# Declaración de uso de IA

> Este documento declara cómo usamos asistentes de IA en el proyecto, como pide la materia
> (Programación Web, AEB-1055). La IA no es autora: los autores humanos respondemos por la exactitud de
> todo el material, incluido el generado por la herramienta. Si no podemos explicar un fragmento en la
> demo, no cuenta como nuestro.
>
> **Estado:** documento en construcción. Se va llenando mientras se programa (no al final). Las partes
> marcadas como _pendiente_ se completan antes de la etiqueta `v1.0.0`.

## 1. Herramientas y modelos

| Herramienta | Modelo(s) | Quién la usó | Para qué |
|---|---|---|---|
| Claude Code (app de escritorio de Claude) | Claude Sonnet 5.5 | Luis David Reyna Morisco | Análisis de requisitos, documentos de planeación, estructura del repositorio y, más adelante, código |
| Claude Code, subagentes (copias aisladas del repositorio) | Claude Sonnet 5.5 | Luis | Revisión independiente del código base (solo lectura), catálogos del backend, pantallas de alumnos y pantallas de catálogos y usuarios del frontend |
| Claude Code (app de escritorio de Claude) | Claude Sonnet 5.5 (orquestador) | Carlos Limones Ayala | Recibe las tareas de Carlos, las reparte y delega el trabajo a subagentes |
| Claude Code, subagentes | Claude Sonnet 5.5 | Carlos | Frontend (base, autenticación, estilos y pantallas) y servicio de clima |
| Claude Code, subagentes | Claude Opus | Carlos | Grupos (lógica del servidor y formulario dinámico) |
| Claude Code, subagentes | Claude Haiku | Carlos | Integración continua (CI) con GitHub Actions |

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

Servidores MCP o *skills* adicionales: _pendiente de listar si se usan en el proyecto_.

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
| 2026-11-21 | Carlos | Claude Code (subagente de frontend) / Claude Sonnet 5.5 | Prompt P8: crear la base del frontend (commits C01 a C04 del plan): proyecto Vite + React + TypeScript con react-router, rutas y layout semántico con navegación por rol; estilos globales responsivos (Flexbox y Grid, 2 breakpoints, variables y foco visible); cliente de API con token y manejo de errores, contexto de autenticación, hook `useApi`, componente `Estado` y rutas protegidas; pantallas de login y registro con validación en cliente. Además, completar mis filas de esta declaración. Se pidió respetar los contratos de `/api/auth/*` del backend, no agregar dependencias sin justificar y que el token nunca se imprima | `frontend/` (C01 y C02 en el PR `feature/front-base`; `src/api/`, `AuthContext`, `useApi`, `Estado`, `pages/Login` y `pages/Registro` en el PR `feature/front-auth`), `AI_USAGE.md` | _pendiente: Carlos revisa_ |

_(Se agregan filas con cada prompt importante: fecha, quién, herramienta y modelo, resumen fiel del
prompt, archivos y qué cambiamos nosotros después.)_

## 5. Marcado en commits

Los commits con código o texto generado por IA terminan con una línea final:

- `Co-Authored-By: Claude <modelo> <noreply@anthropic.com>` (la agrega Claude Code, con el modelo que se usó), o
- `Assisted-by: <herramienta/modelo>` para cualquier otra herramienta.

Para ver cuáles son: `git log --grep="Co-Authored-By\|Assisted-by"`.

## 6. Estimación de código generado por IA por carpeta

Medido con el historial de Git (líneas añadidas en commits marcados con `Co-Authored-By` o `Assisted-by`) al 21 de noviembre:

| Carpeta | % con IA | Líneas añadidas | Nota |
|---|---|---|---|
| `backend/` | ~100 % | 5 514 | Todo el código lo escribió el asistente; las personas dirigen, revisan, prueban y aprueban cada commit |
| `frontend/` | ~100 % | 4 450 | Incluye `package-lock.json` (generado por npm) |
| `db/` | ~100 % | 560 | Modelos, migración y datos semilla |
| `infra/` y raíz | ~100 % | 492 | Docker, compose, `render.yaml`, configuración |
| `docs/` | ~100 % | 949 | La planeación fue redactada con IA y revisada por el equipo |

38 de 38 commits llevan la marca de IA. **Ningún commit se hizo sin asistente.** La contribución humana está en
decidir el alcance, dirigir el trabajo, revisar los cambios, probarlos, corregirlos y poder explicarlos en la demo.

## 7. Reflexión crítica

> **Borrador escrito con ayuda de IA a partir de casos reales del proyecto. Luis lo revisa y lo reescribe con sus
> palabras antes de la entrega.**

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

## Reglas de seguridad que seguimos

- No pegamos en ningún asistente contraseñas, cadenas de conexión ni llaves de API reales.
- Los datos de ejemplo del repositorio son ficticios; no se suben registros reales de alumnos.
- Revisamos que la IA no agregue dependencias inexistentes o abandonadas (OWASP A03). Por eso se evitan
  `passlib` y `python-jose` y se usan `bcrypt` y `PyJWT`.
- El archivo `.env` real nunca se sube; solo `.env.example`.
