# 04 · Prompts estructurados (para `AI_USAGE.md` y para trabajar con el asistente)

El profesor pide una **bitácora de prompts significativos**. Estos son los que más ayudan a avanzar el
proyecto. Cada uno está escrito para que el asistente tenga clara la tarea; **ustedes los leen, los
corrigen antes de enviarlos y revisan lo que devuelve**. Lo que cambien después va en la columna
"Ajustes humanos" de la bitácora.

## Cómo usar este documento

1. **Contexto fijo.** Pongan el bloque de la sección A en `CLAUDE.md` en la raíz del repo (el asistente
   lo lee solo) y declárenlo en `AI_USAGE.md`. Así no se repite en cada prompt.
2. **Un prompt = una rama = un PR pequeño.** Pidan el cambio, léanlo, córranlo, corrijan, y solo
   entonces hagan commit.
3. **Antes de enviar**, reemplacen lo que dice `<…>` y quiten cualquier dato real. **Nunca** peguen
   contraseñas, cadenas de conexión ni llaves de API.
4. **Después de recibir**, hagan la lista "Revisión humana" de cada prompt y anótenla en la bitácora.
5. Si no pueden explicar lo que generó, usen el **P13 (modo tutor)** o pidan una versión más simple.

Plantilla de cada prompt: **Rol · Contexto · Tarea · Restricciones · Entregable · Verificación**.

---

## A. Contexto fijo (`CLAUDE.md` del repositorio)

```markdown
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
```

---

## P1 · Modelos SQLAlchemy, migración inicial y seed — *Luis · sábado/domingo*

```text
ROL: Eres mi asistente de programación. Yo soy estudiante y debo poder explicar todo el código.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md, sección 6 "Modelo de datos". Usamos SQLAlchemy 2
(estilo declarativo con Mapped / mapped_column), PostgreSQL y Alembic.

TAREA:
1. Crea los modelos en backend/app/models/: usuario, alumno, promotor, extraescolar, semestre, grupo y
   alumno_grupo (tabla de asociación con calificacion y desempenio, PK compuesta nocontrol+idgrupo).
2. Usa EXACTAMENTE los nombres de columnas de la sección 6. nocontrol y rfc son String (no enteros).
3. Relaciones: promotor 1:N grupo, extraescolar 1:N grupo, semestre 1:N grupo, alumno N:M grupo.
4. Restricciones de integridad: CHECK horainicio < horatermino; CHECK calificacion entre 0 y 100;
   UNIQUE (anio, mesinicio) en semestre; usuario.correo UNIQUE; valores válidos para sexo, tipo y rol.
5. Configura Alembic para que las migraciones queden en db/migrations/ y genera la migración inicial.
6. Escribe db/seed.py con datos FICTICIOS (≈200 alumnos, 10 promotores, 8 actividades con tipo y
   al_aire_libre, 6 semestres, ≈40 grupos sin cruces, ≈600 inscripciones con calificación y desempeño
   calculado) y 2 usuarios de prueba: un administrador y un capturista. Las contraseñas de prueba vienen
   de variables de entorno o se imprimen al correr el seed; no las dejes escritas en el código.

RESTRICCIONES: no agregues tablas ni columnas que no estén en la sección 6. No uses datos reales.
El seed debe poder correrse más de una vez sin duplicar datos.

ENTREGABLE: archivos creados, comando para aplicar migraciones y para sembrar, y una explicación breve
de cada relación.

VERIFICACIÓN: `alembic upgrade head` y `python db/seed.py` funcionan sobre una BD vacía en Docker;
muéstrame cómo comprobar las tablas con `docker compose exec db psql ...`.
```

**Revisión humana:** que las claves foráneas y la PK compuesta sean las del modelo; que los `CHECK`
existan en la migración (no solo en Python); que el seed no contenga nombres reales; que `downgrade` funcione.

---

## P2 · Autenticación JWT y autorización por rol — *Luis · domingo*

