# Extra-Liebres v2 — Propuesta ampliada

> Esta versión toma la **Tarea 1** (propuesta original) y la completa con la estructura del documento
> "Requerimientos del cliente" del profesor: actores, épicas, historias de usuario con criterios de
> aceptación (Dado / Cuando / Entonces), reglas de negocio, requerimientos no funcionales y alcance.
> Será el contenido del **primer issue** del repositorio y la base del backlog (≥ 15 historias).
>
> Lo que **se agregó** respecto a la Tarea 1 está marcado con ➕. Los valores marcados con ⚠️ son
> supuestos nuestros que conviene confirmar con el profesor (que actúa como cliente).

**Equipo:** Luis David Reyna Morisco (22111443) · Carlos Limones Ayala (22111415)
**Materia:** Programación Web (AEB-1055) · ITCJ · Docente: Dr. Roberto Contreras Masse
**Entrega y demo:** jueves 26 de noviembre de 2026

---

## 1. Problema y propuesta

Hasta 2022 el Departamento de Actividades Extraescolares del ITCJ guardó en papel los registros de los
alumnos que cursaron actividades extraescolares. Desde 2023 se usa SIISAE, pero **los registros
anteriores nunca se migraron**, así que no se pueden consultar.

En 2024 se hizo *Extra-Liebres* (PHP + MySQL) para digitalizar esos registros. Funciona, pero tiene la
lógica de consulta dispersa en scripts ligados al frontend, no tiene capa de API ni datos bien
normalizados, y a veces responde lento.

**Propuesta:** rehacer Extra-Liebres como una **SPA en React** que consume una **API REST en FastAPI**
con base de datos **PostgreSQL**, para dar de alta, consultar, editar y dar de baja alumnos,
promotores, actividades, semestres, grupos e inscripciones con su desempeño. ➕ Con inicio de sesión
por rol, un tablero de resumen y un aviso de clima para las actividades al aire libre.

## 2. Actores

| Actor | Quién es | Qué necesita | Prioridad |
|---|---|---|---|
| **Administrador** | Jefatura del Departamento | Todo lo del capturista + administrar usuarios, roles y catálogos | I |
| **Capturista** | Personal administrativo | Capturar y consultar alumnos, grupos e inscripciones; ver el tablero | I |
| **Lector** | Cualquier persona que se registra | Ver el tablero y las listas de grupos y catálogos, sin datos de alumnos y sin cambiar nada | I |

Una persona tiene **un solo rol**. Solo el administrador cambia roles. Las cuentas nuevas nacen como **lector**, que no ve
datos de alumnos: los registros contienen datos personales (ver RN-07).

## 3. Épicas e historias de usuario

| ID | Épica | Historias (I / D) |
|---|---|---|
| E1 | Cuentas y acceso | 4 / 0 |
| E2 | Alumnos | 4 / 0 |
| E3 | Catálogos | 3 / 0 |
| E4 | Grupos | 3 / 1 |
| E5 | Inscripción y evaluación | 2 / 1 |
| E6 | Consulta transversal | 1 / 1 |
| E7 | Indicadores | 1 / 1 |
| E8 | Servicio externo (clima) | 1 / 0 |
| | **Total: 23 historias** | **19 I / 4 D** |

Prioridad **I** = indispensable · **D** = deseable. Cada historia es un issue en GitHub
(`HU-01.1`, `HU-01.2`, …) y cada criterio se usa como caso de prueba.

### E1. Cuentas y acceso

**HU-01.1 Crear una cuenta · I · Visitante**
Como persona del departamento, quiero registrarme, para poder entrar al sistema.
- CA1 Dado que lleno nombre, correo y contraseña válidos, cuando envío el registro, entonces se crea mi cuenta con rol Lector, que solo ve el tablero y los grupos.
- CA2 Dado que el correo ya existe, cuando envío el registro, entonces veo un mensaje claro y no se crea otra cuenta.
- CA3 Dado que la contraseña tiene menos de 8 caracteres o no mezcla letras y números, cuando envío, entonces veo el error junto al campo sin perder lo capturado.

