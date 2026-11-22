"""Pronóstico del clima de Ciudad Juárez con Open-Meteo (API pública, sin llave).

Solo el backend llama a Open-Meteo (RN-10); el navegador nunca. El resultado correcto se guarda en
memoria 1 hora. Si algo falla, el sistema sigue funcionando: se devuelve "no disponible" y se registra.
"""

import logging
import time

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

TIMEOUT_SEGUNDOS = 5
CACHE_SEGUNDOS = 3600  # 1 hora
NO_DISPONIBLE = {"disponible": False, "mensaje": "Pronóstico no disponible"}

# Caché en memoria: el último resultado correcto y el momento en que se guardó.
_cache: dict = {"guardado": 0.0, "datos": None}


def _consultar_open_meteo() -> dict:
    """Pide el pronóstico. Parámetros de https://open-meteo.com/en/docs (verificados con una petición real)."""
    parametros = {
        "latitude": 31.69,
        "longitude": -106.42,
        "timezone": "America/Ciudad_Juarez",
        "current": "temperature_2m",  # temperatura actual (°C)
        "hourly": "precipitation_probability",  # probabilidad de lluvia por hora (%)
        "forecast_hours": 12,  # solo las próximas 12 horas
    }
    respuesta = httpx.get(settings.clima_url, params=parametros, timeout=TIMEOUT_SEGUNDOS)
    respuesta.raise_for_status()
    datos = respuesta.json()
    temperatura = datos["current"]["temperature_2m"]
    probabilidades = datos["hourly"]["precipitation_probability"]
    # Open-Meteo puede mandar null en alguna hora: esas se ignoran
    prob_lluvia = max(p for p in probabilidades if p is not None)
    if not isinstance(temperatura, int | float):
        raise ValueError("temperatura inválida")
    return {
        "disponible": True,
        "temperatura": temperatura,
        "prob_lluvia": prob_lluvia,
        "aviso_lluvia": prob_lluvia >= settings.clima_umbral_lluvia,
    }


def obtener_clima() -> dict:
    """Devuelve el clima (de la caché si tiene menos de 1 hora). Nunca lanza error."""
    if _cache["datos"] and time.monotonic() - _cache["guardado"] < CACHE_SEGUNDOS:
        return _cache["datos"]
    try:
        datos = _consultar_open_meteo()
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        # HTTPError: red, timeout o status != 2xx. ValueError: JSON inválido. KeyError/TypeError: forma inesperada.
        log.exception("No se pudo obtener el clima de Open-Meteo")
        return dict(NO_DISPONIBLE)  # las fallas no se guardan: el siguiente intento vuelve a consultar
    _cache["datos"] = datos
    _cache["guardado"] = time.monotonic()
    return datos
