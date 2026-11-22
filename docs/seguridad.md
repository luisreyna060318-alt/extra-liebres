# Seguridad

Revisión de seguridad de Extra-Liebres con el **OWASP Top 10:2025**, que pide la materia: **A01** (control de acceso) y
**A02** (configuración incorrecta), y de paso **A03** (cadena de suministro), porque usamos un asistente de IA que podría
proponer dependencias inexistentes. Todo lo que dice este documento tiene una prueba o un comando que lo demuestra.

## A01 · Control de acceso

**Regla de oro:** la autorización se verifica **siempre en el servidor** (dependencias `get_current_user` y
`require_role` de FastAPI). Ocultar un botón en React no protege nada: aunque alguien conozca la ruta y la llame a mano,
el servidor responde `401` (sin sesión) o `403` (sin permiso) y no cambia ningún dato.

- El **rol y el estado de la cuenta se leen de la base de datos en cada petición**. Si el administrador cambia un rol o
  suspende una cuenta, el cambio se aplica en la siguiente acción de esa persona aunque conserve su token.
- Un usuario nuevo **siempre nace como capturista**. El campo `rol` que se mande al registrarse se ignora.
- No se puede quitar el rol ni suspender al **último administrador activo** (`409`).
- La **exportación** de inscritos (`/api/export/...`) es solo del administrador. En el CSV, un texto que empieza con `=`, `+`, `-` o `@`
  se escribe con una comilla al inicio para que la hoja de cálculo no lo ejecute como fórmula (`backend/tests/test_exportar.py`).
- El token JWT solo lleva el id y la expiración (`sub`, `exp`). Se rechazan tokens manipulados, vencidos, firmados con
  otra clave y con algoritmo `none`.

### Matriz de permisos de toda la API (43 rutas)

Públicas: **3** · Con sesión (ambos roles): **27** · Solo administrador: **13**

| Método | Ruta | Quién puede |
|---|---|---|
| GET | `/api/alumnos` | Administrador o capturista |
| POST | `/api/alumnos` | Administrador o capturista |
| GET | `/api/alumnos/opciones` | Administrador o capturista |
| DELETE | `/api/alumnos/{nocontrol}` | Administrador o capturista |
| GET | `/api/alumnos/{nocontrol}` | Administrador o capturista |
| PUT | `/api/alumnos/{nocontrol}` | Administrador o capturista |
| GET | `/api/alumnos/{nocontrol}/historial` | Administrador o capturista |
| POST | `/api/auth/login` | Público (no exige sesión) |
| GET | `/api/auth/me` | Administrador o capturista |
| POST | `/api/auth/register` | Público (no exige sesión) |
| GET | `/api/busqueda` | Administrador o capturista |
| GET | `/api/clima` | Administrador o capturista |
| GET | `/api/consultas/inscritos` | Administrador o capturista |
| GET | `/api/dashboard/resumen` | Administrador o capturista |
| GET | `/api/export/inscritos.csv` | Solo administrador |
| GET | `/api/export/inscritos.xml` | Solo administrador |
| GET | `/api/extraescolares` | Administrador o capturista |
| POST | `/api/extraescolares` | Solo administrador |
| DELETE | `/api/extraescolares/{idextraescolar}` | Solo administrador |
| GET | `/api/extraescolares/{idextraescolar}` | Administrador o capturista |
| PUT | `/api/extraescolares/{idextraescolar}` | Solo administrador |
| GET | `/api/grupos` | Administrador o capturista |
| POST | `/api/grupos` | Administrador o capturista |
| DELETE | `/api/grupos/{idgrupo}` | Administrador o capturista |
| GET | `/api/grupos/{idgrupo}` | Administrador o capturista |
| PUT | `/api/grupos/{idgrupo}` | Administrador o capturista |
| POST | `/api/grupos/{idgrupo}/inscripciones` | Administrador o capturista |
| DELETE | `/api/grupos/{idgrupo}/inscripciones/{nocontrol}` | Administrador o capturista |
| PUT | `/api/grupos/{idgrupo}/inscripciones/{nocontrol}` | Administrador o capturista |
| GET | `/api/grupos/{idgrupo}/inscritos` | Administrador o capturista |
| GET | `/api/health` | Público (no exige sesión) |
| GET | `/api/promotores` | Administrador o capturista |
| POST | `/api/promotores` | Solo administrador |
| DELETE | `/api/promotores/{rfc}` | Solo administrador |
| GET | `/api/promotores/{rfc}` | Administrador o capturista |
| PUT | `/api/promotores/{rfc}` | Solo administrador |
| GET | `/api/semestres` | Administrador o capturista |
| POST | `/api/semestres` | Solo administrador |
| DELETE | `/api/semestres/{idsemestre}` | Solo administrador |
| GET | `/api/semestres/{idsemestre}` | Administrador o capturista |
| PUT | `/api/semestres/{idsemestre}` | Solo administrador |
| GET | `/api/usuarios` | Solo administrador |
| PATCH | `/api/usuarios/{usuario_id}` | Solo administrador |

Esta tabla no se escribió a mano: sale de las mismas listas que usa la prueba automática
[`backend/tests/test_matriz_permisos.py`](../backend/tests/test_matriz_permisos.py), que **llama a cada ruta** sin sesión y
como capturista y comprueba lo que el servidor responde. Si alguien agrega una ruta nueva sin protegerla, esa prueba falla
y el CI se pone en rojo. Se verificó rompiendo la protección a propósito de tres maneras distintas (pruebas de mutación).

### Cómo demostrar el 403 en la demo

1. Abre `/docs` del backend, pulsa **Authorize** e inicia sesión con el **capturista** (`capturista@ejemplo.com`).
2. Prueba `GET /api/usuarios` o `POST /api/promotores`: el servidor responde **`403`** con
   `{"detail": "No tienes permiso para realizar esta acción"}`.