**HU-01.2 Iniciar y cerrar sesión · I · Todos**
Como usuario, quiero entrar y salir, para que nadie use mi cuenta en un equipo compartido.
- CA1 Dado que mis datos son correctos, cuando inicio sesión, entonces veo mi nombre y las opciones de mi rol.
- CA2 Dado que el correo o la contraseña son incorrectos, cuando intento entrar, entonces el mensaje no revela cuál falló.
- CA3 Dado que cerré sesión, cuando escribo la dirección de una pantalla privada, entonces se me pide iniciar sesión.
- CA4 Dado que mi sesión expiró (⚠️ 60 minutos), cuando intento una acción, entonces se me pide iniciar sesión otra vez.

**HU-01.3 Hacer solo lo que mi rol permite · I · Todos**
Como departamento, queremos que cada quien haga solo lo que su rol permite, para proteger los datos.
- CA1 Dado que soy Capturista o Lector, cuando navego, entonces no veo opciones de administración; si soy Lector, tampoco veo Alumnos ni Consultas.
- CA2 Dado que soy Capturista y conozco la ruta de una función de administrador, cuando la intento por cualquier medio (por ejemplo desde `/docs`), entonces el servidor responde 403 y ningún dato cambia.
- CA2b Dado que soy Lector y llamo por cualquier medio una ruta de alumnos, búsqueda, consultas, inscripciones o de crear, editar o eliminar grupos, entonces el servidor responde 403 y ningún dato cambia.
- CA3 Dado que no tengo sesión, cuando llamo cualquier endpoint privado, entonces el servidor responde 401.

**HU-01.4 Administrar usuarios y roles · I · Administrador**
Como administrador, quiero ver las cuentas y cambiar roles, para dar permisos y frenar abusos.
- CA1 Dado que soy administrador, cuando consulto usuarios, entonces puedo buscar por nombre o correo y paginar.
- CA2 Dado que cambio el rol de una persona, cuando guardo, entonces sus permisos cambian en su siguiente petición.
- CA3 Dado que suspendo una cuenta, cuando esa persona intenta entrar, entonces no puede y sus datos se conservan.
- CA4 Dado que soy el único administrador activo, cuando intento quitarme el rol o suspenderme, entonces el sistema lo impide.

### E2. Alumnos

**HU-02.1 Dar de alta un alumno · I · Capturista, administrador**
Como capturista, quiero registrar un alumno, para guardar su historial.
- CA1 Dado que capturo número de control, nombre, apellidos, sexo, carrera y campus, cuando guardo, entonces el alumno queda registrado.
- CA2 Dado que el número de control ya existe, cuando guardo, entonces se rechaza con un mensaje claro (409).
- CA2b Dado que el número de control no tiene exactamente 8 dígitos (solo números) o es mayor a 26999999, cuando guardo, entonces se rechaza (422) y el campo no deja escribir letras ni más de 8 dígitos.
- CA3 Dado que falta un dato obligatorio, cuando guardo, entonces se indica qué corregir, tanto en pantalla como en el servidor.

**HU-02.2 Buscar y listar alumnos · I · Capturista, administrador**
Como capturista, quiero buscar alumnos, para encontrar rápido un registro.
- CA1 Dado que escribo parte del nombre, apellido o número de control, cuando busco, entonces veo los alumnos que coinciden.
- CA2 Dado que filtro por carrera, campus o estado (activo/baja), cuando aplico el filtro, entonces solo veo los que cumplen todos los filtros.
- CA3 Dado que hay más de 10 resultados, cuando consulto, entonces se muestran de 10 en 10 con paginación y el total.
- CA4 Dado que ningún alumno cumple, cuando busco, entonces veo un mensaje de "sin resultados" y la opción de limpiar filtros.

**HU-02.3 Editar y dar de baja a un alumno · I · Capturista, administrador**
Como capturista, quiero corregir los datos de un alumno o darlo de baja, sin perder su historial.
- CA1 Dado que edito un alumno, cuando guardo, entonces los cambios se reflejan en la lista.
- CA2 Dado que doy de baja a un alumno, cuando confirmo, entonces queda inactivo, ya no aparece por defecto en la lista y su historial se conserva (RN-02).
- CA3 Dado que un alumno está de baja, cuando lo reactivo, entonces vuelve a aparecer.

**HU-02.4 Ver el historial de un alumno · I · Capturista, administrador**
Como capturista, quiero ver qué actividades cursó un alumno y cuándo, para atender consultas.
- CA1 Dado que abro un alumno, cuando veo su historial, entonces aparecen actividad, semestre, promotor, calificación y desempeño, del semestre más reciente al más antiguo.
- CA2 Dado que el alumno no tiene inscripciones, cuando abro su historial, entonces veo un mensaje que lo indica.

