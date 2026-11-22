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
| _(se agregarán otros modelos de Claude si se delegan tareas a subagentes)_ | _pendiente_ | Luis | Se anotará aquí modelo y tarea de cada uno |
| _(pendiente)_ | _pendiente_ | Carlos Limones Ayala | Carlos declara aquí las herramientas que use, o escribe "ninguna" |

## 2. Harness y modo de uso

- **Luis:** Claude Code en la app de escritorio de Claude, como **agente que edita archivos y ejecuta
  comandos** (Git, Docker, `gh`, Python, Node) sobre el repositorio local. Cada commit lo aprueba Luis
  antes de hacerse y cada cambio se revisa antes de subirlo.
- **Carlos:** _pendiente_.

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

_(Se agregan filas con cada prompt importante: fecha, quién, herramienta y modelo, resumen fiel del
prompt, archivos y qué cambiamos nosotros después.)_

## 5. Marcado en commits

Los commits con código o texto generado por IA terminan con una línea final:

- `Co-Authored-By: Claude <modelo> <noreply@anthropic.com>` (la agrega Claude Code, con el modelo que se usó), o
- `Assisted-by: <herramienta/modelo>` para cualquier otra herramienta.

Para ver cuáles son: `git log --grep="Co-Authored-By\|Assisted-by"`.

## 6. Estimación de código generado por IA por carpeta

| Carpeta | % aproximado con IA | Nota |
|---|---|---|
| `frontend/` | _pendiente_ | Se estima al final con el historial de commits |
| `backend/` | _pendiente_ | |
| `db/` | _pendiente_ | |
| `infra/` | _pendiente_ | |
| `docs/` | _pendiente_ | La planeación inicial fue redactada con IA y revisada por el equipo |

## 7. Reflexión crítica

_Pendiente. Se escribirá (media página) antes de la entrega con un caso **real** del proyecto: un error o
vulnerabilidad que la IA introdujo, cómo lo detectamos y qué aprendimos que no habríamos aprendido sin ella.
No se redacta por adelantado para no inventar un caso._

## Reglas de seguridad que seguimos

- No pegamos en ningún asistente contraseñas, cadenas de conexión ni llaves de API reales.
- Los datos de ejemplo del repositorio son ficticios; no se suben registros reales de alumnos.
- Revisamos que la IA no agregue dependencias inexistentes o abandonadas (OWASP A03). Por eso se evitan
  `passlib` y `python-jose` y se usan `bcrypt` y `PyJWT`.
- El archivo `.env` real nunca se sube; solo `.env.example`.
