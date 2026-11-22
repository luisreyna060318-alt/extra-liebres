# Lighthouse y accesibilidad: puntajes antes y después

Cumple RNF-02 de `docs/propuesta-v2.md` (accesibilidad con Lighthouse ≥ 90). Todos los números salen de corridas
reales hechas el **21 de noviembre de 2026**; ninguno está redondeado a favor.

## Cómo se midió

- **Sistema real**: copia limpia del repositorio, `docker compose -p lh up --build -d --wait` (PostgreSQL, backend en
  `:8000` y frontend de producción servido por nginx en `:5173`) con los datos de ejemplo del seed.
- **Navegador y versiones**: Lighthouse **13.6.0** controlando Microsoft Edge **158.0.4370.33** (Chromium) sin ventana
  (`headless`) con `puppeteer-core` 25.18.1. En la computadora de prueba no hay Google Chrome instalado; Edge usa el
  mismo motor y es compatible con Lighthouse, pero el puntaje de rendimiento puede variar un poco contra Chrome.
- **Categorías**: rendimiento, accesibilidad, buenas prácticas y SEO. Móvil (configuración predeterminada de Lighthouse,
  con CPU y red limitadas) y escritorio (`desktop-config`).
- **Pantallas autenticadas**: el script pide el token a la API con el usuario administrador de prueba (el correo y la
  contraseña se leen del `.env` local en tiempo de ejecución; no se escriben en ningún archivo) y lo guarda en
  `localStorage` con la misma clave que usa la app. Lighthouse corre con `disableStorageReset` para conservar la sesión.
  `/login` y `/registro` se miden **sin** sesión. Se midieron `/`, `/alumnos`, `/grupos`, `/grupos/1`, `/consultas`,
  `/catalogos` y `/usuarios`.
- **Herramientas solo en la máquina de prueba**: `lighthouse`, `puppeteer-core` y `axe-core` 4.14.1 se instalaron en una
  carpeta temporal fuera del repositorio. **No se agregó ninguna dependencia** a `frontend/package.json` ni al backend.
  Los scripts usados están en `docs/lighthouse/scripts/` solo como referencia (`medir.mjs`, `axe.mjs`, `estados.mjs`;
  necesitan la variable `ENVFILE` con la ruta del `.env`).
- **Reportes guardados**: cada reporte HTML pesa 0.6 a 0.75 MB y cada JSON 0.5 a 0.65 MB, más de los 500 kB permitidos,
  así que **no se guardaron**. Solo se guardan los puntajes en `docs/lighthouse/antes.json` y
  `docs/lighthouse/despues.json`.

## Resultado de Lighthouse

La accesibilidad **ya estaba en 100 en las 9 pantallas, en móvil y escritorio, antes de tocar nada**, y sigue en 100.
Lighthouse solo ejecuta un subconjunto de las reglas de axe-core y no ve el contraste del anillo de foco, los estados
que aparecen al interactuar ni el desbordamiento horizontal, por eso se hicieron las comprobaciones de la sección
siguiente y de ahí salieron las correcciones.

