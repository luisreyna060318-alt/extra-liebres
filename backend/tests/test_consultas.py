"""Pruebas de la consulta de inscritos por actividad y semestre (HU-06.1). Datos ficticios."""

from datetime import time

import pytest

from tests.conftest import encabezado_de

URL = "/api/consultas/inscritos"


@pytest.fixture()
def h(capturista):
    return encabezado_de(capturista)


@pytest.fixture()
def escenario(crear_grupo, crear_alumno, inscribir):
    """Fútbol y Danza en enero-junio 2026, y Fútbol en agosto-diciembre 2026, con alumnos inscritos."""
    futbol_ene = crear_grupo(actividad="Fútbol", tipo="deportiva")
    danza_ene = crear_grupo(actividad="Danza", tipo="cultural", aula="Salón de danza", inicio=time(10), fin=time(11))
    futbol_ago = crear_grupo(mesinicio=8, mestermino=12, actividad="Fútbol")
    ana = crear_alumno("19110001", nombre="Ana", apaterno="López")
    beto = crear_alumno("19110002", nombre="Beto", apaterno="Aguilar", sexo="M")
    inscribir(ana, futbol_ene, calificacion=96, desempenio="Excelente")
    inscribir(beto, futbol_ene)  # sin evaluar
    inscribir(ana, danza_ene, calificacion=72, desempenio="Suficiente")
    inscribir(beto, futbol_ago, calificacion=80, desempenio="Bueno")
    return {
        "futbol": futbol_ene.idextraescolar,
        "danza": danza_ene.idextraescolar,
        "ene": futbol_ene.idsemestre,
        "ago": futbol_ago.idsemestre,
    }


def test_sin_sesion_401(client):
    assert client.get(URL).status_code == 401


def test_sin_filtros_devuelve_todo_ordenado(client, h, escenario):
    r = client.get(URL, headers=h)
    assert r.status_code == 200
    datos = r.json()
    assert datos["total"] == 4
    # Primero el semestre más reciente (agosto); luego Danza y Fútbol de enero, por apellidos
    assert [(i["actividad"], i["semestre"], i["nocontrol"]) for i in datos["items"]] == [
        ("Fútbol", "Agosto-Diciembre 2026", "19110002"),
        ("Danza", "Enero-Junio 2026", "19110001"),
        ("Fútbol", "Enero-Junio 2026", "19110002"),
        ("Fútbol", "Enero-Junio 2026", "19110001"),
    ]


def test_renglon_trae_alumno_grupo_calificacion_y_desempenio(client, h, escenario):
    fila = client.get(URL, params={"extraescolar": escenario["danza"]}, headers=h).json()["items"][0]
    assert fila["alumno"] == "López García Ana"
    assert fila["actividad"] == "Danza"
    assert fila["promotor"] == "Pedro Ruiz Soto"
    assert (fila["calificacion"], fila["desempenio"]) == (72, "Suficiente")
    assert "password_hash" not in fila


def test_filtro_por_actividad(client, h, escenario):
    datos = client.get(URL, params={"extraescolar": escenario["futbol"]}, headers=h).json()
    assert datos["total"] == 3
    assert {i["actividad"] for i in datos["items"]} == {"Fútbol"}


def test_filtro_por_semestre(client, h, escenario):
    datos = client.get(URL, params={"semestre": escenario["ago"]}, headers=h).json()
    assert datos["total"] == 1
    assert datos["items"][0]["desempenio"] == "Bueno"


def test_filtros_combinados(client, h, escenario):
    params = {"extraescolar": escenario["futbol"], "semestre": escenario["ene"]}
    datos = client.get(URL, params=params, headers=h).json()
    assert datos["total"] == 2
    # Beto sin evaluar aparece con calificación y desempeño nulos
    beto = next(i for i in datos["items"] if i["nocontrol"] == "19110002")
    assert (beto["calificacion"], beto["desempenio"]) == (None, None)


def test_sin_resultados_lista_vacia(client, h, escenario):
    datos = client.get(URL, params={"extraescolar": escenario["danza"], "semestre": escenario["ago"]}, headers=h).json()
    assert datos == {"items": [], "total": 0, "page": 1, "size": 10}


def test_paginacion(client, h, escenario):
    p1 = client.get(URL, params={"size": 3}, headers=h).json()
    p2 = client.get(URL, params={"size": 3, "page": 2}, headers=h).json()
    assert (len(p1["items"]), p1["total"], p1["page"]) == (3, 4, 1)
    assert (len(p2["items"]), p2["total"], p2["page"]) == (1, 4, 2)
    assert client.get(URL, params={"size": 51}, headers=h).status_code == 422
