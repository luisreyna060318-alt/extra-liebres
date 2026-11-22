"""Pruebas de la búsqueda global en alumnos y grupos (HU-06.2). Datos ficticios."""

from datetime import time

import pytest

from tests.conftest import encabezado_de

URL = "/api/busqueda"


@pytest.fixture()
def h(capturista):
    return encabezado_de(capturista)


@pytest.fixture()
def escenario(crear_alumno, crear_grupo):
    ana = crear_alumno("19110001", nombre="Ana", apaterno="López", amaterno="García")
    crear_alumno("19110002", nombre="Beto", apaterno="Aguilar", amaterno="Díaz")
    crear_alumno("19110003", nombre="Daniel", apaterno="Zamora", amaterno="Ruiz", activo=False)  # de baja
    crear_alumno("19110004", nombre="Daniela", apaterno="Ortiz", amaterno="Vega")
    futbol = crear_grupo(actividad="Fútbol", tipo="deportiva", aula="Cancha de fútbol")
    crear_grupo(actividad="Danza", tipo="cultural", aula="Salón de danza", inicio=time(10), fin=time(11), dia="martes")
    return {"ana": ana, "futbol": futbol}


def test_sin_sesion_401(client):
    assert client.get(URL, params={"q": "ana"}).status_code == 401


def test_q_muy_corta_o_ausente_422(client, h):
    assert client.get(URL, params={"q": "a"}, headers=h).status_code == 422
    assert client.get(URL, headers=h).status_code == 422


def test_agrupa_alumnos_y_grupos(client, h, escenario):
    # "dan" está en el nombre de Daniela y en "Danza": una coincidencia de cada tipo
    datos = client.get(URL, params={"q": "dan"}, headers=h).json()
    assert [a["nocontrol"] for a in datos["alumnos"]] == ["19110004"]  # Daniel, que está de baja, no aparece
    assert datos["alumnos"][0]["alumno"] == "Ortiz Vega Daniela"
    assert [g["descripcion"] for g in datos["grupos"]] == ["Danza (grupo 2), martes de 10:00 a 11:00"]
    assert datos["alumnos_hay_mas"] is False and datos["grupos_hay_mas"] is False


def test_busca_por_numero_de_control_y_por_actividad(client, h, escenario):
    alumnos = client.get(URL, params={"q": "19110002"}, headers=h).json()["alumnos"]
    assert [a["alumno"] for a in alumnos] == ["Aguilar Díaz Beto"]
    grupos = client.get(URL, params={"q": "fútbol"}, headers=h).json()["grupos"]
    assert [g["idgrupo"] for g in grupos] == [escenario["futbol"].idgrupo]


def test_busca_por_promotor_y_todas_las_palabras_deben_coincidir(client, h, escenario):
    # El promotor del escenario es Pedro Ruiz Soto
    assert len(client.get(URL, params={"q": "pedro"}, headers=h).json()["grupos"]) == 2
    assert len(client.get(URL, params={"q": "pedro danza"}, headers=h).json()["grupos"]) == 1
    assert client.get(URL, params={"q": "pedro tenis"}, headers=h).json()["grupos"] == []


def test_sin_coincidencias_listas_vacias(client, h, escenario):
    datos = client.get(URL, params={"q": "zzzz"}, headers=h).json()
    assert datos["alumnos"] == [] and datos["grupos"] == []


def test_comodines_se_buscan_tal_cual(client, h, escenario):
    # % y _ no son comodines: no deben traer a todo el mundo
    assert client.get(URL, params={"q": "%%"}, headers=h).json()["alumnos"] == []
    assert client.get(URL, params={"q": "__"}, headers=h).json()["grupos"] == []


def test_maximo_de_diez_por_tipo_y_avisa_si_hay_mas(client, h, crear_alumno):
    for n in range(12):
        crear_alumno(f"1912{n:04d}", nombre="Luis", apaterno=f"Apellido{n:02d}")
    datos = client.get(URL, params={"q": "luis"}, headers=h).json()
    assert len(datos["alumnos"]) == 10
    assert datos["alumnos_hay_mas"] is True
    assert datos["alumnos"][0]["alumno"].startswith("Apellido00")  # ordenados por apellidos
