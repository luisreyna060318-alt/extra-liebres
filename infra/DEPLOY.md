# Despliegue: Neon + Render + Vercel

Combinación gratuita y sin tarjeta que recomienda la materia. Cada pieza hace una sola cosa:

```
Navegador ──> Vercel (frontend React) ──> Render (backend FastAPI, en Docker) ──> Neon (PostgreSQL)
                                                   └──> Open-Meteo (clima; solo lo llama el backend)
```

Las cuentas las crea cada integrante (con su GitHub). **Ninguna clave se sube a Git**: se escriben solo en el
panel de cada servicio.

## 1. Neon (base de datos)

1. Crea un proyecto en <https://neon.tech> (elige una región; usa la misma o una cercana para Render).
2. En **Connect**, copia la cadena de conexión. Se ve así: `postgresql://usuario:clave@ep-xxxx.neon.tech/neondb?sslmode=require`
3. Guárdala: es el valor de `DATABASE_URL` del paso 2. **No la pegues en chats, issues ni commits.**

No hay que crear tablas a mano: el backend aplica las migraciones al arrancar.

## 2. Render (backend)

1. En <https://render.com>: **New + > Blueprint**, elige este repositorio. Render lee `render.yaml`.
2. Render pide los valores que no se pueden guardar en Git:

| Variable | Qué poner |
|---|---|
| `DATABASE_URL` | La cadena de Neon del paso 1 |
| `CORS_ORIGINS` | La URL del frontend en Vercel, sin diagonal final (si aún no la tienes, pon una provisional y corrígela en el paso 4) |
| `SEED_ADMIN_CORREO` / `SEED_ADMIN_PASSWORD` | Cuenta de administrador de la demo y **una clave tuya** (8 o más caracteres, con letras y números) |
| `SEED_CAPTURISTA_CORREO` / `SEED_CAPTURISTA_PASSWORD` | Cuenta de capturista de la demo |

   `SECRET_KEY` la genera Render sola. Con `ENTORNO=produccion`, el backend **se niega a arrancar** si la
   clave es corta o es la del ejemplo, y el seed se niega a crear usuarios con las claves de ejemplo.
3. Espera a que el servicio diga **Live**. Prueba `https://TU-SERVICIO.onrender.com/api/health` (debe responder
   `{"estado":"ok"}`) y `https://TU-SERVICIO.onrender.com/docs`.

## 3. Vercel (frontend)

1. En <https://vercel.com>: **Add New > Project**, elige este repositorio.
2. **Root Directory:** `frontend` (el repositorio es un monorepo; sin esto Vercel no encuentra `package.json`).
   Framework Preset: Vite (lo detecta solo; build `npm run build`, salida `dist`).
3. **Environment Variables:** `VITE_API_URL` = la URL de Render del paso 2 (sin diagonal final), por ejemplo
   `https://TU-SERVICIO.onrender.com`. Vite la escribe en el código al compilar: si la cambias después, haz
   **Redeploy** para que surta efecto.
4. **Deploy.** Las rutas de React Router (`/grupos`, `/alumnos/3`...) funcionan al recargar la página gracias a
   `frontend/vercel.json`, que ya está en el repositorio y reescribe todas las rutas a `/index.html`.
5. Copia la URL que te da Vercel (`https://TU-PROYECTO.vercel.app`, sin diagonal final): la necesitas en el paso 4.

## 4. Cerrar el círculo (CORS)

Vuelve a Render > **Environment** y pon en `CORS_ORIGINS` la URL final de Vercel (la del paso 3, sin diagonal
final; si usas también un dominio propio, sepáralos con comas). Render reinicia el servicio.
CORS es lo que hace que **solo tu frontend** pueda llamar a la API desde un navegador. Si al iniciar sesión el
navegador marca un error de CORS, casi siempre es que esta URL tiene una diagonal final o no coincide exactamente.

## 5. Comprobar

- [ ] `/api/health` y `/docs` del backend responden.
- [ ] Desde el frontend: iniciar sesión con el administrador y con el capturista.
- [ ] Como capturista, una acción de administrador (por ejemplo `GET /api/usuarios` en `/docs`) responde **403**.
- [ ] El clima aparece (o dice "Pronóstico no disponible" sin romper nada).

## El día de la demo

- **Render (plan gratuito) se duerme** tras 15 minutos sin tráfico y tarda 30 a 60 segundos en despertar.
  Abre el frontend y el `/api/health` unos **10 minutos antes** de tu turno.
- **Plan B obligatorio:** si la nube falla, el sistema se levanta en la laptop con un solo comando
  (`docker compose up --build`, ver el README; requiere Docker Compose 2.24 o más nuevo). Levanta base de datos,
  backend y frontend en <http://localhost:5173>. Pruébalo antes.
- Los límites de los planes gratuitos cambian: verifícalos en el sitio de cada proveedor antes de desplegar.

## Seguridad (para el reporte)

- Ningún secreto en el repositorio ni en la imagen de Docker (`.env` está en `.gitignore` y en `.dockerignore`).
- `SECRET_KEY` aleatoria generada por Render; en producción no se acepta la de ejemplo (OWASP A02).
- CORS limitado al dominio del frontend (OWASP A02) y autorización por rol verificada en el servidor (OWASP A01).
- El contenedor corre como un usuario sin privilegios, no como `root`.
- Los errores de configuración no imprimen la clave ni la contraseña en los logs.
