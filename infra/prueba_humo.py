"""Prueba de humo de Extra-Liebres: recorre los flujos principales del sistema desplegado y dice qué funciona.

Uso (no hay que instalar nada, solo Python 3):
    python infra/prueba_humo.py https://extra-liebres.onrender.com
    python infra/prueba_humo.py http://localhost:8000          (contra tu computadora)

Pide el correo y la contraseña del administrador y del capturista. La contraseña se escribe sin que se vea y
NUNCA se imprime ni se guarda. También se pueden pasar por variables de entorno (para automatizar):
    HUMO_ADMIN_CORREO, HUMO_ADMIN_PASSWORD, HUMO_CAPTURISTA_CORREO, HUMO_CAPTURISTA_PASSWORD

Todo lo que la prueba crea (promotor, actividad, semestre, grupos, una inscripción) se borra al final,
aunque algo falle.
El sistema queda igual que estaba. Aun así escribe datos de prueba en la base real durante un momento: córrelo
antes de la demo y no mientras otras personas usan el sistema.
Solo acepta https:// (o http:// de tu propia computadora): con http:// las contraseñas viajarían sin cifrar.
Conviene correrla unos 10 minutos antes de una demostración: además despierta el servidor gratuito de Render.
"""

import getpass
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 120  # Render gratuito tarda de 30 a 60 s en despertar
resultados: list[bool] = []
temporales: list[tuple[str, str]] = []  # (descripción, ruta) de lo creado, para limpiarlo al final
inscripciones_temporales: list[str] = []  # inscripciones creadas: hay que quitarlas antes de borrar los grupos


def ok(nombre: str, condicion: bool, detalle: str = "") -> bool:
    resultados.append(bool(condicion))
    print(("OK    " if condicion else "FALLA ") + nombre + (f"  -> {detalle}" if detalle != "" else ""))
    return bool(condicion)


def llamar(base: str, metodo: str, ruta: str, token: str | None = None, cuerpo=None, formulario=None):
    """Hace una petición y devuelve (código HTTP, cuerpo ya convertido de JSON si se pudo)."""
    cabeceras = {"Accept": "application/json"}
    datos = None
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    if formulario is not None:
        datos = urllib.parse.urlencode(formulario).encode()
        cabeceras["Content-Type"] = "application/x-www-form-urlencoded"
    elif cuerpo is not None:
        datos = json.dumps(cuerpo).encode()
        cabeceras["Content-Type"] = "application/json"
    peticion = urllib.request.Request(base + ruta, data=datos, headers=cabeceras, method=metodo)
    try:
        with urllib.request.urlopen(peticion, timeout=TIMEOUT) as r:
            codigo, bruto = r.status, r.read()
    except urllib.error.HTTPError as e:
        codigo, bruto = e.code, e.read()
    try:
        return codigo, json.loads(bruto) if bruto else None
    except ValueError:
        return codigo, bruto.decode("utf-8", "replace")


def credencial(variable: str, pregunta: str, secreta: bool = False) -> str:
    valor = os.environ.get(variable)
    if valor:
        return valor
    return getpass.getpass(pregunta) if secreta else input(pregunta).strip()


