"""Pruebas de inscripción y evaluación (HU-05.1 a HU-05.3, RN-04, RN-05). Todos los datos son ficticios."""

import pytest

from app.models import AlumnoGrupo
from tests.conftest import encabezado_de


@pytest.fixture()
def h(capturista):
    return encabezado_de(capturista)


@pytest.fixture()
def grupo(crear_grupo):
    return crear_grupo()


@pytest.fixture()
def alumno(crear_alumno):
    return crear_alumno("19110001")


def url_inscripciones(grupo, nocontrol=None):
    base = f"/api/grupos/{grupo.idgrupo}/inscripciones"
    return f"{base}/{nocontrol}" if nocontrol else base


def evaluar(client, h, grupo, nocontrol, cuerpo):
    return client.put(url_inscripciones(grupo, nocontrol), json=cuerpo, headers=h)


# ---------- Sesión ----------


def test_sin_sesion_401(client, grupo, alumno):
    assert client.get(f"/api/grupos/{grupo.idgrupo}/inscritos").status_code == 401
    assert client.post(url_inscripciones(grupo), json={"nocontrol": "19110001"}).status_code == 401
    assert client.put(url_inscripciones(grupo, "19110001"), json={"calificacion": 90}).status_code == 401
    assert client.delete(url_inscripciones(grupo, "19110001")).status_code == 401


# ---------- HU-05.1 Inscribir ----------


def test_inscribir_201_sin_calificacion(client, h, grupo, alumno):
    r = client.post(url_inscripciones(grupo), json={"nocontrol": " 19110001 "}, headers=h)
    assert r.status_code == 201
    assert r.json() == {
        "nocontrol": "19110001",
        "alumno": "López García Ana",
        "carrera": "Ingeniería Industrial",
        "activo": True,
        "calificacion": None,
        "desempenio": None,
    }
    inscritos = client.get(f"/api/grupos/{grupo.idgrupo}/inscritos", headers=h).json()
    assert [i["nocontrol"] for i in inscritos] == ["19110001"]


def test_inscribir_duplicado_409(client, h, grupo, alumno):
    client.post(url_inscripciones(grupo), json={"nocontrol": "19110001"}, headers=h)
    r = client.post(url_inscripciones(grupo), json={"nocontrol": "19110001"}, headers=h)
    assert r.status_code == 409
    assert "ya está inscrito" in r.json()["detail"]


def test_inscribir_alumno_inactivo_409(client, h, grupo, crear_alumno):
    crear_alumno("19110002", activo=False)
    r = client.post(url_inscripciones(grupo), json={"nocontrol": "19110002"}, headers=h)
    assert r.status_code == 409
    assert "baja" in r.json()["detail"]


def test_inscribir_alumno_o_grupo_inexistente_404(client, h, grupo, alumno):
    assert client.post(url_inscripciones(grupo), json={"nocontrol": "99999999"}, headers=h).status_code == 404
    r = client.post("/api/grupos/999/inscripciones", json={"nocontrol": "19110001"}, headers=h)
    assert r.status_code == 404
    assert r.json()["detail"] == "El grupo no existe"
    assert client.get("/api/grupos/999/inscritos", headers=h).status_code == 404


# ---------- HU-05.2 Evaluar ----------


@pytest.mark.parametrize(
    ("calificacion", "esperado"),
    [
        (0, "Insuficiente"),
        (69, "Insuficiente"),
        (70, "Suficiente"),
        (74, "Suficiente"),
        (75, "Bueno"),
        (84, "Bueno"),
        (85, "Notable"),
        (94, "Notable"),
        (95, "Excelente"),
        (100, "Excelente"),
    ],
)
def test_evaluar_200_calcula_desempenio_en_los_bordes(client, h, grupo, alumno, inscribir, calificacion, esperado):
    inscribir(alumno, grupo)
    r = evaluar(client, h, grupo, "19110001", {"calificacion": calificacion})
    assert r.status_code == 200
    assert r.json()["calificacion"] == calificacion
    assert r.json()["desempenio"] == esperado


def test_corregir_calificacion_recalcula_desempenio(client, h, db, grupo, alumno, inscribir):
    inscribir(alumno, grupo)
    assert evaluar(client, h, grupo, "19110001", {"calificacion": 96}).json()["desempenio"] == "Excelente"
    r = evaluar(client, h, grupo, "19110001", {"calificacion": 72})
    assert r.json()["desempenio"] == "Suficiente"
    # Y quedó guardado así en la base de datos
    guardada = db.get(AlumnoGrupo, ("19110001", grupo.idgrupo))
    db.refresh(guardada)
    assert (guardada.calificacion, guardada.desempenio) == (72, "Suficiente")


@pytest.mark.parametrize("calificacion", [-1, 101, 94.5, "90", True, None])
def test_calificacion_invalida_422(client, h, grupo, alumno, inscribir, calificacion):
    inscribir(alumno, grupo)
    assert evaluar(client, h, grupo, "19110001", {"calificacion": calificacion}).status_code == 422


def test_cliente_no_puede_mandar_desempenio(client, h, db, grupo, alumno, inscribir):
    inscribir(alumno, grupo, calificacion=60, desempenio="Insuficiente")
    r = evaluar(client, h, grupo, "19110001", {"calificacion": 60, "desempenio": "Excelente"})
    assert r.status_code == 422
    # Nada cambió: el desempeño sigue siendo el que calculó el servidor
    guardada = db.get(AlumnoGrupo, ("19110001", grupo.idgrupo))
    db.refresh(guardada)
    assert guardada.desempenio == "Insuficiente"
    # Mandar solo el desempeño (sin calificación) tampoco sirve
    assert evaluar(client, h, grupo, "19110001", {"desempenio": "Excelente"}).status_code == 422


def test_evaluar_sin_inscripcion_404(client, h, grupo, alumno):
    r = evaluar(client, h, grupo, "19110001", {"calificacion": 90})
    assert r.status_code == 404
    assert "no está inscrito" in r.json()["detail"]
    assert client.put("/api/grupos/999/inscripciones/19110001", json={"calificacion": 90}, headers=h).status_code == 404


# ---------- HU-05.3 Quitar del grupo ----------


def test_quitar_sin_calificacion_204(client, h, db, grupo, alumno, inscribir):
    inscribir(alumno, grupo)
    assert client.delete(url_inscripciones(grupo, "19110001"), headers=h).status_code == 204
    assert db.get(AlumnoGrupo, ("19110001", grupo.idgrupo)) is None


def test_quitar_con_calificacion_pide_confirmacion(client, h, grupo, alumno, inscribir):
    inscribir(alumno, grupo, calificacion=90, desempenio="Notable")
    assert client.delete(url_inscripciones(grupo, "19110001"), headers=h).status_code == 409
    r = client.delete(url_inscripciones(grupo, "19110001"), params={"confirmar": True}, headers=h)
    assert r.status_code == 204


def test_quitar_inscripcion_inexistente_404(client, h, grupo, alumno):
    assert client.delete(url_inscripciones(grupo, "19110001"), headers=h).status_code == 404