| Pantalla | Modo | Acces. antes | Acces. después | Rend. antes | Rend. después | Buenas prác. | SEO antes → después |
|---|---|---|---|---|---|---|---|
| `/login` | móvil | 100 | 100 | 98 | 100 | 100 → 100 | 91 → 100 |
| `/login` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/registro` | móvil | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/registro` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/` | móvil | 100 | 100 | 85 | 90 | 100 → 100 | 91 → 100 |
| `/` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/alumnos` | móvil | 100 | 100 | 92 | 93 | 100 → 100 | 91 → 100 |
| `/alumnos` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/grupos` | móvil | 100 | 100 | 90 | 90 | 100 → 100 | 91 → 100 |
| `/grupos` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/grupos/1` | móvil | 100 | 100 | 90 | 92 | 100 → 100 | 91 → 100 |
| `/grupos/1` | escritorio | 100 | 100 | 99 | 87 | 100 → 100 | 91 → 100 |
| `/consultas` | móvil | 100 | 100 | 89 | 89 | 100 → 100 | 91 → 100 |
| `/consultas` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/catalogos` | móvil | 100 | 100 | 93 | 92 | 100 → 100 | 91 → 100 |
| `/catalogos` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |
| `/usuarios` | móvil | 100 | 100 | 90 | 91 | 100 → 100 | 91 → 100 |
| `/usuarios` | escritorio | 100 | 100 | 100 | 100 | 100 → 100 | 91 → 100 |

**Cómo leer el rendimiento**: los cambios de este commit solo tocan colores, un borde, un nivel de encabezado, una
cuadrícula y el foco; no deberían cambiar el rendimiento. Las diferencias son **ruido de la medición**. Se hicieron tres
corridas completas (antes y dos después) y, por ejemplo, `/` en móvil dio 85, 80 y 90, y `/grupos/1` en escritorio dio
99, 99 y 87. No se debe presumir que el rendimiento "mejoró" ni que "empeoró". Referencia: en móvil el rendimiento
queda entre 80 y 93 en las pantallas privadas; el JavaScript se entrega en un solo archivo de unos 720 kB (Vite avisa
en cada `npm run build`), y `/grupos/1` en móvil tuvo un desplazamiento de diseño acumulado (CLS) de 0.20 en la
corrida de antes, arriba del 0.1 recomendado. No es un tema de accesibilidad y no se corrigió aquí.

**SEO 91 → 100**: la única auditoría fallida era `robots.txt is not valid`, porque nginx devolvía `index.html` cuando el
navegador pedía `/robots.txt`. Se agregó `frontend/public/robots.txt` (permite todo; las pantallas privadas piden sesión).

## Comprobaciones adicionales (lo que Lighthouse no cubre)

Con axe-core 4.14.1 (reglas WCAG 2.0, 2.1 y 2.2 A y AA más buenas prácticas) en 34 combinaciones de pantalla y ancho
(1280 y 320 px, incluida cada pantalla con errores de validación y `/404`), y 24 estados interactivos (12 estados, en 1280 y 360 px):
diálogo de baja de alumno, paneles de confirmación, paneles de formulario de promotores, actividades y semestres,
pestañas de catálogos y formularios enviados vacíos. También se revisó, con Edge, el desbordamiento horizontal y el
contraste del anillo de foco recorriendo la página con Tab.

| Hallazgo | Antes | Después |
|---|---|---|
| Anillo de foco naranja `#e08a00` sobre fondos claros (WCAG 1.4.11 pide 3:1) | 2.49:1 sobre el fondo gris y 2.69:1 sobre blanco | 4.64:1 sobre el fondo gris y 5.02:1 sobre blanco (`#b45309`); en el encabezado rojo del logo, anillo blanco de 5.88:1 |
| Bordes de campos de formulario `#cbd2d9` sobre blanco (WCAG 1.4.11) | 1.53:1 | 3.66:1 (`#7b8794`) |
| Encabezados saltaban de nivel (h1 → h3) en `/usuarios` al abrir la confirmación (axe `heading-order`) | 1 violación en 1280 y 360 px | 0 violaciones |
| `/alumnos` se desbordaba 14 px a la derecha en 360 px por los selects de Carrera y Campus (reflujo, WCAG 1.4.10) | desbordamiento de 14 px | sin desbordamiento en ninguna de las 9 pantallas |
| Al cambiar de pantalla con el menú el foco se quedaba en el enlace pulsado (SPA sin recarga) | foco en el enlace | el foco pasa al contenido (`<main>`); comprobado con puppeteer |
| Violaciones de axe: las 34 combinaciones de pantalla y ancho | 0 | 0 |
| Violaciones de axe: los 24 estados interactivos | 2 (las dos de `heading-order`, arriba) | 0 |

Comprobaciones que ya estaban bien y no se tocaron: `lang="es-MX"`, títulos de página únicos por pantalla, un solo
`h1` por pantalla, landmarks (`header`, `nav` con nombre, `main`, `footer`), enlace "Saltar al contenido", `label`
en todos los campos, `aria-describedby` y `aria-invalid` en errores, `caption` y `th scope` en todas las tablas, nombres
accesibles de los botones de cada fila (contienen el texto visible), `<dialog>` modal con `aria-labelledby`, pestañas
con `role="tablist"`/`tab`/`tabpanel`, gráficas con descripción y tabla equivalente. Axe no dejó ninguna comprobación
"por revisar" en contraste.

