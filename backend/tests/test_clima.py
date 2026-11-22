"""Pruebas del clima. NUNCA usan internet: httpx.get se reemplaza con una respuesta falsa."""

from datetime import datetime

import httpx
import pytest

from app.core.config import settings
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

# Misma forma que la respuesta de wttr.in (el respaldo): temperatura actual y lluvia en bloques de 3 horas
# (la hora "300" significa 03:00)
def _bloques(chances):
    horas = range(0, 24, 3)
    return [{"time": str(hora * 100), "chanceofrain": str(c)} for hora, c in zip(horas, chances, strict=True)]


RESPUESTA_WTTR = {
    "current_condition": [{"temp_C": "15"}],
    "weather": [
        {"date": "2026-11-21", "hourly": _bloques([90, 90, 90, 90, 90, 90, 20, 10])},
        {"date": "2026-11-22", "hourly": _bloques([5, 40, 15, 99, 99, 99, 99, 99])},
    ],
}
# A las 18:30 del 21 de noviembre cuentan los bloques de las 18, 21, 00, 03 y 06 h (el de las 15 ya terminó y el de las
# 09 h empieza después de 12 horas): el máximo es 40
AHORA = datetime(2026, 11, 21, 18, 30)


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
    clima._cache.update(guardado=0.0, datos=None, ultima_falla=None)


@pytest.fixture(autouse=True)
def hora_fija(monkeypatch):
    """La hora local se fija para que el respaldo (wttr.in) dé siempre el mismo resultado."""
    monkeypatch.setattr(clima, "_ahora_local", lambda: AHORA)


@pytest.fixture()
def falso_httpx(monkeypatch):
    """Reemplaza httpx.get; devuelve la lista de llamadas hechas. Se configura con falso_httpx.respuesta (Open-Meteo)
    y falso_httpx.respaldo (wttr.in, que por defecto también falla)."""

    class Falso:
        llamadas: list = []
        respuesta = RespuestaFalsa(RESPUESTA_OK)
        respaldo = httpx.ConnectError("sin respaldo")

    def get(url, params=None, timeout=None):
        Falso.llamadas.append({"url": url, "params": params, "timeout": timeout})
        elegida = Falso.respuesta if url == settings.clima_url else Falso.respaldo
        if isinstance(elegida, Exception):
            raise elegida
        return elegida

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


def test_una_falla_total_no_se_guarda_como_dato_y_se_reintenta_despues_de_la_espera(falso_httpx):
    falso_httpx.respuesta = httpx.ConnectError("sin red")
    assert clima.obtener_clima()["disponible"] is False
    assert clima._cache["datos"] is None  # la falla no se guardó como si fuera un pronóstico
    falso_httpx.respuesta = RespuestaFalsa(RESPUESTA_OK)
    clima._cache["ultima_falla"] -= clima.ESPERA_TRAS_FALLA_SEGUNDOS + 1  # simula que pasó la espera
    assert clima.obtener_clima()["disponible"] is True  # se recuperó en el siguiente intento


# ---------- Respaldo (wttr.in), espera tras fallar y copia vieja ----------


def test_si_open_meteo_responde_429_se_usa_el_respaldo(falso_httpx, caplog):
    falso_httpx.respuesta = RespuestaFalsa(status=429)
    falso_httpx.respaldo = RespuestaFalsa(RESPUESTA_WTTR)
    resultado = clima.obtener_clima()
    assert resultado == {"disponible": True, "temperatura": 15.0, "prob_lluvia": 40, "aviso_lluvia": False}
    urls = [llamada["url"] for llamada in falso_httpx.llamadas]
    assert urls == [settings.clima_url, f"{settings.clima_respaldo_url}/31.69,-106.42"]
    assert falso_httpx.llamadas[1]["params"] == {"format": "j1"}
    assert "Open-Meteo" in caplog.text  # quedó registrado por qué se usó el respaldo


def test_el_resultado_del_respaldo_tambien_se_guarda_en_cache(falso_httpx):
    falso_httpx.respuesta = RespuestaFalsa(status=429)
    falso_httpx.respaldo = RespuestaFalsa(RESPUESTA_WTTR)
    clima.obtener_clima()
    clima.obtener_clima()
    assert len(falso_httpx.llamadas) == 2  # la segunda vez no salió a internet


def test_el_respaldo_avisa_de_lluvia_con_el_umbral(falso_httpx):
    wttr = {**RESPUESTA_WTTR, "weather": [{"date": "2026-11-21", "hourly": _bloques([0, 0, 0, 0, 0, 0, 60, 0])}]}
    falso_httpx.respuesta = RespuestaFalsa(status=429)
    falso_httpx.respaldo = RespuestaFalsa(wttr)
    resultado = clima.obtener_clima()
    assert resultado["prob_lluvia"] == 60 and resultado["aviso_lluvia"] is True


@pytest.mark.parametrize(
    "respaldo",
    [RespuestaFalsa({"otra_cosa": 1}), RespuestaFalsa(error_json=True), RespuestaFalsa(status=503)],
)
def test_si_el_respaldo_tambien_falla_no_hay_pronostico(falso_httpx, respaldo):
    falso_httpx.respuesta = RespuestaFalsa(status=429)
    falso_httpx.respaldo = respaldo
    assert clima.obtener_clima() == {"disponible": False, "mensaje": "Pronóstico no disponible"}


def test_el_respaldo_sin_bloques_dentro_de_las_12_horas_no_inventa_datos(falso_httpx, monkeypatch):
    monkeypatch.setattr(clima, "_ahora_local", lambda: datetime(2027, 1, 1))  # el pronóstico es de noviembre
    falso_httpx.respuesta = RespuestaFalsa(status=429)
    falso_httpx.respaldo = RespuestaFalsa(RESPUESTA_WTTR)
    assert clima.obtener_clima()["disponible"] is False


def test_tras_una_falla_total_no_se_insiste_durante_un_minuto(falso_httpx):
    falso_httpx.respuesta = httpx.ConnectError("sin red")
    clima.obtener_clima()
    llamadas_del_primer_intento = len(falso_httpx.llamadas)  # Open-Meteo y el respaldo
    clima.obtener_clima()
    clima.obtener_clima()
    assert len(falso_httpx.llamadas) == llamadas_del_primer_intento


def test_si_todo_falla_se_muestra_la_ultima_copia_de_menos_de_6_horas(falso_httpx):
    buena = clima.obtener_clima()
    clima._cache["guardado"] -= clima.CACHE_SEGUNDOS + 1  # la copia ya está vieja, hay que volver a consultar
    falso_httpx.respuesta = httpx.ConnectError("sin red")
    assert clima.obtener_clima() == buena  # se muestra la copia vieja en lugar de "no disponible"


def test_una_copia_de_mas_de_6_horas_ya_no_se_muestra(falso_httpx):
    clima.obtener_clima()
    clima._cache["guardado"] -= clima.COPIA_VIEJA_SEGUNDOS + 1
    falso_httpx.respuesta = httpx.ConnectError("sin red")
    assert clima.obtener_clima()["disponible"] is False


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