```text
ROL: Asistente de programación para un proyecto estudiantil (código simple y explicable).

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md (HU-01.1 a HU-01.4, RN-06, RNF-05).

TAREA:
1. Endpoints: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me.
   - register crea siempre rol "capturista". Valida correo único y contraseña (≥ 8, letras y números).
   - login recibe OAuth2PasswordRequestForm (username = correo) para que el botón "Authorize" de /docs
     funcione, y devuelve un JWT de 60 minutos. El mensaje de error NO revela si falló correo o contraseña.
2. backend/app/core/security.py: hash/verificación con bcrypt, creación/lectura de JWT con PyJWT. La clave
   y el algoritmo salen de variables de entorno (core/config.py).
3. backend/app/core/deps.py: dependencias get_current_user y require_role("administrador") (inyección de
   dependencias de FastAPI). Si no hay token → 401. Si el rol no alcanza → 403. Usuario inactivo → 401.
4. PATCH /api/usuarios/{id} y GET /api/usuarios (solo administrador), con las reglas de RN-06: no quitar ni
   suspender al último administrador.
5. Esquemas Pydantic de entrada y salida separados; la salida nunca incluye password_hash.

RESTRICCIONES: no uses passlib ni python-jose. No guardes secretos en el código. Un solo rol por persona.
Sin refresh tokens ni OAuth externo. Logout = el cliente descarta el token (explícalo en un comentario).

ENTREGABLE: archivos nuevos/modificados, variables de entorno que se agregan a .env.example, y un
diagrama en texto del flujo login → token → petición protegida.

VERIFICACIÓN: pruebas pytest para: registro correcto, correo duplicado (409), login correcto, login
incorrecto (401), /me sin token (401), /usuarios con capturista (403) y con administrador (200).
```

**Revisión humana:** que `require_role` se aplique en el **servidor** (no solo en React); que no haya
`SECRET_KEY` fija en el código; que la expiración del token se respete; probar a mano el 403 en `/docs`.

---

## P3 · CRUD de alumnos con búsqueda y paginación (plantilla de todos los CRUD) — *Luis · domingo*

```text
ROL: Asistente de programación para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md (HU-02.1 a HU-02.4, RN-01, RN-02, RN-11). Ya existen los
modelos y la autenticación.

TAREA: Implementa el CRUD de alumnos con la estructura en capas:
- schemas/alumno.py: AlumnoCrear, AlumnoActualizar, AlumnoSalida, y una respuesta paginada genérica
  {items, total, page, size}.
- services/alumno_service.py: toda la lógica (crear con validación de duplicado → 409, buscar, actualizar,
  baja lógica, reactivar, historial).
- routers/alumnos.py: GET /api/alumnos (q, carrera, campus, activo, page=1, size=10), POST, GET /{nocontrol},
  PUT /{nocontrol}, DELETE /{nocontrol} (hace baja lógica y responde 204), GET /{nocontrol}/historial.
- La búsqueda q compara con nombre, apellidos y nocontrol sin distinguir mayúsculas.
- Todos los endpoints exigen sesión. Nada de SQL escrito a mano: solo el ORM.

RESTRICCIONES: size máximo 50. Documenta cada endpoint con summary y descripción para /docs.
No agregues librerías de paginación. Mantén los routers sin lógica de negocio.

ENTREGABLE: archivos, y un comentario explicando cómo viaja una petición GET /api/alumnos?q=ana desde
el router hasta SQLAlchemy.

VERIFICACIÓN: pruebas pytest de crear, duplicado (409), buscar, paginar (total y página 2), baja lógica
(el alumno deja de salir por defecto pero su historial sigue) y 401 sin token.
```

**Revisión humana:** que `DELETE` no borre filas; que `size` esté limitado; que el filtro `activo` tenga
valor por defecto sensato; que el `total` sea el de toda la consulta y no el de la página.
*Este router es el modelo: promotores, actividades, semestres y grupos se piden "con el mismo patrón que alumnos".*

---

## P4 · Grupos y validación de cruces de horario/aula — *Carlos · domingo*

```text
ROL: Asistente de programación para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md (HU-04.1, HU-04.3, HU-04.4, RN-03, RN-08). Sigue el mismo
patrón por capas que el CRUD de alumnos (schemas, services, routers).

TAREA:
1. CRUD de grupos: GET /api/grupos (filtros semestre, extraescolar, promotor, dia; paginado),
   POST, GET /{id}, PUT /{id}, DELETE /{id}.
2. En el servicio, una función `validar_cruces(grupo, excluir_id=None)` que rechaza con 409 y un mensaje
   que nombre el grupo en conflicto cuando, EN EL MISMO semestre y día, el horario se traslapa con otro
   grupo del mismo promotor o del mismo aula. Dos horarios se traslapan si inicio1 < fin2 y inicio2 < fin1.
3. Rechaza con 422 si horatermino <= horainicio.
4. DELETE responde 409 si el grupo tiene alumnos inscritos.
5. La respuesta de un grupo incluye nombre de actividad, promotor y semestre (no solo los ids).

RESTRICCIONES: lógica solo en services/. Explica la condición de traslape en un comentario con un
ejemplo numérico. Sin librerías extra.

ENTREGABLE: archivos y una tabla de casos (horarios que sí y que no se traslapan).

VERIFICACIÓN: pruebas pytest con estos casos: sin conflicto (201); mismo promotor traslapado (409);
mismo aula traslapado (409); horarios contiguos (08:00-09:00 y 09:00-10:00) permitidos (201);
hora fin <= inicio (422); editar un grupo sin cruzarse consigo mismo (200).
```