## Pantallas agregadas después de la medición (22 de noviembre)

Después de la medición se agregaron la búsqueda global (`/buscar`) y los botones de exportar en `/consultas` (PR #52). Con
axe-core 4.14.1 (reglas WCAG 2.0, 2.1 y 2.2 A y AA más buenas prácticas), con el administrador y a 1280 y 360 px, se revisó
`/buscar` con resultados, sin coincidencias y con un texto muy corto, y `/consultas`: **0 violaciones y 0 px de desbordamiento
horizontal** en las 8 combinaciones. **No se volvió a correr Lighthouse** en esas pantallas, así que su puntaje de
rendimiento no está medido.

## Identidad visual (22 de noviembre)

Los colores de la aplicación salen del logo (`frontend/src/styles/variables.css`): rojo `#c8102e` (el del logo, `#e01030`, se
oscureció un poco para que el texto blanco pase 4.5:1), grafito `#2b2e36` para los botones y blanco. Contrastes calculados con
la fórmula de WCAG: blanco sobre el rojo del encabezado 5.88:1, blanco sobre el grafito de los botones 13.58:1, enlaces
`#a50e26` sobre blanco 7.8:1 y sobre el fondo gris 7.11:1. Después del cambio, con axe-core 4.14.1 (mismas reglas que arriba) en
13 pantallas y a 1280 y 360 px: **0 violaciones y 0 px de desbordamiento horizontal** en las 26 combinaciones. Además se pasó el
cursor sobre 156 botones y pestañas: **0** con el texto por debajo de 3:1. Axe también reportó que había dos formularios
`role="search"` sin nombre en `/alumnos` y `/grupos/1` (`landmark-unique`); cada uno ya tiene su `aria-label`. El logo es el
icono de la pestaña (`favicon-32.png`, `favicon-192.png`, `apple-touch-icon.png`) y va en el encabezado con `alt=""`, porque el
nombre de la aplicación ya está escrito al lado. **No se volvió a correr Lighthouse** después de este cambio.

## Lo que no se pudo medir y límites

- **Lector de pantalla**: no se probó con NVDA, JAWS ni VoiceOver; la lectura real (por ejemplo cómo se anuncia el foco
  en `<main>` tras cambiar de pantalla, o las tablas apiladas en celular) debe revisarla una persona.
- **Tablas apiladas en celular** (`.tabla-apilable`, menos de 600 px): usan `display: block` y ocultan el
  `<thead>` con CSS. Axe no marca error, pero algunos navegadores con lector de pantalla pierden la semántica de tabla.
  Pendiente de revisar a mano.
- **Teclado**: se recorrió con Tab solo `/alumnos` y `/alumnos/nuevo` (30 y 29 elementos) para medir el foco; el orden
  y el uso completo (diálogos con Esc, pestañas con flechas) deben revisarse a mano en el resto.
- **Chrome**: solo se midió con Edge (mismo motor). Tampoco se midió en dispositivos reales ni con la red de
  Render/Neon/Vercel: todo fue en `localhost`, así que el rendimiento de producción puede ser distinto.
- **Solo con axe, no con Lighthouse**: `/alumnos/nuevo`, `/alumnos/:nocontrol`, `/alumnos/:nocontrol/editar`,
  `/grupos/nuevo`, `/grupos/1/editar` y `/404`.
- **Estados no cubiertos**: errores de la API (el estado "error" de cada pantalla), el aviso de lluvia del pronóstico
  (depende de Open-Meteo) y pantallas con muchos más datos que el seed.
- **Accesibilidad por debajo de 90**: ninguna pantalla quedó por debajo de 90; todas están en 100 con Lighthouse. Un 100
  de Lighthouse no garantiza que la app sea accesible: solo detecta una parte de los problemas.
