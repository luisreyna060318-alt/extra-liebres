"""Pruebas de registro, inicio de sesión y sesión (HU-01.1, HU-01.2 y HU-01.3)."""

from datetime import timedelta

import pytest

from app.core.security import crear_token
from tests.conftest import PASSWORD_PRUEBA, encabezado_de

REGISTRO = {"nombre": "Ana López", "correo": "ana@correo.com", "password": "Clave1234"}


def iniciar_sesion(client, correo, password=PASSWORD_PRUEBA):
    return client.post("/api/auth/login", data={"username": correo, "password": password})


# ---------- HU-01.1 Crear una cuenta ----------


def test_hu_01_1_registro_crea_cuenta_capturista_sin_exponer_la_contrasena(client):
    r = client.post("/api/auth/register", json=REGISTRO)
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["rol"] == "capturista"
    assert cuerpo["correo"] == "ana@correo.com"
    assert "password" not in cuerpo and "password_hash" not in cuerpo


def test_hu_01_1_no_se_puede_pedir_rol_administrador_al_registrarse(client):
    r = client.post("/api/auth/register", json={**REGISTRO, "rol": "administrador"})
    assert r.status_code == 201
    assert r.json()["rol"] == "capturista"  # el campo "rol" se ignora: nadie se hace admin solo


def test_hu_01_1_correo_duplicado_da_409_aunque_cambien_las_mayusculas(client):
    assert client.post("/api/auth/register", json=REGISTRO).status_code == 201
    r = client.post("/api/auth/register", json={**REGISTRO, "correo": "ANA@Correo.com"})
    assert r.status_code == 409
    assert "registrado" in r.json()["detail"]


@pytest.mark.parametrize(
    "password",
    ["Corta1", "soloLetrasAqui", "123456789", "é" * 40 + "1"],  # corta, sin números, sin letras, >72 bytes
)
def test_hu_01_1_contrasena_invalida_da_422(client, password):
    r = client.post("/api/auth/register", json={**REGISTRO, "password": password})
    assert r.status_code == 422


def test_hu_01_1_correo_con_formato_invalido_da_422(client):
    assert client.post("/api/auth/register", json={**REGISTRO, "correo": "no-es-un-correo"}).status_code == 422


# ---------- HU-01.2 Iniciar sesión ----------


def test_hu_01_2_login_correcto_devuelve_token_y_me_muestra_mi_cuenta(client, capturista):
    r = iniciar_sesion(client, "capturista@correo.com")
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert r.json()["token_type"] == "bearer"

    yo = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert yo.status_code == 200
    assert yo.json()["correo"] == "capturista@correo.com"
    assert yo.json()["rol"] == "capturista"


def test_hu_01_2_login_acepta_el_correo_en_mayusculas(client, capturista):
    assert iniciar_sesion(client, "CAPTURISTA@correo.com").status_code == 200


def test_hu_01_2_el_mensaje_de_error_no_revela_si_fallo_el_correo_o_la_contrasena(client, capturista):
    contrasena_mala = iniciar_sesion(client, "capturista@correo.com", "otra-clave-1")
    correo_inexistente = iniciar_sesion(client, "nadie@correo.com")
    assert contrasena_mala.status_code == correo_inexistente.status_code == 401
    assert contrasena_mala.json() == correo_inexistente.json()


def test_hu_01_2_me_sin_token_da_401(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_hu_01_2_token_manipulado_da_401(client, capturista):
    token = crear_token(capturista.id)
    manipulado = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {manipulado}"})
    assert r.status_code == 401


def test_hu_01_2_token_vencido_da_401(client, capturista):
    vencido = crear_token(capturista.id, expira_en=timedelta(minutes=-1))
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {vencido}"})
    assert r.status_code == 401


def test_hu_01_2_token_firmado_con_otra_clave_da_401(client, capturista):
    import jwt

    falso = jwt.encode({"sub": str(capturista.id), "exp": 9999999999}, "otra-clave-de-32-caracteres-o-mas!!", "HS256")
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_hu_01_2_token_sin_algoritmo_none_da_401(client, capturista):
    import jwt

    sin_firma = jwt.encode({"sub": str(capturista.id), "exp": 9999999999}, key=None, algorithm="none")
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {sin_firma}"}).status_code == 401


# ---------- Cuentas suspendidas ----------


def test_hu_01_4_cuenta_suspendida_no_puede_iniciar_sesion(client, crear_usuario):
    crear_usuario("suspendido@correo.com", activo=False)
    r = iniciar_sesion(client, "suspendido@correo.com")
    assert r.status_code == 403
    assert "suspendida" in r.json()["detail"]


def test_hu_01_4_cuenta_suspendida_pierde_su_token_en_la_siguiente_peticion(client, db, capturista):
    encabezado = encabezado_de(capturista)
    assert client.get("/api/auth/me", headers=encabezado).status_code == 200
    capturista.activo = False
    db.commit()
    assert client.get("/api/auth/me", headers=encabezado).status_code == 401