**Revisión humana:** probar los casos límite a mano (horarios contiguos); que al **editar** no choque con
sí mismo; que el mensaje de conflicto sea claro para el usuario.

---

## P5 · Inscripción, evaluación y consulta de inscritos — *Carlos · lunes*

```text
ROL: Asistente de programación para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md (HU-05.1 a HU-05.3, HU-06.1, RN-04, RN-05).

TAREA:
1. Endpoints: GET /api/grupos/{id}/inscritos, POST /api/grupos/{id}/inscripciones (body: nocontrol),
   PUT /api/grupos/{id}/inscripciones/{nocontrol} (body: calificacion), DELETE ... (204).
2. Reglas: alumno inactivo → 409; alumno ya inscrito en ese grupo → 409; calificación fuera de 0–100 → 422.
3. El desempeño NO lo envía el cliente: el servidor lo calcula con una función pura
   `calcular_desempenio(calificacion)` (Excelente 95–100, Notable 85–94, Bueno 75–84, Suficiente 70–74,
   Insuficiente < 70) y lo guarda al evaluar.
4. GET /api/consultas/inscritos con filtros opcionales extraescolar y semestre, paginado, devolviendo
   alumno, grupo, calificación y desempeño.

RESTRICCIONES: la función de desempeño va aislada en services/ para poder probarla sin base de datos.
Sin librerías extra.

ENTREGABLE: archivos y una explicación del flujo de una evaluación.

VERIFICACIÓN: pruebas pytest de calcular_desempenio en los bordes (69, 70, 74, 75, 84, 85, 94, 95, 100,
0) y de los endpoints (inscribir, duplicado 409, alumno inactivo 409, evaluar, fuera de rango 422).
```

**Revisión humana:** que el desempeño se recalcule al **corregir** una calificación; los bordes de la
escala; que el cliente no pueda mandar `desempenio` por su cuenta.

---

## P6 · Servicio externo: clima con Open-Meteo — *Carlos · lunes*

```text
ROL: Asistente de programación para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md (HU-08.1, RN-10). Debemos consumir una API pública DESDE EL
BACKEND; el navegador nunca la llama directamente. Usamos Open-Meteo (sin llave de API).

TAREA:
1. backend/app/services/clima.py: función `obtener_clima()` que consulta Open-Meteo para Ciudad Juárez
   (latitud 31.69, longitud -106.42, zona America/Ciudad_Juarez): temperatura actual y la probabilidad
   máxima de precipitación de las próximas 12 horas. Revisa la documentación oficial para los nombres
   exactos de los parámetros y no inventes campos.
2. Usa httpx con timeout de 5 segundos. Caché en memoria de 1 hora (diccionario con marca de tiempo).
3. Si la API falla, hay timeout o la respuesta es inválida: NO lances error al cliente; devuelve
   {"disponible": false, "mensaje": "Pronóstico no disponible"} y registra el error en el log.
4. GET /api/clima (requiere sesión) devuelve {disponible, temperatura, prob_lluvia, aviso_lluvia} donde
   aviso_lluvia es true si prob_lluvia >= 50 (umbral configurable por variable de entorno).

RESTRICCIONES: sin llaves ni secretos. La URL base y el umbral van en configuración. No más de ~60 líneas
en el servicio.

ENTREGABLE: archivos y un ejemplo de la respuesta JSON en cada caso (ok y falla).

VERIFICACIÓN: pruebas pytest SIN red: simula la respuesta de httpx con monkeypatch para (a) respuesta
correcta, (b) timeout, (c) JSON inválido, (d) segunda llamada dentro de la hora usa caché.
```

