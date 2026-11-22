"""Rol lector: las cuentas nuevas solo ven el tablero y las listas, y no pueden cambiar ni leer datos de alumnos."""

import pytest

from tests.conftest import encabezado_de

REGISTRO = {"nombre": "Ana López", "correo": "ana@correo.com", "password": "Clave1234"}


def test_una_cuenta_recien_registrada_entra_como_lector_y_no_puede_ver_alumnos(client):
    client.post("/api/auth/register", json=REGISTRO)
    login = client.post("/api/auth/login", data={"username": REGISTRO["correo"], "password": REGISTRO["password"]})
    h = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/auth/me", headers=h).json()["rol"] == "lector"
    assert client.get("/api/alumnos", headers=h).status_code == 403


def test_el_lector_ve_el_tablero_los_grupos_y_los_catalogos(client, lector):
    h = encabezado_de(lector)
    urls = ("/api/dashboard/resumen", "/api/clima", "/api/grupos", "/api/extraescolares", "/api/promotores",
            "/api/semestres")
    for url in urls:
        assert client.get(url, headers=h).status_code == 200, url


def test_el_lector_no_puede_crear_editar_ni_eliminar_grupos_y_no_cambia_nada(client, db, lector, crear_grupo):
    from app.models import Grupo

    grupo = crear_grupo()
    h = encabezado_de(lector)
    assert client.post("/api/grupos", json={}, headers=h).status_code == 403
    assert client.put(f"/api/grupos/{grupo.idgrupo}", json={}, headers=h).status_code == 403
    assert client.delete(f"/api/grupos/{grupo.idgrupo}", headers=h).status_code == 403
    assert db.get(Grupo, grupo.idgrupo) is not None  # el grupo sigue existiendo


URLS_DE_ALUMNOS = ["/api/alumnos", "/api/busqueda?q=ana", "/api/consultas/inscritos", "/api/grupos/1/inscritos"]


@pytest.mark.parametrize("url", URLS_DE_ALUMNOS)
def test_el_lector_no_ve_datos_de_alumnos(client, lector, url):
    assert client.get(url, headers=encabezado_de(lector)).status_code == 403


def test_el_lector_no_puede_borrar_alumnos_y_no_se_borra_nada(client, db, lector, crear_alumno):
    from app.models import Alumno

    crear_alumno("19110001")
    assert client.delete("/api/alumnos/19110001", headers=encabezado_de(lector)).status_code == 403
    assert db.get(Alumno, "19110001") is not None


def test_un_administrador_puede_subir_a_un_lector_a_capturista(client, admin, lector):
    r = client.patch(f"/api/usuarios/{lector.id}", json={"rol": "capturista"}, headers=encabezado_de(admin))
    assert r.status_code == 200 and r.json()["rol"] == "capturista"
    # El cambio se aplica en la siguiente petición, con el mismo token
    assert client.get("/api/alumnos", headers=encabezado_de(lector)).status_code == 200


def test_un_lector_no_puede_subirse_el_rol_a_si_mismo(client, db, lector):
    r = client.patch(f"/api/usuarios/{lector.id}", json={"rol": "administrador"}, headers=encabezado_de(lector))
    assert r.status_code == 403
    db.refresh(lector)
    assert lector.rol == "lector"


def test_el_filtro_de_usuarios_acepta_el_rol_lector(client, admin, lector):
    r = client.get("/api/usuarios?rol=lector", headers=encabezado_de(admin))
    assert r.status_code == 200
    assert [u["correo"] for u in r.json()["items"]] == ["lector@correo.com"]
