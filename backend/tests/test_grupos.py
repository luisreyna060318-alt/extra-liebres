"""Pruebas de grupos y de la validación de cruces de horario y lugar (HU-04.1, HU-04.3, HU-04.4, RN-03)."""

import pytest

from app.models import Alumno, AlumnoGrupo, Extraescolar, Promotor, Semestre
from tests.conftest import encabezado_de

URL = "/api/grupos"
RFC_PEDRO = "RUSP800101AA1"  # RFC ficticio
RFC_LAURA = "MELA850202BB2"  # RFC ficticio


@pytest.fixture()
def catalogos(db):
    """Un semestre, dos actividades y dos promotores (todo ficticio). Devuelve sus ids."""
    semestre = Semestre(anio=2026, mesinicio=1, mestermino=6)
    otro_semestre = Semestre(anio=2026, mesinicio=8, mestermino=12)
    futbol = Extraescolar(nombreextra="Fútbol", tipo="deportiva")
    danza = Extraescolar(nombreextra="Danza", tipo="cultural")
    db.add_all([
        semestre,
        otro_semestre,
        futbol,
        danza,
        Promotor(rfc=RFC_PEDRO, nombre="Pedro", apaterno="Ruiz", amaterno="Soto"),
        Promotor(rfc=RFC_LAURA, nombre="Laura", apaterno="Méndez", amaterno=None),
    ])
    db.commit()
    return {
        "semestre": semestre.idsemestre,
        "otro_semestre": otro_semestre.idsemestre,
        "futbol": futbol.idextraescolar,
        "danza": danza.idextraescolar,
    }


@pytest.fixture()
def h(capturista):
    """Encabezado con sesión de capturista (los grupos los administra cualquier rol con sesión)."""
    return encabezado_de(capturista)


def datos_grupo(catalogos, **cambios):
    """Datos válidos de un grupo; con **cambios se sobreescribe lo que cada prueba necesite."""
    datos = {
        "idsemestre": catalogos["semestre"],
        "idextraescolar": catalogos["futbol"],
        "rfcpromotor": RFC_PEDRO,
        "dia": "lunes",
        "horainicio": "08:00",
        "horatermino": "10:00",
        "aula": "Cancha de fútbol",
    }
    datos.update(cambios)
    return datos


def crear(client, h, catalogos, **cambios):
    return client.post(URL, json=datos_grupo(catalogos, **cambios), headers=h)


# ---------- Sesión ----------


def test_sin_sesion_401(client, catalogos):
    assert client.get(URL).status_code == 401
    assert client.post(URL, json=datos_grupo(catalogos)).status_code == 401


# ---------- HU-04.1 Crear un grupo validando cruces ----------


def test_crear_sin_conflicto_201_con_nombres(client, h, catalogos):
    r = crear(client, h, catalogos)
    assert r.status_code == 201
    grupo = r.json()
    # La respuesta trae los nombres, no solo los ids
    assert grupo["actividad"] == "Fútbol"
    assert grupo["promotor"] == "Pedro Ruiz Soto"
    assert grupo["semestre"] == "Enero-Junio 2026"
    assert grupo["horainicio"] == "08:00:00"
    assert grupo["inscritos"] == 0


def test_mismo_promotor_traslapado_409(client, h, catalogos):
    crear(client, h, catalogos)  # Pedro, lunes 08:00-10:00
    r = crear(client, h, catalogos, horainicio="09:00", horatermino="11:00", aula="Gimnasio",
              idextraescolar=catalogos["danza"])
    assert r.status_code == 409
    mensaje = r.json()["detail"]
    # El mensaje nombra al promotor y al grupo en conflicto
    assert "Pedro Ruiz Soto" in mensaje
    assert "Fútbol" in mensaje
    assert "08:00 a 10:00" in mensaje


def test_mismo_lugar_traslapado_409(client, h, catalogos):
    crear(client, h, catalogos)  # Cancha de fútbol, lunes 08:00-10:00
    r = crear(client, h, catalogos, rfcpromotor=RFC_LAURA, horainicio="09:30", horatermino="10:30")
    assert r.status_code == 409
    assert "Cancha de fútbol" in r.json()["detail"]


def test_mismo_lugar_sin_distinguir_mayusculas_409(client, h, catalogos):
    crear(client, h, catalogos)
    r = crear(client, h, catalogos, rfcpromotor=RFC_LAURA, aula="  cancha DE fútbol ")
    assert r.status_code == 409


def test_grupo_que_contiene_a_otro_409(client, h, catalogos):
    crear(client, h, catalogos, horainicio="09:00", horatermino="10:00")
    r = crear(client, h, catalogos, horainicio="08:00", horatermino="12:00", aula="Gimnasio")
    assert r.status_code == 409