### E3. Catálogos

**HU-03.1 Administrar promotores · I · Administrador** (consulta: ambos roles)
- CA1 Dado que soy administrador, cuando creo, edito o desactivo un promotor (RFC, nombre, apellidos), entonces el cambio se refleja en los formularios de grupo.
- CA2 Dado que el RFC ya existe o no tiene formato válido (12 o 13 caracteres), cuando guardo, entonces se rechaza.
- CA3 Dado que un promotor tiene grupos, cuando intento eliminarlo, entonces solo se permite desactivarlo (RN-08).

**HU-03.2 Administrar actividades extraescolares · I · Administrador**
- CA1 Dado que soy administrador, cuando creo o edito una actividad (nombre, ➕ tipo: deportiva / cultural / cívica, ➕ ¿al aire libre?), entonces queda disponible al crear grupos.
- CA2 Dado que una actividad tiene grupos, cuando intento eliminarla, entonces solo se permite desactivarla.
- CA3 Dado que la lista es larga, cuando la consulto, entonces puedo buscar por nombre y paginar.

**HU-03.3 Administrar semestres · I · Administrador**
- CA1 Dado que soy administrador, cuando creo un semestre (año de 2000 a 2027 y periodo), entonces queda disponible al crear grupos. Solo hay dos periodos: enero-junio y agosto-diciembre.
- CA2 Dado que ya existe un semestre con el mismo año y mes de inicio, cuando guardo, entonces se rechaza.
- CA3 Dado que un semestre tiene grupos, cuando intento eliminarlo, entonces el sistema lo impide.

### E4. Grupos

**HU-04.1 Crear un grupo validando cruces · I · Capturista, administrador**
Como capturista, quiero crear un grupo asignando actividad, semestre, promotor, día, horario y lugar, sin cruces.
- CA1 Dado que capturo todos los datos y no hay conflictos, cuando guardo, entonces el grupo se crea.
- CA2 Dado que la hora de término no es posterior a la de inicio, cuando guardo, entonces se rechaza.
- CA2b Dado que la actividad dura menos de 1 hora, cuando guardo, entonces se rechaza (422).
- CA3 Dado que el promotor ya tiene un grupo ese día, en ese semestre y con horario traslapado, cuando guardo, entonces se rechaza indicando el grupo en conflicto (409).
- CA4 Dado que el aula ya está ocupada ese día, en ese semestre y con horario traslapado, cuando guardo, entonces se rechaza indicando el grupo en conflicto (409).

**HU-04.2 Formulario dinámico según el tipo de actividad · I · Capturista, administrador**
Como capturista, quiero que el formulario me pida solo lo que aplica a la actividad, para capturar rápido y bien.
- CA1 Dado que elijo una actividad **deportiva**, cuando la selecciono, entonces aparece un selector de instalación (cancha, gimnasio, pista…) en lugar del campo de aula.
- CA2 Dado que elijo una actividad **cultural o cívica**, cuando la selecciono, entonces aparece el campo de aula de texto.
- CA3 Dado que la actividad es **al aire libre**, cuando la selecciono, entonces veo el pronóstico del clima de Juárez junto al formulario (HU-08.1).
- CA4 Dado que falta un dato obligatorio, cuando envío, entonces el cliente lo marca y el servidor también lo rechaza si alguien salta la pantalla.

**HU-04.3 Listar y filtrar grupos · I · Capturista, administrador**
- CA1 Dado que abro grupos, cuando filtro por semestre, actividad, promotor o día, entonces veo solo los que cumplen todos los filtros.
- CA2 Dado que hay más de 10 grupos, cuando consulto, entonces se muestran de 10 en 10 con paginación y el total.
- CA3 Dado que ningún grupo cumple, cuando busco, entonces veo un mensaje claro.

**HU-04.4 Editar y eliminar un grupo · D · Capturista, administrador**
- CA1 Dado que edito un grupo, cuando guardo, entonces se vuelven a validar los cruces.
- CA2 Dado que un grupo tiene alumnos inscritos, cuando intento eliminarlo, entonces el sistema lo impide (409).

### E5. Inscripción y evaluación

