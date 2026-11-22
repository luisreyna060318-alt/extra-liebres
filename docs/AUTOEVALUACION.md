# Autoevaluación (borrador)

> **Borrador para que Carlos y Luis lo revisen y ajusten.** Los niveles se asignaron con lo que **existe hoy en
> `main`** (estado revisado en el commit [`698c691`](https://github.com/luisreyna060318-alt/extra-liebres/commit/698c6911923bedb1045b05abf4e31959706dfe23),
> 21 de noviembre de 2026), no con lo que está planeado. Regla de la materia: un nivel sin evidencia queda como
> **Insuficiente**. Escala: Excelente 100 % · Notable 90 % · Bueno 80 % · Suficiente 70 % · Insuficiente 40 % o 0 %
> (0 % cuando no hay nada entregado). **Puntos = Peso × %.** Las rutas son relativas a esta carpeta (`docs/`).
>
> Todo lo marcado como _pendiente_ lo escribe cada integrante con sus palabras.

## Tabla de autoevaluación

| # | Criterio | Peso | Nivel autoasignado | % | Puntos | Evidencia (enlace) |
|---|---|---:|---|---:|---:|---|
| 1 | Planeación y arquitectura | 6 | Bueno | 80 % | 4.8 | [propuesta-v2.md](propuesta-v2.md) · [plan-de-trabajo.md](plan-de-trabajo.md) · [prompts.md](prompts.md) · [arquitectura.png](arquitectura.png) · [er.png](../db/er.png) · [diagramas/](diagramas/README.md) · [issue #1 (propuesta)](https://github.com/luisreyna060318-alt/extra-liebres/issues/1) y 23 issues de historias de usuario (#3 a #25). **Falta:** verificar el tablero de GitHub Projects (no se pudo leer con `gh`); las 24 issues siguen abiertas aunque varias historias ya tienen su PR fusionado. |
| 2 | HTML, CSS y responsividad | 8 | Bueno | 80 % | 6.4 | [Layout.tsx](../frontend/src/components/Layout.tsx) (`header`, `nav`, `main`, `footer`, enlace «Saltar al contenido») · [CampoFormulario.tsx](../frontend/src/components/CampoFormulario.tsx) (`label`) · [styles/](../frontend/src/styles/) (CSS externo, puntos de corte en 600 y 1024 px, p. ej. [base.css](../frontend/src/styles/base.css)). **Falta:** reporte de Lighthouse (RNF-02 pide accesibilidad ≥ 90) y revisión documentada en móvil; la app no tiene imágenes, así que el texto alternativo no aplica todavía. |
| 3 | Frontend React | 14 | Notable | 90 % | 12.6 | SPA con rutas protegidas: [App.tsx](../frontend/src/App.tsx) · [RutaPrivada.tsx](../frontend/src/components/RutaPrivada.tsx) · [AuthContext.tsx](../frontend/src/context/AuthContext.tsx) · [cliente.ts](../frontend/src/api/cliente.ts) (`fetch`, sin librerías de estado) · PR [#32](https://github.com/luisreyna060318-alt/extra-liebres/pull/32), [#33](https://github.com/luisreyna060318-alt/extra-liebres/pull/33), [#36](https://github.com/luisreyna060318-alt/extra-liebres/pull/36), [#39](https://github.com/luisreyna060318-alt/extra-liebres/pull/39), [#41](https://github.com/luisreyna060318-alt/extra-liebres/pull/41), [#43](https://github.com/luisreyna060318-alt/extra-liebres/pull/43) · CI del frontend (lint y build) en [ci.yml](../.github/workflows/ci.yml). **Falta:** pruebas del frontend (no hay ninguna); verlo funcionando en una URL pública. |
| 4 | Backend FastAPI | 14 | Notable | 90 % | 12.6 | API por capas ([main.py](../backend/app/main.py), `routers/`, `services/`, `models/`, `schemas/`) con 40 rutas ([matriz en seguridad.md](seguridad.md)), documentación OpenAPI en `/docs`, al menos 221 funciones de prueba en [backend/tests/](../backend/tests/) · PR [#26](https://github.com/luisreyna060318-alt/extra-liebres/pull/26), [#27](https://github.com/luisreyna060318-alt/extra-liebres/pull/27), [#28](https://github.com/luisreyna060318-alt/extra-liebres/pull/28), [#30](https://github.com/luisreyna060318-alt/extra-liebres/pull/30), [#31](https://github.com/luisreyna060318-alt/extra-liebres/pull/31), [#34](https://github.com/luisreyna060318-alt/extra-liebres/pull/34), [#35](https://github.com/luisreyna060318-alt/extra-liebres/pull/35), [#37](https://github.com/luisreyna060318-alt/extra-liebres/pull/37) · [ejecución verde del CI](https://github.com/luisreyna060318-alt/extra-liebres/actions/runs/44983273369). **Falta:** las historias deseables HU-06.2 (búsqueda global) y HU-07.2 (exportar); la API no está accesible en una URL pública. |
| 5 | Base de datos | 12 | Notable | 90 % | 10.8 | [modelos](../backend/app/models/) · [migración de Alembic](../db/migrations/versions/20261121_0001_esquema_inicial.py) · [seed.py](../db/seed.py) (datos ficticios) · [er.png](../db/er.png) (generado desde la migración) · restricciones `CHECK`, `UNIQUE`, `FK ... ON DELETE RESTRICT` e índices · PR [#26](https://github.com/luisreyna060318-alt/extra-liebres/pull/26). **Falta:** la base en Neon (no existe aún); las pruebas del CI usan SQLite en memoria, no PostgreSQL. |
| 6 | Seguridad e interoperabilidad | 10 | Notable | 90 % | 9.0 | [seguridad.md](seguridad.md) (OWASP A01, A02 y A03, matriz de permisos) · [security.py](../backend/app/core/security.py) (bcrypt y PyJWT) · [deps.py](../backend/app/core/deps.py) (`require_role`) · [test_matriz_permisos.py](../backend/tests/test_matriz_permisos.py) · [test_security.py](../backend/tests/test_security.py) · CORS limitado en [main.py](../backend/app/main.py) · API REST con OpenAPI y servicio externo [Open-Meteo](../backend/app/services/clima.py) · PR [#27](https://github.com/luisreyna060318-alt/extra-liebres/pull/27), [#30](https://github.com/luisreyna060318-alt/extra-liebres/pull/30), [#42](https://github.com/luisreyna060318-alt/extra-liebres/pull/42). **Falta:** límite de intentos de inicio de sesión, token fuera de `localStorage` y `/docs` cerrado en producción (las tres están declaradas como limitaciones en seguridad.md); comprobar CORS con el dominio real de Vercel. |
| 7 | Contenedores y despliegue | 10 | Suficiente | 70 % | 7.0 | [backend/Dockerfile](../backend/Dockerfile) · [frontend/Dockerfile](../frontend/Dockerfile) · [docker-compose.yml](../infra/docker-compose.yml) y [compose.yaml](../compose.yaml) (`docker compose up --build` levanta `db`, `backend` y `frontend` con *healthchecks*) · [render.yaml](../render.yaml) · [vercel.json](../frontend/vercel.json) · [DEPLOY.md](../infra/DEPLOY.md) · job `docker` del [CI](../.github/workflows/ci.yml) · PR [#38](https://github.com/luisreyna060318-alt/extra-liebres/pull/38), [#40](https://github.com/luisreyna060318-alt/extra-liebres/pull/40). **Falta:** el **despliegue público no existe**: no hay URL de Vercel, Render ni Neon (el README dice «Pendiente de desplegar»). Al desplegar y probar la URL, este criterio sube. |
| 8 | Calidad y DevOps | 8 | Bueno | 80 % | 6.4 | [ci.yml](../.github/workflows/ci.yml) (ruff, pytest, lint, build y construcción de imágenes; [ejecución verde](https://github.com/luisreyna060318-alt/extra-liebres/actions/runs/44983273369) y insignia en el README) · Conventional Commits en español en todos los commits (salvo los de fusión) · 19 PR fusionados a `main`, 16 con aprobación de la otra persona (p. ej. [#29](https://github.com/luisreyna060318-alt/extra-liebres/pull/29), [#31](https://github.com/luisreyna060318-alt/extra-liebres/pull/31), [#43](https://github.com/luisreyna060318-alt/extra-liebres/pull/43)) · al menos 221 funciones de prueba del backend. **Falta:** pruebas del frontend; los PR [#39](https://github.com/luisreyna060318-alt/extra-liebres/pull/39), [#40](https://github.com/luisreyna060318-alt/extra-liebres/pull/40) y [#41](https://github.com/luisreyna060318-alt/extra-liebres/pull/41) no tienen revisión de Luis; etiqueta `v1.0.0` (no existe); tablero de Projects sin verificar; no se pudo confirmar la protección de `main`. |
| 9 | Declaración de uso de IA | 5 | Bueno | 80 % | 4.0 | [AI_USAGE.md](../AI_USAGE.md) (herramientas, modelos, harness, bitácora de prompts, porcentaje por carpeta, reflexión crítica) · [CLAUDE.md](../CLAUDE.md) · [prompts.md](prompts.md) · línea `Co-Authored-By` en los commits asistidos. **Falta:** las celdas «Ajustes humanos» marcadas como _Pendiente_; la reflexión crítica es un borrador escrito con IA que cada integrante debe reescribir con sus palabras; la lista de servidores MCP y *skills*. |
| 10 | Reporte técnico | 5 | Insuficiente | 0 % | 0.0 | **Sin evidencia en `main`:** no hay `docs/REPORTE*` (el reporte aún no está en el repositorio). **Falta:** entregar el reporte en el repositorio con las 4 fases, figuras ([arquitectura.png](arquitectura.png), [er.png](../db/er.png)) y referencias. |
| 11a | Demo y defensa — Luis David Reyna Morisco | 8 | Insuficiente | 0 % | 0.0 | **Sin evidencia:** la demo todavía no ha ocurrido. _pendiente: lo escribe cada integrante_ |
| 11b | Demo y defensa — Carlos Limones Ayala | 8 | Insuficiente | 0 % | 0.0 | **Sin evidencia:** la demo todavía no ha ocurrido. _pendiente: lo escribe cada integrante_ |
| Extra | Puntos extra | — | — | — | 0.0 | Ninguno declarado (el plan de trabajo recorta el alcance a «sin puntos extra»). |
| **Total** | **Luis** (criterios 1 a 10 + su demo 11a) | 100 | | | **73.6** | Suma de la columna «Puntos» con su fila de demo. |
| **Total** | **Carlos** (criterios 1 a 10 + su demo 11b) | 100 | | | **73.6** | Suma de la columna «Puntos» con su fila de demo. |

Los criterios 1 a 10 valen 92 puntos y la demo (8) se califica por persona, por eso hay un total por integrante.
**Qué mueve más la nota si se hace antes de entregar:** reporte técnico (hasta +5), despliegue público (hasta +3 en
el criterio 7 y respalda el 3, el 4 y el 5) y la demo (hasta +8 por persona).

## Notas por criterio (cómo se llegó al nivel)

1. **Planeación y arquitectura (Bueno).** La propuesta, el plan, las historias y las reglas de negocio están completos y
   los diagramas se agregan en este cambio. No se sube a Notable porque el tablero de Projects no está verificado y las
   issues de historias siguen abiertas, así que el avance no se ve ahí.
2. **HTML, CSS y responsividad (Bueno).** HTML semántico, `label` en formularios, CSS externo con Flexbox/Grid y dos
   puntos de corte. Falta la medición de Lighthouse, que es lo que respalda el «Notable».
3. **Frontend React (Notable).** Rutas, sesión, formularios con validación, tablero y gráficas funcionan y pasan lint y
   build en el CI. Sin pruebas del frontend ni URL pública, no llega a Excelente.
4. **Backend FastAPI (Notable).** Capas, esquemas separados de entrada y salida, errores uniformes, autorización por rol y
   al menos 221 funciones de prueba. Faltan las dos historias deseables.
5. **Base de datos (Notable).** Esquema normalizado con restricciones y migración reproducible. Falta probarla contra Neon.
6. **Seguridad e interoperabilidad (Notable).** Hay evidencia fuerte (matriz de permisos probada) y las limitaciones están
   escritas con honestidad; quedan abiertas medidas como el límite de intentos.
7. **Contenedores y despliegue (Suficiente).** La parte de contenedores está lista; la de despliegue público no existe.
8. **Calidad y DevOps (Bueno).** CI sólido y flujo de PR con revisión cruzada en 16 de 19 PR; falta el frontend sin pruebas,
   la etiqueta y las revisiones de #39 a #41.
9. **Declaración de IA (Bueno).** El documento es completo, pero tiene secciones pendientes de las personas.
10. **Reporte técnico (Insuficiente, 0 %).** Nada entregado en el repositorio todavía.
11. **Demo y defensa.** Aún no ocurre.

## Demo y defensa y reflexión por integrante

### Luis David Reyna Morisco

_pendiente: lo escribe cada integrante_

### Carlos Limones Ayala

_pendiente: lo escribe cada integrante_

## Cómo actualizar esta tabla

Cuando cambie algo (despliegue, Lighthouse, reporte, pruebas del frontend), subir el nivel **solo si hay un enlace que
lo demuestre**, recalcular `Puntos = Peso × %` y actualizar los totales.