def iniciar_sesion(base: str, correo: str, password: str) -> str | None:
    codigo, cuerpo = llamar(base, "POST", "/api/auth/login", formulario={"username": correo, "password": password})
    return cuerpo["access_token"] if codigo == 200 and isinstance(cuerpo, dict) else None


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    base = sys.argv[1].rstrip("/")
    esquema, _, resto = base.partition("://")
    servidor = resto.split("/")[0].split(":")[0]
    if esquema == "http" and servidor not in ("localhost", "127.0.0.1", "::1"):
        # Con http:// las contraseñas viajarían sin cifrar por internet
        print(f"Por seguridad no se aceptan direcciones http:// que no sean de tu computadora ({base}). Usa https://.")
        return 2
    if "//localhost" in base:
        # En Windows "localhost" resuelve primero a IPv6 y cada petición tarda ~8 s; 127.0.0.1 es inmediato
        base = base.replace("//localhost", "//127.0.0.1")
    print(f"Probando {base}\n(si es la primera vez en un rato, Render puede tardar hasta 1 minuto en despertar)\n")

    # ---------- 1. Servicio vivo ----------
    t0 = time.perf_counter()
    codigo, cuerpo = llamar(base, "GET", "/api/health")
    if not ok(
        "el servicio responde", codigo == 200 and cuerpo == {"estado": "ok"}, f"{time.perf_counter() - t0:.1f} s"
    ):
        print("\nSin servicio no se puede seguir.")
        return 1
    ok("/docs (documentación de la API) abre", llamar(base, "GET", "/docs")[0] == 200)

    # ---------- 2. Credenciales e inicio de sesión ----------
    print("\nEscribe las credenciales (la contraseña no se ve y no se guarda):")
    correo_admin = credencial("HUMO_ADMIN_CORREO", "  Correo del administrador: ")
    clave_admin = credencial("HUMO_ADMIN_PASSWORD", "  Contraseña del administrador: ", secreta=True)
    correo_cap = credencial("HUMO_CAPTURISTA_CORREO", "  Correo del capturista: ")
    clave_cap = credencial("HUMO_CAPTURISTA_PASSWORD", "  Contraseña del capturista: ", secreta=True)
    print()
    admin = iniciar_sesion(base, correo_admin, clave_admin)
    capturista = iniciar_sesion(base, correo_cap, clave_cap)
    ok("el administrador inicia sesión", admin is not None)
    ok("el capturista inicia sesión", capturista is not None)
    if not (admin and capturista):
        print("\nSin las dos sesiones no se puede seguir (revisa correos y contraseñas).")
        return 1
    ok(
        "/me del administrador dice 'administrador'",
        llamar(base, "GET", "/api/auth/me", admin)[1].get("rol") == "administrador",
    )
    ok(
        "/me del capturista dice 'capturista'",
        llamar(base, "GET", "/api/auth/me", capturista)[1].get("rol") == "capturista",
    )

    # ---------- 3. Permisos ----------
    print()
    ok("sin sesión, /api/alumnos da 401", llamar(base, "GET", "/api/alumnos")[0] == 401)
    ok("el capturista NO puede ver usuarios (403)", llamar(base, "GET", "/api/usuarios", capturista)[0] == 403)
    ok(
        "el capturista NO puede crear un promotor (403)",
        llamar(base, "POST", "/api/promotores", capturista, {"rfc": "AAAA000101AAA", "nombre": "X", "apaterno": "Y"})[0]
        == 403,
    )
    ok("el administrador sí ve los usuarios (200)", llamar(base, "GET", "/api/usuarios", admin)[0] == 200)

    # ---------- 4. Lecturas con los datos reales ----------
    print()
    codigo, alumnos = llamar(base, "GET", "/api/alumnos?size=50", capturista)
    ok("lista de alumnos", codigo == 200 and alumnos["total"] > 0, f"{alumnos['total']} alumnos activos")
    primero = alumnos["items"][0]
    codigo, busqueda = llamar(base, "GET", "/api/alumnos?q=" + primero["nocontrol"], capturista)
    ok("buscar un alumno por su número de control", codigo == 200 and busqueda["total"] == 1)
    codigo, historial = llamar(base, "GET", f"/api/alumnos/{primero['nocontrol']}/historial", capturista)
    ok("historial de un alumno", codigo == 200 and isinstance(historial, list), f"{len(historial)} actividades")
    totales = {}
    for nombre, ruta in (
        ("promotores", "/api/promotores"),
        ("actividades", "/api/extraescolares"),
        ("semestres", "/api/semestres"),
    ):
        codigo, lista = llamar(
            base, "GET", ruta + "?estado=todos&size=50" if nombre != "semestres" else ruta + "?size=50", capturista
        )
        totales[nombre] = lista["total"] if codigo == 200 else -1
    ok("catálogos (promotores, actividades, semestres)", all(v > 0 for v in totales.values()), str(totales))
    codigo, grupos = llamar(base, "GET", "/api/grupos", capturista)
    ok("lista de grupos", codigo == 200 and grupos["total"] > 0, f"{grupos['total']} grupos")
    codigo, tablero = llamar(base, "GET", "/api/dashboard/resumen", capturista)
    ok(
        "tablero de resumen",
        codigo == 200 and tablero["totales"]["grupos"] > 0,
        str(tablero["totales"]) if codigo == 200 else codigo,
    )
    codigo, clima = llamar(base, "GET", "/api/clima", capturista)
    ok("clima (o 'Pronóstico no disponible' sin romper nada)", codigo == 200 and "disponible" in clima, str(clima))

    # ---------- 5. Flujo de escritura completo, con limpieza ----------
    print("\nFlujo de escritura (todo se borra al final):")
    sufijo = str(int(time.time()))[-6:]
    antes = dict(totales)
    try:
        c, promotor = llamar(
            base, "POST", "/api/promotores", admin, {"rfc": f"HUMO{sufijo}AB1", "nombre": "Prueba", "apaterno": "Humo"}
        )
        ok("el administrador crea un promotor", c == 201)
        if c == 201:
            temporales.append(("promotor", f"/api/promotores/{promotor['rfc']}"))
        c, r = llamar(
            base,
            "PUT",
            f"/api/promotores/{promotor['rfc']}",
            admin,
            {"nombre": "Prueba", "apaterno": "Humo", "activo": False},
        )
        ok("lo desactiva", c == 200 and r["activo"] is False)
        c, r = llamar(
            base,
            "PUT",
            f"/api/promotores/{promotor['rfc']}",
            admin,
            {"nombre": "Prueba", "apaterno": "Humo", "activo": True},
        )
        ok("lo reactiva", c == 200 and r["activo"] is True)
        c, actividad = llamar(
            base,
            "POST",
            "/api/extraescolares",
            admin,
            {"nombreextra": f"Humo {sufijo}", "tipo": "cultural", "al_aire_libre": False},
        )
        ok("crea una actividad", c == 201)
        if c == 201:
            temporales.append(("actividad", f"/api/extraescolares/{actividad['idextraescolar']}"))
        # El servidor solo acepta años de 2000 a 2027 y dos periodos (enero-junio y agosto-diciembre), así que se
        # busca, del año más alto hacia atrás, el primer semestre que todavía no exista (409 = ya existe)
        semestre = None
        for anio in range(2027, 1999, -1):
            for mesinicio, mestermino in ((8, 12), (1, 6)):
                datos = {"anio": anio, "mesinicio": mesinicio, "mestermino": mestermino}
                c, semestre = llamar(base, "POST", "/api/semestres", admin, datos)
                if c != 409:
                    break
            if c != 409:
                break
        ok("crea un semestre de prueba (el más alto libre, hasta 2027)", c == 201, f"{anio}, mes {mesinicio}")
        if c == 201:
            temporales.append(("semestre", f"/api/semestres/{semestre['idsemestre']}"))

        def grupo(inicio: str, fin: str):
            return llamar(
                base,
                "POST",
                "/api/grupos",
                capturista,
                {
                    "idsemestre": semestre["idsemestre"],
                    "idextraescolar": actividad["idextraescolar"],
                    "rfcpromotor": promotor["rfc"],
                    "dia": "sabado",
                    "horainicio": inicio,
                    "horatermino": fin,
                    "aula": "Aula Humo",
                },
            )

        c, ga = grupo("05:00", "06:00")
        ok("el capturista crea un grupo", c == 201)
        if c == 201:
            temporales.insert(0, ("grupo", f"/api/grupos/{ga['idgrupo']}"))
        c, r = grupo("05:30", "06:30")
        ok(
            "un grupo que se traslapa se rechaza (409)",
            c == 409,
            (r or {}).get("detail", "")[:70] if isinstance(r, dict) else "",
        )
        c, gc = grupo("06:00", "07:00")
        ok("un grupo contiguo (06:00 a 07:00) sí se permite", c == 201)
        if c == 201:
            temporales.insert(0, ("grupo", f"/api/grupos/{gc['idgrupo']}"))

        ins = f"/api/grupos/{ga['idgrupo']}/inscripciones"
        c, r = llamar(base, "POST", ins, capturista, {"nocontrol": primero["nocontrol"]})
        ok("inscribe a un alumno existente", c == 201)
        if c == 201:
            # Se anota ya, para que la limpieza la quite aunque el script falle más adelante
            inscripciones_temporales.append(f"{ins}/{primero['nocontrol']}")
        ok(
            "inscribirlo otra vez se rechaza (409)",
            llamar(base, "POST", ins, capturista, {"nocontrol": primero["nocontrol"]})[0] == 409,
        )
        ruta_ev = f"{ins}/{primero['nocontrol']}"
        c, r = llamar(base, "PUT", ruta_ev, capturista, {"calificacion": 85})
        ok(
            "evaluarlo con 85 da 'Notable' (lo calcula el servidor)",
            c == 200 and r["desempenio"] == "Notable",
            str(r.get("desempenio")) if isinstance(r, dict) else "",
        )
        ok(
            "mandar el desempeño a mano se rechaza (422)",
            llamar(base, "PUT", ruta_ev, capturista, {"calificacion": 85, "desempenio": "Excelente"})[0] == 422,
        )
        ok(
            "una calificación de 101 se rechaza (422)",
            llamar(base, "PUT", ruta_ev, capturista, {"calificacion": 101})[0] == 422,
        )
        c, r = llamar(base, "GET", f"/api/consultas/inscritos?semestre={semestre['idsemestre']}", capturista)
        ok("la consulta de inscritos lo encuentra", c == 200 and r["total"] == 1)
        c, r = llamar(base, "GET", f"/api/dashboard/resumen?semestre={semestre['idsemestre']}", capturista)
        ok(
            "el tablero cuenta 2 grupos y 1 inscripción",
            c == 200 and r["totales"]["grupos"] == 2 and r["totales"]["inscripciones"] == 1,
            str(r["totales"]) if c == 200 else c,
        )
        ok(
            "eliminar un grupo con inscritos se rechaza (409)",
            llamar(base, "DELETE", f"/api/grupos/{ga['idgrupo']}", capturista)[0] == 409,
        )
        ok(
            "quitar a un alumno con calificación pide confirmación (409)",
            llamar(base, "DELETE", ruta_ev, capturista)[0] == 409,
        )
        ok("con confirmación se quita (204)", llamar(base, "DELETE", ruta_ev + "?confirmar=true", capturista)[0] == 204)
    except Exception as error:  # noqa: BLE001  (cualquier fallo inesperado se reporta y se limpia igual)
        ok("el flujo de escritura terminó sin errores inesperados", False, f"{type(error).__name__}: {error}")
    finally:
        # ---------- Limpieza: se borra en orden (grupos primero, luego promotor, actividad y semestre) ----------
        print("\nLimpieza:")
        # Primero las inscripciones: un grupo con inscritos no se puede borrar (409) y, sin borrar los grupos,
        # tampoco el promotor, la actividad ni el semestre. Si ya se quitó antes, el 404 se ignora.
        for ruta in inscripciones_temporales:
            codigo, _ = llamar(base, "DELETE", ruta + "?confirmar=true", admin)
            if codigo == 204:
                ok("se quita la inscripción de prueba que quedó pendiente", True)
            elif codigo != 404:
                ok("se quita la inscripción de prueba", False, f"código {codigo}")
        orden = {"grupo": 0, "promotor": 1, "actividad": 2, "semestre": 3}
        for descripcion, ruta in sorted(temporales, key=lambda t: orden[t[0]]):
            codigo, _ = llamar(base, "DELETE", ruta, admin)
            ok(f"se borra el/la {descripcion} de prueba", codigo == 204, "" if codigo == 204 else f"código {codigo}")
        despues = {}
        for nombre, ruta in (
            ("promotores", "/api/promotores"),
            ("actividades", "/api/extraescolares"),
            ("semestres", "/api/semestres"),
        ):
            codigo, lista = llamar(
                base, "GET", ruta + "?estado=todos&size=50" if nombre != "semestres" else ruta + "?size=50", admin
            )
            despues[nombre] = lista["total"] if codigo == 200 else -1
        ok("el sistema quedó igual que al empezar", despues == antes, f"antes {antes} / después {despues}")

    correctas = sum(resultados)
    print(
        f"\n{correctas} de {len(resultados)} comprobaciones correctas"
        + ("  :)" if correctas == len(resultados) else "  <- REVISA LAS QUE DICEN FALLA")
    )
    return 0 if correctas == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