**HU-05.1 Inscribir alumnos a un grupo · I · Capturista, administrador**
- CA1 Dado que abro un grupo, cuando agrego un alumno activo, entonces queda inscrito.
- CA2 Dado que el alumno ya está inscrito en ese grupo, cuando intento inscribirlo otra vez, entonces se rechaza (409).
- CA3 Dado que el alumno está de baja, cuando intento inscribirlo, entonces se rechaza.

**HU-05.2 Registrar calificación y desempeño · I · Capturista, administrador**
- CA1 Dado que un alumno está inscrito, cuando capturo su calificación (0 a 100), entonces el sistema calcula y guarda su desempeño (RN-05).
- CA2 Dado que la calificación está fuera de 0 a 100, cuando guardo, entonces se rechaza.
- CA3 Dado que corrijo una calificación, cuando guardo, entonces el desempeño se recalcula.

**HU-05.3 Dar de baja una inscripción · D · Capturista, administrador**
- CA1 Dado que un alumno está inscrito y sin calificación, cuando lo quito del grupo, entonces la inscripción se elimina.
- CA2 Dado que ya tiene calificación, cuando intento quitarlo, entonces se pide confirmación explícita.

### E6. Consulta transversal

**HU-06.1 Alumnos inscritos por actividad y/o semestre · I · Capturista, administrador**
- CA1 Dado que elijo una actividad y/o un semestre, cuando consulto, entonces veo la lista de alumnos inscritos con su grupo, calificación y desempeño.
- CA2 Dado que no hay inscritos con esos criterios, cuando consulto, entonces veo un mensaje claro.
- CA3 Dado que hay más de 10 resultados, cuando consulto, entonces se paginan.

**HU-06.2 Búsqueda global · D · Capturista, administrador**
- CA1 Dado que escribo un texto en el buscador superior, cuando busco, entonces veo coincidencias en alumnos y grupos, agrupadas por tipo.

### E7. Indicadores

**HU-07.1 Tablero de resumen · I · Capturista, administrador**
Como jefatura, quiero ver cifras del departamento, para reportar la participación.
- CA1 Dado que abro el tablero, cuando carga, entonces veo el total de alumnos activos, grupos e inscripciones del semestre elegido.
- CA2 Dado que abro el tablero, cuando carga, entonces veo una gráfica de inscritos por actividad.
- CA3 Dado que abro el tablero, cuando carga, entonces veo una gráfica de la distribución por desempeño y el promedio de calificación.
- CA4 Dado que cambio el semestre, cuando aplico el filtro, entonces todos los indicadores se recalculan.

**HU-07.2 Exportar información · D · Administrador**
- CA1 Dado que consulto inscritos de un semestre, cuando exporto en CSV, entonces el archivo abre en una hoja de cálculo.
- CA2 Dado que exporto en XML, cuando abro el archivo, entonces es XML bien formado con la estructura documentada (➕ punto extra: intercambio XML).

### E8. Servicio externo

**HU-08.1 Pronóstico de clima para actividades al aire libre · I · Todos**
Como capturista, quiero ver el clima de Ciudad Juárez, para saber si una actividad al aire libre puede verse afectada.
- CA1 Dado que abro el tablero, cuando carga, entonces veo temperatura actual y probabilidad de lluvia de las próximas horas, obtenidas del backend (que consulta Open-Meteo).
- CA2 Dado que hay ⚠️ 50 % o más de probabilidad de lluvia, cuando entro al tablero, entonces veo un aviso destacado para las actividades al aire libre.
- CA3 Dado que la información tiene más de 1 hora, cuando alguien consulta, entonces el backend la actualiza (caché de 1 hora, RN-10).
- CA4 Dado que el servicio externo no responde, cuando entro, entonces el sistema sigue funcionando y muestra "Pronóstico no disponible".
- CA5 Dado que Open-Meteo rechaza la consulta (por ejemplo 429 por límite de uso), cuando entro, entonces el backend usa el servicio de respaldo (wttr.in) y, si también falla, muestra la última copia de menos de 6 horas; solo si no hay ninguna aparece "Pronóstico no disponible".