**Revisión humana:** que el fallo **no** rompa el tablero (criterio de "API externa con manejo de
fallos"); que los nombres de parámetros coincidan con la documentación oficial de Open-Meteo (verificar
a mano con una petición real); que las pruebas no dependan de internet.

---

## P7 · Tablero: endpoint de resumen y gráficas — *Carlos · martes*

```text
ROL: Asistente de programación para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md (HU-07.1). Backend con SQLAlchemy; frontend React.

TAREA:
BACKEND — GET /api/dashboard/resumen?semestre=<id> (sesión requerida) devuelve:
 {totales: {alumnos_activos, grupos, inscripciones}, inscritos_por_actividad: [{actividad, total}],
  distribucion_desempenio: [{desempenio, total}], promedio_calificacion}
 Calculado con consultas agregadas (COUNT, GROUP BY, AVG) con SQLAlchemy; sin recorrer filas en Python.
 Si no se envía semestre, usa el más reciente.
FRONTEND — pages/Tablero.tsx:
 - Selector de semestre (consume GET /api/semestres).
 - Tarjetas con los totales, y dos gráficas (barras: inscritos por actividad; pastel o barras: desempeño)
   con la librería Recharts.
 - Muestra el aviso del clima (GET /api/clima) y el aviso destacado si aviso_lluvia es true.
 - Estados de carga, error y vacío en cada bloque. Texto alternativo/tabla accesible para las gráficas.

RESTRICCIONES: una sola librería de gráficas (Recharts). Componentes pequeños y reutilizables
(TarjetaIndicador, GraficaBarras). Si el clima falla, el resto del tablero sigue funcionando.

ENTREGABLE: archivos, y cómo cambiar el semestre recalcula todo.

VERIFICACIÓN: prueba pytest del endpoint con datos conocidos (totales exactos); revisión manual en
móvil (360 px) y escritorio.
```

**Revisión humana:** comparar los números del tablero con una consulta SQL directa; que no haya
divisiones por cero cuando no hay inscritos (promedio nulo); contraste y etiquetas de las gráficas.

---

## P8 · Base del frontend: rutas, autenticación y estados de carga/error/vacío — *Carlos · sábado*

```text
ROL: Asistente de programación para un proyecto estudiantil (React + TypeScript).

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md secciones 7 y 8 (endpoints y pantallas).

TAREA:
1. Proyecto Vite + React + TypeScript en frontend/ con react-router. Rutas: /login, /registro, / (tablero),
   /alumnos, /grupos, /catalogos, /usuarios, /consultas. Las privadas redirigen a /login sin sesión; /catalogos
   y /usuarios solo se muestran a administrador (la API igual protege en el servidor).
2. src/api/cliente.ts: wrapper de fetch que agrega el token (guardado en memoria y localStorage), la URL base
   desde import.meta.env.VITE_API_URL, y convierte errores HTTP en un error con el mensaje del servidor.
   Si recibe 401, cierra la sesión y manda a /login.
3. AuthContext con useState/useEffect: usuario actual, login, logout.
4. Un hook `useApi(fn)` que devuelva {datos, cargando, error, recargar} y un componente `Estado` que muestre
   "Cargando…", el error con botón de reintentar, o el mensaje de "sin resultados".
5. Layout semántico: header, nav, main, footer; navegación según rol.
6. CSS externo con Flexbox/Grid, mobile-first, al menos 2 breakpoints (≈600 px y ≈1024 px), variables CSS
   y foco visible. Sin Tailwind ni librerías de componentes.

RESTRICCIONES: componentes funcionales con props tipadas; sin Redux/React Query. Comentarios breves en
español. Usa `label` en todos los campos y type de input adecuado (email, password).

ENTREGABLE: archivos, y una explicación de cómo viaja un clic en "Iniciar sesión" hasta la API.

VERIFICACIÓN: `npm run build` y `npm run lint` pasan; probar en 360 px; navegar con teclado.
```

**Revisión humana:** que el token no se imprima en consola; que las rutas de admin se **oculten** pero
la seguridad real esté en el backend; correr Lighthouse en `/login`.

---

## P9 · Formulario dinámico validado en cliente y servidor — *Carlos · lunes*

