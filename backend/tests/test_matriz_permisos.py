"""Matriz de permisos de TODA la API (OWASP A01: control de acceso).

En lugar de probar rutas una por una, esta prueba recorre todas las rutas que publica /openapi.json y comprueba lo
que el servidor responde de verdad:
  - sin sesión   -> 401 (salvo las 3 rutas públicas de abajo),
  - como capturista -> 403 solo en las rutas de administrador,
  - como lector     -> 403 en las rutas de administrador y en las de personal (datos de alumnos y escrituras).

Si alguien agrega una ruta nueva y olvida protegerla, esta prueba falla: aparecerá como "pública" y no está en la lista.
"""

import re

import pytest

from tests.conftest import encabezado_de

# Las únicas rutas que no exigen sesión: ver si el servicio vive, crear una cuenta e iniciar sesión
PUBLICAS = {
    ("get", "/api/health"),
    ("post", "/api/auth/register"),
    ("post", "/api/auth/login"),
}

# Rutas que solo puede usar el administrador (catálogos: escribir; usuarios: todo; exportar)
SOLO_ADMIN = {
    ("get", "/api/usuarios"),
    ("patch", "/api/usuarios/{usuario_id}"),
    ("post", "/api/promotores"),
    ("put", "/api/promotores/{rfc}"),
    ("delete", "/api/promotores/{rfc}"),
    ("post", "/api/extraescolares"),
    ("put", "/api/extraescolares/{idextraescolar}"),
    ("delete", "/api/extraescolares/{idextraescolar}"),
    ("post", "/api/semestres"),
    ("put", "/api/semestres/{idsemestre}"),
    ("delete", "/api/semestres/{idsemestre}"),
    ("get", "/api/export/inscritos.csv"),
    ("get", "/api/export/inscritos.xml"),
}


# Rutas que solo usan el administrador y el capturista (el lector recibe 403): todo lo de alumnos, la búsqueda, las
# consultas, las inscripciones y crear, editar o eliminar grupos. Al lector solo le quedan el tablero, el clima, su
# propia cuenta y las listas de grupos y catálogos.
SOLO_PERSONAL = {
    ("get", "/api/alumnos"),
    ("post", "/api/alumnos"),
    ("get", "/api/alumnos/opciones"),
    ("get", "/api/alumnos/{nocontrol}"),
    ("put", "/api/alumnos/{nocontrol}"),
    ("delete", "/api/alumnos/{nocontrol}"),
    ("get", "/api/alumnos/{nocontrol}/historial"),
    ("get", "/api/busqueda"),
    ("get", "/api/consultas/inscritos"),
    ("post", "/api/grupos"),
    ("put", "/api/grupos/{idgrupo}"),
    ("delete", "/api/grupos/{idgrupo}"),
    ("post", "/api/grupos/{idgrupo}/inscripciones"),
    ("put", "/api/grupos/{idgrupo}/inscripciones/{nocontrol}"),
    ("delete", "/api/grupos/{idgrupo}/inscripciones/{nocontrol}"),
    ("get", "/api/grupos/{idgrupo}/inscritos"),
}


def rutas_de_la_api(client):
    """Todas las (método, ruta) que documenta /openapi.json."""
    rutas = client.get("/openapi.json").json()["paths"]
    return [(metodo, ruta) for ruta, operaciones in rutas.items() for metodo in operaciones]


def llamar(client, metodo, ruta, **extra):
    url = re.sub(r"\{[^}]+\}", "1", ruta)  # los parámetros de ruta se reemplazan por un valor cualquiera
    cuerpo = {"json": {}} if metodo in ("post", "put", "patch") else {}
    return client.request(metodo.upper(), url, **cuerpo, **extra).status_code


def test_hay_las_rutas_esperadas(client):
    # Si cambia el tamaño de la API a propósito, actualiza este número: es un recordatorio de revisar la matriz
    assert len(rutas_de_la_api(client)) == 43


def test_solo_las_rutas_publicas_responden_sin_sesion(client):
    abiertas = {(m, r) for m, r in rutas_de_la_api(client) if llamar(client, m, r) != 401}
    assert abiertas == PUBLICAS, f"rutas sin protección que no están en la lista de públicas: {abiertas - PUBLICAS}"


def test_solo_el_administrador_puede_usar_las_rutas_de_administrador(client, capturista):
    h = encabezado_de(capturista)
    prohibidas = {(m, r) for m, r in rutas_de_la_api(client) if llamar(client, m, r, headers=h) == 403}
    assert prohibidas == SOLO_ADMIN, (
        f"rutas de administrador sin proteger: {SOLO_ADMIN - prohibidas}; "
        f"rutas que bloquean a los capturistas sin estar en la lista: {prohibidas - SOLO_ADMIN}"
    )


def test_el_lector_solo_pasa_en_el_tablero_las_listas_y_su_cuenta(client, lector):
    h = encabezado_de(lector)
    prohibidas = {(m, r) for m, r in rutas_de_la_api(client) if llamar(client, m, r, headers=h) == 403}
    esperadas = SOLO_ADMIN | SOLO_PERSONAL
    assert prohibidas == esperadas, (
        f"rutas que el lector todavía puede usar: {esperadas - prohibidas}; "
        f"rutas que bloquean al lector sin estar en las listas: {prohibidas - esperadas}"
    )


@pytest.mark.parametrize(("metodo", "ruta"), sorted(SOLO_PERSONAL))
def test_el_capturista_si_pasa_las_rutas_de_personal(client, capturista, metodo, ruta):
    # El capturista no recibe 401 ni 403 (puede recibir 404 o 422 porque se mandan datos vacíos)
    assert llamar(client, metodo, ruta, headers=encabezado_de(capturista)) not in (401, 403)


@pytest.mark.parametrize(("metodo", "ruta"), sorted(SOLO_ADMIN))
def test_el_administrador_si_pasa_las_rutas_de_administrador(client, admin, metodo, ruta):
    # El administrador no recibe 401 ni 403 (puede recibir 404 o 422 porque se mandan datos vacíos)
    assert llamar(client, metodo, ruta, headers=encabezado_de(admin)) not in (401, 403)