def test_horarios_contiguos_permitidos_201(client, h, catalogos):
    # Mismo promotor y mismo lugar: 08:00-09:00 y 09:00-10:00 se tocan pero no se traslapan
    assert crear(client, h, catalogos, horainicio="08:00", horatermino="09:00").status_code == 201
    assert crear(client, h, catalogos, horainicio="09:00", horatermino="10:00").status_code == 201
    # Y también hacia atrás: 07:00-08:00
    assert crear(client, h, catalogos, horainicio="07:00", horatermino="08:00").status_code == 201


def test_mismo_horario_otro_dia_201(client, h, catalogos):
    crear(client, h, catalogos)
    assert crear(client, h, catalogos, dia="martes").status_code == 201


def test_mismo_horario_otro_semestre_201(client, h, catalogos):
    crear(client, h, catalogos)
    assert crear(client, h, catalogos, idsemestre=catalogos["otro_semestre"]).status_code == 201


def test_otro_promotor_y_otro_lugar_mismo_horario_201(client, h, catalogos):
    crear(client, h, catalogos)
    r = crear(client, h, catalogos, rfcpromotor=RFC_LAURA, aula="Aula 5", idextraescolar=catalogos["danza"])
    assert r.status_code == 201


@pytest.mark.parametrize("fin", ["08:00", "07:00"])
def test_fin_menor_o_igual_que_inicio_422(client, h, catalogos, fin):
    r = crear(client, h, catalogos, horainicio="08:00", horatermino=fin)
    assert r.status_code == 422
    assert "posterior" in r.text


def test_dia_invalido_422(client, h, catalogos):
    assert crear(client, h, catalogos, dia="domingo").status_code == 422


def test_promotor_inexistente_404(client, h, catalogos):
    assert crear(client, h, catalogos, rfcpromotor="XXXX000000XX0").status_code == 404


# ---------- HU-04.3 Listar y filtrar ----------


def test_listar_con_filtros_y_paginacion(client, h, catalogos):
    crear(client, h, catalogos, horainicio="08:00", horatermino="09:00")
    crear(client, h, catalogos, horainicio="09:00", horatermino="10:00", dia="martes")
    crear(client, h, catalogos, rfcpromotor=RFC_LAURA, aula="Aula 5", idextraescolar=catalogos["danza"])

    r = client.get(URL, params={"size": 2}, headers=h)
    assert r.status_code == 200
    assert r.json()["total"] == 3
    assert len(r.json()["items"]) == 2

    r = client.get(URL, params={"promotor": RFC_PEDRO, "dia": "lunes"}, headers=h)
    assert r.json()["total"] == 1

    r = client.get(URL, params={"extraescolar": catalogos["danza"], "semestre": catalogos["semestre"]}, headers=h)
    assert [g["promotor"] for g in r.json()["items"]] == ["Laura Méndez"]


def test_obtener_inexistente_404(client, h):
    assert client.get(f"{URL}/999", headers=h).status_code == 404


# ---------- HU-04.4 Editar y eliminar ----------


def test_editar_sin_cruzarse_consigo_mismo_200(client, h, catalogos):
    idgrupo = crear(client, h, catalogos).json()["idgrupo"]  # 08:00-10:00
    # Recorrer su propio horario media hora se traslapa con el horario viejo, pero es el mismo grupo
    r = client.put(f"{URL}/{idgrupo}", json=datos_grupo(catalogos, horainicio="08:30", horatermino="10:30"), headers=h)
    assert r.status_code == 200
    assert r.json()["horainicio"] == "08:30:00"


def test_editar_hacia_un_cruce_con_otro_409(client, h, catalogos):
    crear(client, h, catalogos)  # 08:00-10:00
    idgrupo = crear(client, h, catalogos, horainicio="10:00", horatermino="11:00").json()["idgrupo"]
    r = client.put(f"{URL}/{idgrupo}", json=datos_grupo(catalogos, horainicio="09:00", horatermino="11:00"), headers=h)
    assert r.status_code == 409


def test_borrar_sin_inscritos_204(client, h, catalogos):
    idgrupo = crear(client, h, catalogos).json()["idgrupo"]
    assert client.delete(f"{URL}/{idgrupo}", headers=h).status_code == 204
    assert client.get(f"{URL}/{idgrupo}", headers=h).status_code == 404


def test_borrar_con_inscritos_409(client, db, h, catalogos):
    idgrupo = crear(client, h, catalogos).json()["idgrupo"]
    db.add(Alumno(nocontrol="99000001", nombre="Ana", apaterno="López", amaterno=None, sexo="F",
                  carrera="Ingeniería Industrial", campus="Campus I"))
    db.add(AlumnoGrupo(nocontrol="99000001", idgrupo=idgrupo))
    db.commit()

    r = client.delete(f"{URL}/{idgrupo}", headers=h)
    assert r.status_code == 409
    assert "1 alumno(s) inscrito(s)" in r.json()["detail"]
    assert client.get(f"{URL}/{idgrupo}", headers=h).status_code == 200
