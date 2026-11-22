"""Cabeceras de seguridad HTTP (OWASP A02: configuración incorrecta)."""

import pytest

from app.core.config import settings
from tests.conftest import encabezado_de

CABECERAS_SIEMPRE = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "no-referrer",
}


@pytest.mark.parametrize("ruta", ["/api/health", "/docs", "/openapi.json", "/ruta-que-no-existe"])
def test_todas_las_respuestas_llevan_las_cabeceras_de_seguridad(client, ruta):
    respuesta = client.get(ruta)
    for cabecera, valor in CABECERAS_SIEMPRE.items():
        assert respuesta.headers.get(cabecera) == valor, f"{ruta}: falta {cabecera}"


def test_las_respuestas_de_error_tambien_llevan_las_cabeceras(client):
    sin_sesion = client.get("/api/alumnos")  # 401
    assert sin_sesion.status_code == 401
    assert sin_sesion.headers["x-content-type-options"] == "nosniff"
    invalido = client.post("/api/auth/register", json={})  # 422
    assert invalido.status_code == 422
    assert invalido.headers["x-frame-options"] == "DENY"


def test_los_datos_de_la_api_no_se_guardan_en_cache(client, capturista):
    respuesta = client.get("/api/alumnos", headers=encabezado_de(capturista))
    assert respuesta.status_code == 200
    assert respuesta.headers["cache-control"] == "no-store"


def test_la_documentacion_si_puede_guardarse_en_cache(client):
    # Solo /api lleva no-store: la documentación (/docs) es contenido público
    assert "no-store" not in client.get("/docs").headers.get("cache-control", "")


def test_hsts_solo_en_produccion(client, monkeypatch):
    assert "strict-transport-security" not in client.get("/api/health").headers  # desarrollo
    monkeypatch.setattr(settings, "entorno", "produccion")
    hsts = client.get("/api/health").headers.get("strict-transport-security", "")
    assert "max-age=" in hsts and "includeSubDomains" in hsts


def test_cors_sigue_funcionando_con_las_cabeceras(client):
    # Las cabeceras nuevas no deben romper el permiso del frontend (regresión)
    permitido = client.options(
        "/api/alumnos", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"}
    )
    assert permitido.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert permitido.headers.get("x-content-type-options") == "nosniff"
    ajeno = client.options(
        "/api/alumnos", headers={"Origin": "http://sitio-malo.com", "Access-Control-Request-Method": "GET"}
    )
    assert "access-control-allow-origin" not in ajeno.headers