```text
ROL: Asistente de programación para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md (HU-04.2). El formulario de grupo cambia según el tipo
de la actividad elegida.

TAREA:
1. frontend/src/pages/GrupoFormulario.tsx: al elegir actividad, leer su tipo y al_aire_libre:
   - deportiva → mostrar <select> "Instalación" (cancha, gimnasio, pista, alberca) y ocultar "Aula";
   - cultural o cívica → mostrar <input> "Aula";
   - al_aire_libre → mostrar el pronóstico (GET /api/clima) junto al formulario.
   Siempre: semestre, promotor, día, hora de inicio y de término.
2. Validación en el cliente antes de enviar (campos obligatorios, hora fin > hora inicio) con mensajes junto a
   cada campo y sin perder lo capturado. Los errores 409 del servidor (cruce) se muestran en un aviso claro.
3. El servidor valida lo mismo con Pydantic: si tipo es deportiva, el lugar debe estar en la lista de
   instalaciones permitidas; el servidor rechaza con 422 aunque alguien salte la pantalla.
4. Reutiliza un componente `CampoFormulario` (label + input + mensaje de error) con props.

RESTRICCIONES: sin librerías de formularios. Un solo estado con useState por formulario. Código que un
estudiante pueda explicar.

ENTREGABLE: archivos y una descripción de qué se valida dónde (cliente vs servidor).

VERIFICACIÓN: probar cada tipo de actividad; enviar el formulario con curl/`/docs` saltando la pantalla y
comprobar el 422; prueba pytest del esquema.
```

**Revisión humana:** que cliente y servidor **coincidan** en las reglas; que `CampoFormulario` use
`htmlFor`/`id`; que cambiar de actividad limpie el campo que ya no aplica.

---

## P10 · Pruebas automáticas con pytest — *ambos · lunes/martes*

```text
ROL: Asistente de programación para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y docs/propuesta-v2.md. Las pruebas usan SQLite en memoria y el cliente de pruebas de
FastAPI (TestClient); la base real no se toca.

TAREA:
1. backend/tests/conftest.py: engine SQLite en memoria, creación de tablas, sobrescritura de la dependencia
   de sesión de BD, fixtures para un administrador y un capturista y un helper que devuelva el encabezado
   Authorization con token.
2. Escribe pruebas para ≥ 8 endpoints distintos, incluyendo: registro y login, GET protegido sin token (401),
   endpoint de administrador con capturista (403) y con administrador (200), CRUD de alumnos, creación de
   grupo con cruce (409), inscripción duplicada (409) y clima con httpx simulado.
3. Nombra cada prueba por el criterio que cubre (por ejemplo test_hu_01_3_capturista_no_puede_listar_usuarios).

RESTRICCIONES: sin acceso a internet ni a servicios reales; pruebas independientes entre sí; sin sleeps.

ENTREGABLE: archivos, comando `pytest -q` y una tabla "criterio de aceptación → prueba".

VERIFICACIÓN: `pytest -q` pasa dos veces seguidas y en cualquier orden (`-p no:randomly` y con randomly si
está instalado).
```

**Revisión humana:** que cada prueba **falle** si rompen la regla (probar quitando temporalmente la
validación); que ninguna dependa del orden.

---

## P11 · Docker, Compose y CI — *Luis (Docker/Compose) y Carlos (CI) · martes*

```text
ROL: Asistente de DevOps para un proyecto estudiantil.

CONTEXTO: Lee CLAUDE.md y la estructura del repo (monorepo). Requisito: `docker compose up` levanta
frontend, backend y PostgreSQL con un solo comando, copiando antes .env.example a .env.

TAREA (Luis):
1. backend/Dockerfile (python:3.12-slim, usuario sin privilegios, instala requirements, copia backend/ y db/).
   El contexto de build es la raíz del repo para poder copiar db/migrations.
2. frontend/Dockerfile en dos etapas: build con Node LTS y servir los estáticos con nginx.
3. infra/docker-compose.yml: servicios db (postgres con volumen y healthcheck), backend (espera a la BD,
   corre `alembic upgrade head` y el seed solo si la tabla está vacía) y frontend. Variables desde .env.
4. .env.example con TODAS las variables, valores de ejemplo NO reales, y CORS_ORIGINS limitado al frontend.

TAREA (Carlos): .github/workflows/ci.yml que en cada push y PR ejecute (a) backend: instalar dependencias,
`ruff check` y `pytest`; (b) frontend: `npm ci`, `npm run lint` y `npm run build`. Con caché de pip/npm.

RESTRICCIONES: no incluir secretos reales; .env en .gitignore; versiones de imágenes fijas (no `latest`).

ENTREGABLE: archivos y los comandos exactos para levantar y apagar el sistema.

VERIFICACIÓN: desde un clon limpio, `copy .env.example .env` y `docker compose -f infra/docker-compose.yml up
--build` deja todo funcionando en < 3 minutos; el CI queda en verde.
```