3. Cierra la sesión, inicia con el **administrador** y repite: ahora responde `200` o `201`.
4. Sin ninguna sesión, cualquier ruta privada responde **`401`**.

### Pruebas que respaldan A01
| Qué se comprueba | Dónde |
|---|---|
| Matriz de las 43 rutas (401 sin sesión, 403 al capturista) | `backend/tests/test_matriz_permisos.py` |
| Capturista no puede listar usuarios ni cambiar roles (403) y no cambia ningún dato | `backend/tests/test_usuarios.py` |
| El cambio de rol y la suspensión se aplican en la siguiente petición | `backend/tests/test_usuarios.py`, `test_auth.py` |
| No se puede dejar el sistema sin administradores | `backend/tests/test_usuarios.py` |
| Token manipulado, vencido, de otra clave o `alg: none` → 401 | `backend/tests/test_auth.py` |
| Los catálogos se leen con sesión pero solo el administrador escribe | `test_promotores.py`, `test_extraescolares.py`, `test_semestres.py` |

## A02 · Configuración incorrecta

| Riesgo | Cómo se evita | Dónde se comprueba |
|---|---|---|
| Secretos en el repositorio | `.env` en `.gitignore` y en `.dockerignore`; solo `.env.example` con valores de ejemplo | `git ls-files` no contiene `.env`; la imagen de Docker tampoco |
| Claves de ejemplo en producción | Con `ENTORNO=produccion` el backend **se niega a arrancar** si `SECRET_KEY` es corta o la de ejemplo, y el seed no crea usuarios con las claves de ejemplo | `backend/tests/test_config.py`; arranque real en Docker |
| Secretos en los logs | `hide_input_in_errors`: un error de configuración ya no imprime la clave ni la contraseña | `test_config.py` (se verificó que falla sin el arreglo) |
| CORS abierto | Lista explícita de orígenes (`CORS_ORIGINS`), nunca `*`; solo los métodos y encabezados necesarios | Prueba real: un origen ajeno no recibe `access-control-allow-origin` |
| Cabeceras HTTP de seguridad ausentes | El backend agrega `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control: no-store` en `/api` y HSTS en producción. El frontend (Vercel) agrega las mismas más `Permissions-Policy` y una **Content-Security-Policy estricta** (solo scripts, estilos e imágenes del propio sitio; solo se puede hablar con la API del proyecto; nadie puede incrustar el sitio) | `backend/tests/test_cabeceras.py` (9 pruebas, verificadas con una mutación). La CSP se probó en el navegador recorriendo las 8 pantallas y el tablero con gráficas: **0 violaciones** |
| Contraseñas débiles o guardadas en claro | Mínimo 8 caracteres con letras y números, máximo 72 bytes; hash **bcrypt** con sal | `test_security.py`, `test_auth.py` |
| Contenedor con demasiados privilegios | El proceso corre como usuario `app`, no `root` | `docker compose exec backend whoami` → `app` |
| Base de datos expuesta | PostgreSQL se publica solo en `127.0.0.1`, nunca en la red | `infra/docker-compose.yml` |
| Variables de más en un contenedor | PostgreSQL recibe solo sus 3 variables; no ve la `SECRET_KEY` | `infra/docker-compose.yml` |
| Errores que revelan si un correo existe | El login responde igual con correo inexistente o contraseña incorrecta, y tarda lo mismo | `test_auth.py` |

## A03 · Cadena de suministro

- Se evitaron a propósito `passlib` y `python-jose` (sin mantenimiento): se usan `bcrypt` y `PyJWT`.
- Las dependencias del backend están **fijadas a una versión** (`backend/requirements.txt`); las del frontend, en `package-lock.json`.
- `npm audit`: **0 vulnerabilidades**. Todas las descargas del `package-lock.json` apuntan al registro oficial de npm.
- Las dependencias se verificaron instalándolas desde cero en una copia limpia, no solo leyendo el archivo.

## Limitaciones conocidas y trabajo futuro

Cosas que decidimos no hacer en esta entrega y que un sistema real debería tener:

1. **Sin límite de intentos de inicio de sesión** (protección contra fuerza bruta).
2. **El token vive en `localStorage`** del navegador: es cómodo, pero se podría leer si hubiera una falla XSS. Una alternativa
   es una cookie `HttpOnly`. Mitigación actual: React escapa el contenido y no se usa `dangerouslySetInnerHTML`.
3. **No hay revocación de tokens en el servidor**: cerrar sesión borra el token del navegador, pero un token ya emitido
   sigue siendo válido hasta que expira (60 minutos). Se compensa leyendo el estado de la cuenta en cada petición, así que
   una cuenta suspendida deja de funcionar de inmediato.
4. **El login distingue una cuenta suspendida (403) de una contraseña incorrecta (401)**. Solo se llega al 403 con la contraseña
   correcta, así que no revela nada a un extraño; es una decisión consciente.
5. **`/docs` queda público**, también en producción: es útil para la demo y para el profesor; un sistema real lo cerraría.
6. **`SEED_ON_START=true` en producción** carga datos ficticios. Es explícito en `render.yaml`; hay que quitarlo si algún día
   hubiera datos reales.
7. **La CSP fija la URL de la API de producción** (`connect-src`): si la API cambia de dirección hay que editar
   `frontend/vercel.json`.
8. **El frontend de `docker compose` (nginx) no lleva estas cabeceras ni la CSP**: solo aplican en Vercel y en el backend.
9. **Datos personales:** los datos de ejemplo son ficticios (los números de control empiezan con `99`) y los registros reales
   de alumnos no se suben al repositorio ni a un asistente de IA (RN-07).
