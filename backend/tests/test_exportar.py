"""Pruebas de la exportación de inscritos a CSV y XML (HU-07.2). Datos ficticios."""

import csv
import io
import xml.etree.ElementTree as ET
from datetime import time

import pytest

from tests.conftest import encabezado_de

CSV = "/api/export/inscritos.csv"
XML = "/api/export/inscritos.xml"


@pytest.fixture()
def h(admin):
    return encabezado_de(admin)


@pytest.fixture()
def escenario(crear_grupo, crear_alumno, inscribir):
    futbol_ene = crear_grupo(actividad="Fútbol", tipo="deportiva")
    danza_ene = crear_grupo(actividad="Danza", tipo="cultural", aula="Salón de danza", inicio=time(10), fin=time(11))
    futbol_ago = crear_grupo(mesinicio=8, mestermino=12, actividad="Fútbol")
    ana = crear_alumno("19110001", nombre="Ana", apaterno="López")
    beto = crear_alumno("19110002", nombre="Beto", apaterno="Aguilar", sexo="M")
    inscribir(ana, futbol_ene, calificacion=96, desempenio="Excelente")
    inscribir(beto, futbol_ene)  # sin evaluar
    inscribir(ana, danza_ene, calificacion=72, desempenio="Suficiente")
    inscribir(beto, futbol_ago, calificacion=80, desempenio="Bueno")
    return {"danza": danza_ene.idextraescolar, "ene": futbol_ene.idsemestre}


def filas_csv(respuesta):
    return list(csv.reader(io.StringIO(respuesta.content.decode("utf-8-sig"))))


@pytest.mark.parametrize("url", [CSV, XML])
def test_sin_sesion_401_y_capturista_403(client, capturista, url):
    assert client.get(url).status_code == 401
    assert client.get(url, headers=encabezado_de(capturista)).status_code == 403


def test_csv_trae_encabezados_y_todos_los_renglones(client, h, escenario):
    r = client.get(CSV, headers=h)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert 'filename="inscritos.csv"' in r.headers["content-disposition"]
    assert r.content.startswith(b"\xef\xbb\xbf")  # BOM: Excel respeta los acentos
    filas = filas_csv(r)
    assert filas[0] == ["No. de control", "Alumno", "Carrera", "Actividad", "Semestre", "Grupo", "Promotor",
                        "Calificación", "Desempeño"]
    assert len(filas) == 1 + 4  # encabezado y los 4 inscritos, sin paginar
    assert filas[1][:5] == [
        "19110002", "Aguilar García Beto", "Ingeniería Industrial", "Fútbol", "Agosto-Diciembre 2026"
    ]


def test_csv_respeta_los_filtros_y_deja_vacia_la_calificacion_sin_evaluar(client, h, escenario):
    filas = filas_csv(client.get(CSV, params={"semestre": escenario["ene"]}, headers=h))
    assert len(filas) == 1 + 3
    sin_evaluar = [f for f in filas[1:] if f[0] == "19110002"][0]
    assert sin_evaluar[7] == "" and sin_evaluar[8] == ""
    assert len(filas_csv(client.get(CSV, params={"extraescolar": escenario["danza"]}, headers=h))) == 1 + 1


def test_csv_sin_resultados_solo_trae_el_encabezado(client, h):
    assert len(filas_csv(client.get(CSV, headers=h))) == 1


def test_csv_no_deja_que_un_nombre_se_ejecute_como_formula(client, h, crear_alumno, crear_grupo, inscribir):
    # El alumno se muestra como "apellidos nombre": un apellido que empieza con "=" se escribiría como fórmula
    inscribir(crear_alumno("19110009", nombre="Ana", apaterno="=CMD"), crear_grupo())
    assert filas_csv(client.get(CSV, headers=h))[1][1] == "'=CMD García Ana"


def test_xml_esta_bien_formado_y_tiene_la_estructura_documentada(client, h, escenario):
    r = client.get(XML, headers=h)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert 'filename="inscritos.xml"' in r.headers["content-disposition"]
    raiz = ET.fromstring(r.content)  # si no estuviera bien formado, aquí truena
    assert raiz.tag == "inscritos" and raiz.get("total") == "4"
    inscritos = raiz.findall("inscrito")
    assert len(inscritos) == 4
    assert [c.tag for c in inscritos[0]] == ["nocontrol", "alumno", "carrera", "actividad", "semestre", "idgrupo",
                                             "promotor", "calificacion", "desempenio"]
    assert inscritos[0].findtext("nocontrol") == "19110002"


def test_xml_escapa_los_caracteres_especiales_y_respeta_filtros(client, h, crear_alumno, crear_grupo, inscribir):
    inscribir(crear_alumno("19110011", nombre="Ana <&> Beto", apaterno="Pérez"), crear_grupo())
    raiz = ET.fromstring(client.get(XML, headers=h).content)
    assert raiz.find("inscrito").findtext("alumno") == "Pérez García Ana <&> Beto"
    vacio = ET.fromstring(client.get(XML, params={"extraescolar": 999}, headers=h).content)
    assert vacio.get("total") == "0" and vacio.findall("inscrito") == []