**Revisión humana:** `git grep` de contraseñas/llaves antes de cada PR; que el backend no arranque antes
que la BD; que el contenedor no corra como root; cronometrar el arranque desde cero.

---

## P12 · Revisión de seguridad (OWASP A01 y A02) — *ambos · miércoles*

```text
ROL: Revisor de seguridad. NO modifiques archivos; solo analiza y reporta.

CONTEXTO: Lee CLAUDE.md. Proyecto FastAPI + React. Debemos revisar OWASP Top 10:2025 A01 (control de
acceso) y A02 (configuración incorrecta), y reportarlo en nuestro documento de seguridad.

TAREA:
1. Lista TODOS los endpoints de backend/app/routers y, para cada uno, indica si exige sesión y qué rol, y si
   la verificación ocurre en el servidor. Marca cualquiera sin protección.
2. Busca: secretos o contraseñas en el código y en el historial de Git (`git log -p` por patrones), CORS
   abierto (`*`), DEBUG activo, mensajes de error que filtren datos internos, endpoints que devuelvan
   password_hash, y rutas que un capturista pueda usar para modificar datos de otro rol.
3. Revisa requirements.txt y package.json: paquetes inexistentes, abandonados o con vulnerabilidades
   conocidas.

ENTREGABLE: tabla "hallazgo → archivo:línea → severidad → arreglo sugerido", ordenada por severidad. Si no
encuentras nada en una categoría, dilo explícitamente.

NO HAGAS: no ejecutes ataques ni escaneos contra servidores en internet; solo revisa el repositorio local.
```

**Revisión humana:** verificar cada hallazgo antes de aplicarlo; decidir qué arreglar y documentar lo
demás. Este resultado alimenta la sección de seguridad del reporte y la **reflexión crítica** de `AI_USAGE.md`
(ej.: "la IA dejó un endpoint sin `require_role` y lo detectamos con esta revisión").

---

## P13 · Modo tutor para la defensa — *ambos · miércoles (y siempre que no entiendan algo)*

```text
ROL: Eres mi tutor de Programación Web. NO escribas ni cambies código; ayúdame a entenderlo.

CONTEXTO: Voy a defender este proyecto en una demo. El profesor puede pedirme que explique cualquier parte y
el flujo completo de una petición, desde el clic en React hasta la consulta en PostgreSQL.

TAREA: Toma el archivo <ruta del archivo> (y los que importe) y:
1. Explícalo en lenguaje simple, bloque por bloque, y dime por qué está escrito así.
2. Traza el flujo de una petición concreta: <ej. "crear un grupo con cruce de horario"> pasando por
   componente React → fetch → ruta FastAPI → servicio → modelo SQLAlchemy → PostgreSQL → respuesta.
3. Hazme 5 preguntas como las que haría un profesor y espera mi respuesta antes de corregirme, una a la vez.
4. Dime qué parte sería más difícil de defender y por qué.

RESTRICCIONES: usa el vocabulario del manual del curso. Si algo del código es más complicado de lo
necesario, dilo para que lo simplifiquemos.
```

**Revisión humana:** si no pueden contestar, **simplifiquen el código** o estudien esa parte antes del
jueves. Este prompt es también la base del ensayo cruzado del miércoles.

---

## Bitácora (plantilla para `AI_USAGE.md`)

| Fecha | Integrante | Herramienta / modelo | Prompt (resumen fiel) | Archivos afectados | Ajustes humanos |
|---|---|---|---|---|---|
| 2026-11-21 | Luis | Claude Code / Claude Sonnet 5.5 | P1: modelos SQLAlchemy + migración + seed | `backend/app/models/`, `db/` | _(qué corrigieron)_ |

Los 7 puntos que exige `AI_USAGE.md`: **(1)** herramientas y modelos y quién las usó · **(2)** harness y modo
(agente que edita archivos y ejecuta comandos, en la terminal/VS Code) · **(3)** archivos de contexto
(`CLAUDE.md`, plantillas de prompts de este documento) · **(4)** bitácora · **(5)** marcado en commits ·
**(6)** estimación de % de código con IA por carpeta · **(7)** reflexión crítica de ½ página con un error
concreto que la IA introdujo y cómo lo detectaron.