## 4. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | El **número de control** es el identificador del alumno: texto único de exactamente 8 dígitos (conserva los ceros del inicio) y, de momento, no mayor a 26999999. El **RFC** identifica al promotor. |
| RN-02 | Un alumno **solo se elimina si no está inscrito en ningún grupo** (si lo está, 409). Para conservar su historial se da de baja (inactivo). |
| RN-03 | **No se permiten cruces**: un promotor o un aula no pueden tener dos grupos con horario traslapado el mismo día y semestre. Hora de inicio < hora de término. |
| RN-04 | Un alumno no puede inscribirse dos veces al mismo grupo, ni estando de baja. |
| RN-05 | Calificación entera de 0 a 100. El **desempeño lo calcula el servidor** (el usuario no lo captura): Excelente 95–100, Notable 85–94, Bueno 75–84, Suficiente 70–74, Insuficiente < 70 (escala del TecNM). ⚠️ Confirmar con el profesor que este es el criterio que quiere. |
| RN-06 | Un rol por persona (administrador, capturista o lector). Las cuentas nuevas son lector. Solo el administrador cambia roles. Siempre debe existir al menos un administrador activo. |
| RN-07 | **Privacidad:** los datos de alumnos son personales (Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados). Solo se ven con sesión. Las contraseñas se guardan con hash y nunca se muestran. Los datos semilla del repositorio son **ficticios**. |
| RN-08 | Un registro referenciado por otros (promotor, actividad, semestre) no se elimina: se desactiva, o el sistema responde 409. |
| RN-09 | Todas las fechas y horas se muestran en hora local de Ciudad Juárez (`America/Ciudad_Juarez`). |
| RN-10 | El pronóstico se consulta solo desde el backend y se guarda en caché 1 hora. Si falla Open-Meteo se usa wttr.in como respaldo (solo se le mandan las coordenadas de Ciudad Juárez); si también falla, se muestra la última copia de menos de 6 horas y no se vuelve a intentar durante 1 minuto. El sistema siempre sigue funcionando. |
| RN-11 | Los listados se paginan de 10 en 10 (valor ajustable, documentado en el reporte). |

## 5. Requerimientos no funcionales

| ID | Requerimiento | Cómo se verifica |
|---|---|---|
| RNF-01 | Funciona en celular y escritorio (desde 360 px de ancho), con al menos 2 breakpoints | Capturas y revisión en la demo |
| RNF-02 | Accesible: HTML semántico, `label` en formularios, contraste, texto alternativo, uso con teclado | Lighthouse accesibilidad ≥ 90 |
| RNF-03 | En internet con URL pública el día de la entrega | Demo |
| RNF-04 | `docker compose up` levanta frontend, backend y BD en < 3 minutos | Demo (plan B) |
| RNF-05 | Seguridad: hash de contraseñas, JWT, autorización por rol en el servidor, CORS restringido, sin secretos en Git | Pruebas de endpoints protegidos y revisión OWASP A01/A02 |
| RNF-06 | Los listados responden en < 3 s con los datos semilla | Prueba manual |
| RNF-07 | Pruebas automáticas con pytest (≥ 8 endpoints, incluido uno protegido) y CI en verde | GitHub Actions |
| RNF-08 | Toda la interfaz en español de México | Revisión en la demo |
| RNF-09 | Datos semilla: ⚠️ ~200 alumnos, 10 promotores, 8 actividades, 6 semestres, ~40 grupos, ~600 inscripciones (ficticios) y una cuenta por rol | Demo y README |

## 6. Modelo de datos (Tarea 1 + cambios)

```
usuario ➕(id PK, nombre, correo UNIQUE, password_hash, rol, activo, creado_en)

alumno(nocontrol PK, nombre, apaterno, amaterno, sexo, carrera, campus, ➕activo)
promotor(rfc PK, nombre, apaterno, amaterno, ➕activo)
extraescolar(idextraescolar PK, nombreextra, ➕tipo, ➕al_aire_libre, ➕activo)
semestre(idsemestre PK, mesinicio, mestermino, anio)
grupo(idgrupo PK, dia, horainicio, horatermino, aula, idsemestre FK, idextraescolar FK, rfcpromotor FK)
alumno_grupo(nocontrol FK, idgrupo FK, calificacion, desempenio, PK compuesta)
```

Relaciones: **promotor 1:N grupo**, **extraescolar 1:N grupo**, **semestre 1:N grupo**,
**alumno N:M grupo** (a través de `alumno_grupo`, que además guarda calificación y desempeño).

Cambios sobre la Tarea 1:
- ➕ `usuario` (no existía; es necesaria para login y roles).
- ➕ `activo` en alumno, promotor y extraescolar (baja lógica, RN-02/RN-08).
- ➕ `tipo` y `al_aire_libre` en extraescolar (alimentan el formulario dinámico y el clima).
- `desempenio` pasa a ser **calculado** a partir de `calificacion` (RN-05).
- Restricciones: `CHECK (horainicio < horatermino)`, `CHECK (calificacion BETWEEN 0 AND 100)`,
  `UNIQUE (anio, mesinicio)` en semestre, `sexo` y `tipo` limitados a valores válidos.
