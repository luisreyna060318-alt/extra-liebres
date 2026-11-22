"""P9 (lado servidor): el lugar del grupo según el tipo de actividad (HU-04.2). Datos ficticios."""

import pytest

from app.core.constantes import INSTALACIONES
from app.models import Extraescolar, Promotor, Semestre
from tests.conftest import encabezado_de

URL = "/api/grupos"
RFC = "RUSP800101AA1"  # RFC ficticio


@pytest.fixture()
def h(capturista):
    return encabezado_de(capturista)


@pytest.fixture()
def ids(db):
    semestre = Semestre(anio=2026, mesinicio=1, mestermino=6)
    actividades = {
        "deportiva": Extraescolar(nombreextra="Fútbol", tipo="deportiva"),
        "cultural": Extraescolar(nombreextra="Ajedrez", tipo="cultural"),
        "civica": Extraescolar(nombreextra="Escolta", tipo="civica"),
    }
    db.add_all([semestre, *actividades.values(), Promotor(rfc=RFC, nombre="Pedro", apaterno="Ruiz")])
    db.commit()
    return {"semestre": semestre.idsemestre, **{t: a.idextraescolar for t, a in actividades.items()}}


def crear(client, h, ids, tipo, aula):
    datos = {
        "idsemestre": ids["semestre"],
        "idextraescolar": ids[tipo],
        "rfcpromotor": RFC,
        "dia": "lunes",
        "horainicio": "08:00",
        "horatermino": "09:00",
        "aula": aula,
    }
    return client.post(URL, json=datos, headers=h)


@pytest.mark.parametrize("aula", ["Aula 5", "Salón de danza", "Cancha"])
def test_deportiva_con_lugar_invalido_422(client, h, ids, aula):
    r = crear(client, h, ids, "deportiva", aula)
    assert r.status_code == 422
    mensaje = r.json()["detail"]
    assert aula in mensaje
    assert "Gimnasio" in mensaje  # el mensaje dice qué lugares sí se permiten


@pytest.mark.parametrize("aula", INSTALACIONES)
def test_deportiva_con_lugar_valido_201(client, h, ids, aula):
    r = crear(client, h, ids, "deportiva", aula)
    assert r.status_code == 201
    assert r.json()["aula"] == aula


def test_deportiva_acepta_mayusculas_y_guarda_nombre_oficial(client, h, ids):
    r = crear(client, h, ids, "deportiva", "  gimnasio ")
    assert r.status_code == 201
    assert r.json()["aula"] == "Gimnasio"


@pytest.mark.parametrize("tipo", ["cultural", "civica"])
def test_cultural_o_civica_con_lugar_libre_201(client, h, ids, tipo):
    r = crear(client, h, ids, tipo, "Salón 12 del edificio B")
    assert r.status_code == 201
    assert r.json()["aula"] == "Salón 12 del edificio B"


def test_editar_a_deportiva_con_aula_invalida_422(client, h, ids):
    # Un grupo cultural en "Aula 5" no puede cambiarse a una actividad deportiva sin cambiar el lugar
    grupo = crear(client, h, ids, "cultural", "Aula 5").json()
    datos = {
        "idsemestre": ids["semestre"],
        "idextraescolar": ids["deportiva"],
        "rfcpromotor": RFC,
        "dia": "lunes",
        "horainicio": "08:00",
        "horatermino": "09:00",
        "aula": "Aula 5",
    }
    r = client.put(f"{URL}/{grupo['idgrupo']}", json=datos, headers=h)
    assert r.status_code == 422
    assert client.get(f"{URL}/{grupo['idgrupo']}", headers=h).json()["idextraescolar"] == ids["cultural"]
