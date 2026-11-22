"""Pruebas del clima. NUNCA usan internet: httpx.get se reemplaza con una respuesta falsa."""

import httpx
import pytest

from app.services import clima
from tests.conftest import encabezado_de

# Misma forma que la respuesta real de Open-Meteo (recortada a lo que usamos)
RESPUESTA_OK = {
    "current": {"time": "2026-11-21T18:30", "temperature_2m": 14.7},
    "hourly": {
        "time": [f"2026-11-21T{h:02d}:00" for h in range(12)],
        "precipitation_probability": [0, 0, 10, 30, 20, 0, 0, 0, 5, 0, 0, 0],
    },
}


class RespuestaFalsa:
    def __init__(self, datos=None, error_json=False, status=200):
        self._datos, self._error_json, self.status_code = datos, error_json, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=httpx.Request("GET", "http://x"), response=self)

    def json(self):
        if self._error_json:
            raise ValueError("JSON inválido")
        return self._datos


@pytest.fixture(autouse=True)
def cache_limpia():
    """Cada prueba empieza con la caché vacía."""
    clima._cache.update(guardado=0.0, datos=None)


@pytest.fixture()
def falso_httpx(monkeypatch):
    """Reemplaza httpx.get; devuelve la lista de llamadas hechas. Se configura con falso_httpx.respuesta."""

    class Falso:
        llamadas: list = []
        respuesta = RespuestaFalsa(RESPUESTA_OK)

    def get(url, params=None, timeout=None):
        Falso.llamadas.append({"url": url, "params": params, "timeout": timeout})
        if isinstance(Falso.respuesta, Exception):
            raise Falso.respuesta
        return Falso.respuesta

    Falso.llamadas = []
    monkeypatch.setattr(clima.httpx, "get", get)
    return Falso


def test_respuesta_correcta(falso_httpx):
    resultado = clima.obtener_clima()
    assert resultado == {"disponible": True, "temperatura": 14.7, "prob_lluvia": 30, "aviso_lluvia": False}
    # Parámetros que pide la doc de Open-Meteo y timeout de 5 s
    llamada = falso_httpx.llamadas[0]
    assert llamada["timeout"] == 5
    assert llamada["params"]["current"] == "temperature_2m"
    assert llamada["params"]["hourly"] == "precipitation_probability"
    assert llamada["params"]["forecast_hours"] == 12
    assert llamada["params"]["timezone"] == "America/Ciudad_Juarez"


def test_aviso_de_lluvia_con_el_umbral(falso_httpx):
    falso_httpx.respuesta = RespuestaFalsa(
        {**RESPUESTA_OK, "hourly": {"precipitation_probability": [0, 50, None, 20]}}
    )
    resultado = clima.obtener_clima()
    assert resultado["prob_lluvia"] == 50
    assert resultado["aviso_lluvia"] is True


def test_timeout(falso_httpx, caplog):
    falso_httpx.respuesta = httpx.ReadTimeout("tardó demasiado")
    assert clima.obtener_clima() == {"disponible": False, "mensaje": "Pronóstico no disponible"}
    assert "Open-Meteo" in caplog.text  # quedó registrado en el log


def test_json_invalido(falso_httpx):
    falso_httpx.respuesta = RespuestaFalsa(error_json=True)
    assert clima.obtener_clima() == {"disponible": False, "mensaje": "Pronóstico no disponible"}


def test_respuesta_con_forma_inesperada(falso_httpx):
    falso_httpx.respuesta = RespuestaFalsa({"otra_cosa": 1})
    assert clima.obtener_clima()["disponible"] is False


def test_error_http_del_servicio(falso_httpx):
    falso_httpx.respuesta = RespuestaFalsa(status=500)
    assert clima.obtener_clima()["disponible"] is False


def test_segunda_llamada_usa_la_cache(falso_httpx):
    primera = clima.obtener_clima()
    segunda = clima.obtener_clima()
    assert primera == segunda
    assert len(falso_httpx.llamadas) == 1  # la segunda no salió a internet


def test_cache_vencida_vuelve_a_consultar(falso_httpx):
    clima.obtener_clima()
    clima._cache["guardado"] -= clima.CACHE_SEGUNDOS + 1  # simula que pasó más de 1 hora
    clima.obtener_clima()
    assert len(falso_httpx.llamadas) == 2


def test_una_falla_no_se_guarda_en_cache(falso_httpx):
    falso_httpx.respuesta = httpx.ConnectError("sin red")
    assert clima.obtener_clima()["disponible"] is False
    falso_httpx.respuesta = RespuestaFalsa(RESPUESTA_OK)
    assert clima.obtener_clima()["disponible"] is True  # se recuperó en el siguiente intento


def test_endpoint_sin_sesion_da_401(client):
    assert client.get("/api/clima").status_code == 401


def test_endpoint_con_sesion(client, capturista, falso_httpx):
    r = client.get("/api/clima", headers=encabezado_de(capturista))
    assert r.status_code == 200
    assert r.json() == {"disponible": True, "temperatura": 14.7, "prob_lluvia": 30, "aviso_lluvia": False}


def test_endpoint_con_falla_responde_200(client, capturista, falso_httpx):
    falso_httpx.respuesta = httpx.ReadTimeout("tardó demasiado")
    r = client.get("/api/clima", headers=encabezado_de(capturista))
    assert r.status_code == 200
    assert r.json() == {"disponible": False, "mensaje": "Pronóstico no disponible"}