- `carrera` es una lista fija de 16 carreras (`backend/app/core/constantes.py`; el servidor rechaza cualquier otra) y `campus` queda como texto (no hace falta catálogo propio).

## 7. Endpoints de la API (≥ 12 requeridos; la API final tiene 43 operaciones, ver `seguridad.md`)

| Grupo | Método y ruta | Rol |
|---|---|---|
| Auth | `POST /api/auth/register` · `POST /api/auth/login` · `GET /api/auth/me` | público / público / sesión |
| Usuarios | `GET /api/usuarios` · `PATCH /api/usuarios/{id}` | administrador |
| Alumnos | `GET /api/alumnos` (q, carrera, campus, activo, page, size) · `POST` · `GET /{nocontrol}` · `PUT /{nocontrol}` · `DELETE /{nocontrol}` (solo si no tiene inscripciones; la baja lógica es `PUT` con `activo=false`) · `GET /{nocontrol}/historial` | sesión |
| Promotores | `GET` · `POST` · `PUT /{rfc}` · `DELETE /{rfc}` | GET sesión; resto administrador |
| Extraescolares | `GET` · `POST` · `PUT /{id}` · `DELETE /{id}` | GET sesión; resto administrador |
| Semestres | `GET` · `POST` · `PUT /{id}` · `DELETE /{id}` | GET sesión; resto administrador |
| Grupos | `GET` (semestre, extraescolar, promotor, dia, page) · `POST` · `GET /{id}` · `PUT /{id}` · `DELETE /{id}` | sesión |
| Inscripciones | `GET /api/grupos/{id}/inscritos` · `POST /api/grupos/{id}/inscripciones` · `PUT /api/grupos/{id}/inscripciones/{nocontrol}` (evaluar) · `DELETE …` | sesión |
| Consultas | `GET /api/consultas/inscritos` (extraescolar, semestre, page) | sesión |
| Búsqueda | `GET /api/busqueda` (q) (D, entregado) | sesión |
| Tablero | `GET /api/dashboard/resumen` (semestre) | sesión |
| Clima | `GET /api/clima` (llama a Open-Meteo) | sesión |
| Exportar | `GET /api/export/inscritos.csv` · `GET /api/export/inscritos.xml` (extraescolar, semestre; ver [`exportacion.md`](exportacion.md)) | administrador (D, entregado) |
| Sistema | `GET /api/health` | público |

Códigos HTTP: 200/201/204 éxito · 400/422 validación · 401 sin sesión · 403 sin permiso · 404 no existe ·
409 conflicto (duplicado, cruce de horario, registro referenciado).

## 8. Pantallas (rutas de React, ≥ 4 requeridas)

`/login` · `/registro` · `/` (tablero) · `/alumnos` · `/alumnos/nuevo` · `/alumnos/:nocontrol` ·
`/grupos` · `/grupos/nuevo` · `/grupos/:id` (inscritos y evaluación) · `/consultas` · `/buscar` ·
`/catalogos` (pestañas: promotores, actividades, semestres; solo admin) · `/usuarios` (solo admin)

Toda vista que consulta la API muestra estado de **carga**, **error** y **vacío**.

## 9. Fuera de alcance

- Migrar automáticamente los registros de SIISAE o conectarse a ese sistema.
- Aplicación móvil nativa.
- Consulta pública o por parte de los alumnos.
- Envío de correos o notificaciones.
- Captura de los registros reales en papel (el repositorio usa solo datos ficticios).

## 10. Glosario

| Término | Significado |
|---|---|
| Extraescolar | Actividad deportiva, cultural o cívica que los alumnos cursan fuera de sus materias |
| Promotor | Responsable de impartir una actividad |
| Grupo | Una actividad en un semestre, con promotor, día, horario y lugar |
| Inscripción | Relación de un alumno con un grupo; guarda calificación y desempeño |
| Desempeño | Nivel cualitativo (Excelente … Insuficiente) derivado de la calificación |
| Baja lógica | Marcar como inactivo sin borrar, para conservar el historial |
| SIISAE | Plataforma que el departamento usa desde 2023 |
