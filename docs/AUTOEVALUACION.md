# Autoevaluación

> Estado al **22 de noviembre de 2026** (cifras de Git con los commits de `main` hasta [`7f2c49e`](https://github.com/luisreyna060318-alt/extra-liebres/commit/7f2c49e), PR #63;
> después solo entró el PR de la revisión final).
> Es la misma tabla que la sección 9 de `docs/REPORTE.pdf`. Regla de la materia: un nivel sin evidencia queda como
> **Insuficiente**. Escala: Excelente 100 % · Notable 90 % · Bueno 80 % · Suficiente 70 % · Insuficiente 40 % o 0 %.
> **Puntos = Peso × %.** Las rutas son relativas a esta carpeta (`docs/`).

## Tabla de autoevaluación

| # | Criterio | Peso | Nivel autoasignado | % | Puntos | Evidencia (enlace) |
|---|---|---:|---|---:|---:|---|
| 1 | Planeación y arquitectura | 6 | Notable | 90 % | 5.4 | [propuesta-v2.md](propuesta-v2.md) · [plan-de-trabajo.md](plan-de-trabajo.md) · [prompts.md](prompts.md) · [arquitectura.png](arquitectura.png) · [er.png](../db/er.png) · [diagramas/](diagramas/README.md) · [issue #1 (propuesta)](https://github.com/luisreyna060318-alt/extra-liebres/issues/1) y 23 issues de historias (#3 a #25) · [tablero de GitHub Projects](https://github.com/users/luisreyna060318-alt/projects/1) |
| 2 | HTML, CSS y responsividad | 8 | Excelente | 100 % | 8.0 | [Layout.tsx](../frontend/src/components/Layout.tsx) (`header`, `nav`, `main`, `footer`, «Saltar al contenido») · [CampoFormulario.tsx](../frontend/src/components/CampoFormulario.tsx) (`label`) · [styles/](../frontend/src/styles/) (CSS externo, puntos de corte en 600 y 1024 px) · [lighthouse.md](lighthouse.md) (accesibilidad 100 en las 9 pantallas, móvil y escritorio) · PR [#46](https://github.com/luisreyna060318-alt/extra-liebres/pull/46) |
| 3 | Frontend en React | 14 | Notable | 90 % | 12.6 | [App.tsx](../frontend/src/App.tsx) (16 rutas) · [RutaPrivada.tsx](../frontend/src/components/RutaPrivada.tsx) · [AuthContext.tsx](../frontend/src/context/AuthContext.tsx) · [cliente.ts](../frontend/src/api/cliente.ts) (`fetch`, sin librerías de estado) · PR [#32](https://github.com/luisreyna060318-alt/extra-liebres/pull/32), [#33](https://github.com/luisreyna060318-alt/extra-liebres/pull/33), [#36](https://github.com/luisreyna060318-alt/extra-liebres/pull/36), [#39](https://github.com/luisreyna060318-alt/extra-liebres/pull/39), [#41](https://github.com/luisreyna060318-alt/extra-liebres/pull/41), [#43](https://github.com/luisreyna060318-alt/extra-liebres/pull/43), [#46](https://github.com/luisreyna060318-alt/extra-liebres/pull/46), [#47](https://github.com/luisreyna060318-alt/extra-liebres/pull/47) · [aplicación en línea](https://extra-liebres.vercel.app) |
| 4 | Backend en FastAPI | 14 | Excelente | 100 % | 14.0 | [main.py](../backend/app/main.py), `routers/`, `services/`, `models/`, `schemas/` · 43 operaciones ([matriz en seguridad.md](seguridad.md)) · [`/docs` en línea](https://extra-liebres.onrender.com/docs) · 413 pruebas en [backend/tests/](../backend/tests/) · PR [#26](https://github.com/luisreyna060318-alt/extra-liebres/pull/26), [#27](https://github.com/luisreyna060318-alt/extra-liebres/pull/27), [#28](https://github.com/luisreyna060318-alt/extra-liebres/pull/28), [#30](https://github.com/luisreyna060318-alt/extra-liebres/pull/30), [#31](https://github.com/luisreyna060318-alt/extra-liebres/pull/31), [#34](https://github.com/luisreyna060318-alt/extra-liebres/pull/34), [#35](https://github.com/luisreyna060318-alt/extra-liebres/pull/35), [#37](https://github.com/luisreyna060318-alt/extra-liebres/pull/37) |
| 5 | Base de datos | 12 | Excelente | 100 % | 12.0 | [modelos](../backend/app/models/) · [4 migraciones de Alembic](../db/migrations/versions/) (esquema inicial, carreras oficiales, número de control de 8 dígitos y rol lector) · [seed.py](../db/seed.py) (datos ficticios) · [er.png](../db/er.png) · restricciones `CHECK`, `UNIQUE`, llaves foráneas con `ON DELETE RESTRICT` · PR [#26](https://github.com/luisreyna060318-alt/extra-liebres/pull/26) · base en Neon (PostgreSQL) |
| 6 | Seguridad e interoperabilidad | 10 | Notable | 90 % | 9.0 | [seguridad.md](seguridad.md) (OWASP A01, A02 y A03) · [security.py](../backend/app/core/security.py) (bcrypt y PyJWT) · [deps.py](../backend/app/core/deps.py) (`require_role`) · [test_matriz_permisos.py](../backend/tests/test_matriz_permisos.py) · [test_cabeceras.py](../backend/tests/test_cabeceras.py) · [vercel.json](../frontend/vercel.json) (CSP) · servicio externo [Open-Meteo](../backend/app/services/clima.py) con manejo de fallos · PR [#27](https://github.com/luisreyna060318-alt/extra-liebres/pull/27), [#30](https://github.com/luisreyna060318-alt/extra-liebres/pull/30), [#42](https://github.com/luisreyna060318-alt/extra-liebres/pull/42), [#50](https://github.com/luisreyna060318-alt/extra-liebres/pull/50) |
| 7 | Contenedores y despliegue | 10 | Excelente | 100 % | 10.0 | [backend/Dockerfile](../backend/Dockerfile) · [frontend/Dockerfile](../frontend/Dockerfile) · [compose.yaml](../compose.yaml) e [infra/docker-compose.yml](../infra/docker-compose.yml) (arranque desde cero en 46 s, PR #40) · [render.yaml](../render.yaml) · [DEPLOY.md](../infra/DEPLOY.md) · [prueba_humo.py](../infra/prueba_humo.py) (41 de 41 correctas, también en producción) · [Vercel](https://extra-liebres.vercel.app) · [Render](https://extra-liebres.onrender.com/api/health) · PR [#38](https://github.com/luisreyna060318-alt/extra-liebres/pull/38), [#40](https://github.com/luisreyna060318-alt/extra-liebres/pull/40), [#48](https://github.com/luisreyna060318-alt/extra-liebres/pull/48), [#49](https://github.com/luisreyna060318-alt/extra-liebres/pull/49) |
| 8 | Calidad y DevOps | 8 | Notable | 90 % | 7.2 | [ci.yml](../.github/workflows/ci.yml) (ruff, pytest, lint, build y construcción de imágenes) · [ejecución verde](https://github.com/luisreyna060318-alt/extra-liebres/actions/runs/45083359426) · 413 pruebas · 39 PR fusionados (23 de Luis y 16 de Carlos) · Conventional Commits en los 86 commits sin fusiones. **Limitaciones:** solo 18 PR se aprobaron antes de fusionarse; los otros 21 entraron sin revisión por la velocidad del desarrollo y el 22 de noviembre recibieron una revisión posterior de la otra persona sobre lo que ya estaba en `main`. 67 de los 86 commits son del 21 de noviembre y 19 del 22, y el frontend no tiene pruebas automáticas |
| 9 | Declaración de uso de IA | 5 | Bueno | 80 % | 4.0 | [AI_USAGE.md](../AI_USAGE.md) · [CLAUDE.md](../CLAUDE.md) · [prompts.md](prompts.md) · línea `Co-Authored-By` en los 86 commits sin fusiones. |
| 10 | Reporte técnico | 5 | Notable | 90 % | 4.5 | `docs/REPORTE.pdf` (este reporte, con 7 figuras y referencias en APA 7) |
| 11a | Demo y defensa: Luis David Reyna Morisco | 8 | — | — | — | Se llena después de la demo |
| 11b | Demo y defensa: Carlos Limones Ayala | 8 | — | — | — | Se llena después de la demo |
| Extra | Puntos extra | +5 | — | — | — | Se declara el **intercambio de datos en XML**: los inscritos se exportan en XML bien formado, además de JSON ([exportacion.md](exportacion.md) · [test_exportar.py](../backend/tests/test_exportar.py) · PR [#52](https://github.com/luisreyna060318-alt/extra-liebres/pull/52)). Los puntos los define el profesor |
| **Total** | Criterios 1 a 10 | 92 | | | **86.7** | Más los puntos de la demo (hasta 8 por persona) y los extra que defina el profesor |

Los criterios 1 a 10 son de equipo y valen 92 puntos; la demo (8) se califica por persona.

## Notas por criterio (cómo se llegó al nivel)

1. **Planeación y arquitectura (Notable).** Propuesta, historias con criterios de aceptación, reglas de negocio y diagramas completos. No llega a Excelente porque el tablero de Projects se actualizó hasta el 22 de noviembre y no durante todo el proyecto.
2. **HTML, CSS y responsividad (Excelente).** HTML semántico, `label` en formularios, CSS externo con Flexbox y Grid, accesibilidad 100 en Lighthouse y 0 violaciones con axe-core. No se probó con lector de pantalla.
3. **Frontend en React (Notable).** 16 rutas, estados de carga, error y vacío, validación y formulario dinámico. Sin pruebas automáticas del frontend.
4. **Backend en FastAPI (Excelente).** 43 operaciones por capas, esquemas separados de entrada y salida, códigos HTTP correctos y 413 pruebas. Las cuatro historias deseables están entregadas, incluidas HU-06.2 (búsqueda global) y HU-07.2 (exportar a CSV y XML).
5. **Base de datos (Excelente).** Siete tablas con relaciones 1:N y N:M, restricciones, 4 migraciones reproducibles (las de datos, 0002 y 0003, no se pueden deshacer: lo dice cada una) y datos semilla con una cuenta por rol. Las pruebas automáticas del CI usan SQLite en memoria, no PostgreSQL; la migración se probó en PostgreSQL con Docker y en Neon.
6. **Seguridad e interoperabilidad (Notable).** Evidencia fuerte (matriz de permisos probada, cabeceras y CSP, sin secretos en el historial). Siguen abiertas, y declaradas, el límite de intentos de inicio de sesión, el token en `localStorage` y `/docs` público.
7. **Contenedores y despliegue (Excelente).** `docker compose up` desde cero y despliegue público en Vercel, Render y Neon. El plan gratuito de Render apaga el servicio por inactividad.
8. **Calidad y DevOps (Notable).** CI en verde y flujo de PR, pero con commits concentrados en dos días y 21 de 39 PR revisados después de fusionarse.
9. **Declaración de IA (Bueno).** El documento cubre los 7 puntos y no quedan celdas pendientes.
10. **Reporte técnico (Notable).** Cuatro fases, figuras y referencias; quedan detalles de forma.
11. **Demo y defensa.** Aún no ocurre.

## Reflexión por integrante

### Luis David Reyna Morisco

Lo que más me costó fue el criterio 8: todo se hizo en dos días (21 y 22 de noviembre), así que los commits quedaron concentrados y varios PR se fusionaron sin revisión y se revisaron después. Técnicamente, lo más difícil fue blindar la configuración (que el backend no arranque con claves de ejemplo ni imprima secretos). Si lo repitiera, repartiría el trabajo en varios días y llenaría la bitácora de IA mientras programo. Creo estar en un nivel Notable en la competencia: puedo explicar una petición completa, del clic en React a la consulta en PostgreSQL, y defender mi parte.

### Carlos Limones Ayala

Lo que más me costó fue coordinar el trabajo en paralelo: fusionar `main` en cada rama generó conflictos en `main.py` y uno terminó en un commit con marcas de conflicto que tumbó la CI. Si lo repitiera, acordaría el orden de fusión y revisaría `git status` antes de cada `push`. Creo estar en un nivel Notable en la competencia: puedo explicar el flujo de grupos, inscripciones y tablero, y cómo la CI valida cada cambio.

## Cómo actualizar esta tabla

Cuando cambie algo (demo, pruebas del frontend, celdas de `AI_USAGE.md`), subir el nivel **solo si hay un enlace que lo demuestre**,
recalcular `Puntos = Peso × %` y actualizar los totales.
