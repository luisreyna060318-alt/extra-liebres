"""Pronóstico del clima de Ciudad Juárez con Open-Meteo (API pública, sin llave) y wttr.in como respaldo.

Solo el backend llama a los servicios del clima (RN-10); el navegador nunca. El resultado correcto se guarda en
memoria 1 hora. Si algo falla, el sistema sigue funcionando: se prueba con el servicio de respaldo, después se usa la
última copia guardada (hasta 6 horas) y, si no hay ninguna, se devuelve "no disponible" y se registra.

Por qué hay un respaldo: en Render (plan gratis) la dirección de salida se comparte con muchos servicios y Open-Meteo
responde a veces "429 Too Many Requests" por el uso de los demás, sin que nosotros hayamos hecho nada mal.
"""

import logging
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

TIMEOUT_SEGUNDOS = 5
CACHE_SEGUNDOS = 3600  # 1 hora: mientras no pase, no se vuelve a consultar
COPIA_VIEJA_SEGUNDOS = 6 * 3600  # si los dos servicios fallan, se muestra la última copia si tiene menos de 6 horas
ESPERA_TRAS_FALLA_SEGUNDOS = 60  # tras una falla total no se insiste durante 1 minuto (cada intento tarda hasta 10 s)
NO_DISPONIBLE = {"disponible": False, "mensaje": "Pronóstico no disponible"}
LATITUD, LONGITUD, ZONA_HORARIA = 31.69, -106.42, "America/Ciudad_Juarez"

# Caché en memoria: el último resultado correcto, cuándo se guardó y cuándo fue la última falla total.
_cache: dict = {"guardado": 0.0, "datos": None, "ultima_falla": None}


def _resultado(temperatura, prob_lluvia) -> dict:
    """Arma la respuesta con el mismo formato sin importar de qué servicio salieron los datos."""
    if not isinstance(temperatura, int | float):
        raise ValueError("temperatura inválida")
    return {
        "disponible": True,
        "temperatura": temperatura,
        "prob_lluvia": prob_lluvia,
        "aviso_lluvia": prob_lluvia >= settings.clima_umbral_lluvia,
    }


def _consultar_open_meteo() -> dict:
    """Pide el pronóstico. Parámetros de https://open-meteo.com/en/docs (verificados con una petición real)."""
    parametros = {
        "latitude": LATITUD,
        "longitude": LONGITUD,
        "timezone": ZONA_HORARIA,
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
    return _resultado(temperatura, prob_lluvia)


def _ahora_local() -> datetime:
    """Hora de Ciudad Juárez sin zona horaria (para compararla con las horas que manda wttr.in)."""
    return datetime.now(ZoneInfo(ZONA_HORARIA)).replace(tzinfo=None)


def _consultar_respaldo() -> dict:
    """Respaldo: wttr.in (sin llave). Manda la lluvia en bloques de 3 horas, así que se toman los que caen en las
    próximas 12 horas."""
    url = f"{settings.clima_respaldo_url}/{LATITUD},{LONGITUD}"
    respuesta = httpx.get(url, params={"format": "j1"}, timeout=TIMEOUT_SEGUNDOS)
    respuesta.raise_for_status()
    datos = respuesta.json()
    temperatura = float(datos["current_condition"][0]["temp_C"])
    ahora = _ahora_local()
    probabilidades = []
    for dia in datos["weather"]:
        fecha = datetime.strptime(dia["date"], "%Y-%m-%d")
        for bloque in dia["hourly"]:
            inicio = fecha + timedelta(hours=int(bloque["time"]) // 100)  # "300" significa 03:00
            # El bloque dura 3 horas: cuenta si todavía no termina y empieza antes de que pasen 12 horas
            if inicio + timedelta(hours=3) > ahora and inicio <= ahora + timedelta(hours=12):
                probabilidades.append(int(bloque["chanceofrain"]))
    return _resultado(temperatura, max(probabilidades))  # max() de una lista vacía lanza ValueError


def _copia_guardada() -> dict:
    """La última copia correcta si tiene menos de 6 horas; si no, 'no disponible'."""
    if _cache["datos"] and time.monotonic() - _cache["guardado"] < COPIA_VIEJA_SEGUNDOS:
        return _cache["datos"]
    return dict(NO_DISPONIBLE)


def obtener_clima() -> dict:
    """Devuelve el clima (de la caché si tiene menos de 1 hora). Nunca lanza error."""
    ahora = time.monotonic()
    if _cache["datos"] and ahora - _cache["guardado"] < CACHE_SEGUNDOS:
        return _cache["datos"]
    ultima_falla = _cache["ultima_falla"]
    if ultima_falla is not None and ahora - ultima_falla < ESPERA_TRAS_FALLA_SEGUNDOS:
        return _copia_guardada()  # acaba de fallar todo: no se vuelve a intentar todavía

    datos = None
    for nombre, consultar in (("Open-Meteo", _consultar_open_meteo), ("wttr.in", _consultar_respaldo)):
        try:
            datos = consultar()
            break
        except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError):
            # HTTPError: red, timeout o status != 2xx (por ejemplo 429). ValueError: JSON inválido o sin datos.
            # KeyError/TypeError/IndexError: la respuesta no tiene la forma esperada.
            log.exception("No se pudo obtener el clima de %s", nombre)
    if datos is None:
        _cache["ultima_falla"] = ahora
        return _copia_guardada()
    _cache.update(guardado=ahora, datos=datos, ultima_falla=None)
    return datos
