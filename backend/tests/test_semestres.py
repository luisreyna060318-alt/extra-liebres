"""Pruebas del catálogo de semestres (HU-03.3)."""

import pytest

from app.models import Semestre
from tests.conftest import encabezado_de

SEMESTRE = {"anio": 2026, "mesinicio": 1, "mestermino": 6}


@pytest.fixture()
def h_admin(admin):
    return encabezado_de(admin)


@pytest.fixture()
def h_cap(capturista):
    return encabezado_de(capturista)


def crear(client, h, **cambio):
    return client.post("/api/semestres", json={**SEMESTRE, **cambio}, headers=h)


# ---------- Permisos: leer cualquier sesión, escribir solo administrador ----------


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", "/api/semestres"),
        ("post", "/api/semestres"),
        ("get", "/api/semestres/1"),
        ("put", "/api/semestres/1"),
        ("delete", "/api/semestres/1"),
    ],
)
def test_semestres_sin_sesion_da_401(client, metodo, ruta):
    assert getattr(client, metodo)(ruta).status_code == 401


def test_el_capturista_puede_leer_semestres(client, h_cap, h_admin):
    idsem = crear(client, h_admin).json()["idsemestre"]
    assert client.get("/api/semestres", headers=h_cap).status_code == 200
    assert client.get(f"/api/semestres/{idsem}", headers=h_cap).status_code == 200


def test_el_capturista_no_puede_escribir_semestres_da_403(client, db, h_cap, h_admin):
    idsem = crear(client, h_admin).json()["idsemestre"]
    assert crear(client, h_cap, anio=2027).status_code == 403
    assert client.put(f"/api/semestres/{idsem}", json=SEMESTRE, headers=h_cap).status_code == 403
    assert client.delete(f"/api/semestres/{idsem}", headers=h_cap).status_code == 403
    assert db.query(Semestre).count() == 1


# ---------- HU-03.3 CA1 Crear y editar ----------


def test_hu_03_3_alta_correcta_devuelve_201(client, h_admin):
    r = crear(client, h_admin)
    assert r.status_code == 201
    assert r.json() == {"idsemestre": r.json()["idsemestre"], **SEMESTRE}


@pytest.mark.parametrize(
    "cambio",
    [
        {"anio": 1999},
        {"anio": 2101},
        {"mesinicio": 0},
        {"mesinicio": 13},
        {"mestermino": 0},
        {"mestermino": 13},
        {"anio": "dos mil"},
    ],
)
def test_hu_03_3_datos_invalidos_dan_422_y_no_guardan_nada(client, db, h_admin, cambio):
    assert crear(client, h_admin, **cambio).status_code == 422
    assert db.query(Semestre).count() == 0


def test_hu_03_3_los_limites_validos_se_aceptan(client, h_admin):
    assert crear(client, h_admin, anio=2000, mesinicio=1, mestermino=12).status_code == 201
    assert crear(client, h_admin, anio=2100, mesinicio=12, mestermino=1).status_code == 201


def test_hu_03_3_faltan_campos_obligatorios_da_422(client, h_admin):
    assert client.post("/api/semestres", json={"anio": 2026}, headers=h_admin).status_code == 422


def test_hu_03_3_editar_cambia_los_datos(client, h_admin):
    idsem = crear(client, h_admin).json()["idsemestre"]
    r = client.put(f"/api/semestres/{idsem}", json={"anio": 2026, "mesinicio": 1, "mestermino": 5}, headers=h_admin)
    assert r.status_code == 200 and r.json()["mestermino"] == 5
    assert client.get(f"/api/semestres/{idsem}", headers=h_admin).json()["mestermino"] == 5


def test_hu_03_3_editar_valida_igual_que_crear(client, h_admin):
    idsem = crear(client, h_admin).json()["idsemestre"]
    assert client.put(f"/api/semestres/{idsem}", json={**SEMESTRE, "mesinicio": 13}, headers=h_admin).status_code == 422


# ---------- HU-03.3 CA2 Combinación repetida ----------


def test_hu_03_3_mismo_anio_y_mes_de_inicio_da_409(client, db, h_admin):
    crear(client, h_admin)
    r = crear(client, h_admin, mestermino=7)  # cambia el mes de término, pero (anio, mesinicio) es el mismo
    assert r.status_code == 409
    assert "año" in r.json()["detail"]
    assert db.query(Semestre).count() == 1


def test_hu_03_3_mismo_mes_de_otro_anio_o_otro_mes_del_mismo_anio_si_se_permite(client, h_admin):
    crear(client, h_admin)
    assert crear(client, h_admin, anio=2025).status_code == 201
    assert crear(client, h_admin, mesinicio=8, mestermino=12).status_code == 201


def test_hu_03_3_editar_puede_conservar_su_combinacion_pero_no_la_de_otro(client, h_admin):
    uno = crear(client, h_admin).json()["idsemestre"]
    crear(client, h_admin, mesinicio=8, mestermino=12)
    assert client.put(f"/api/semestres/{uno}", json={**SEMESTRE, "mestermino": 5}, headers=h_admin).status_code == 200
    r = client.put(f"/api/semestres/{uno}", json={**SEMESTRE, "mesinicio": 8, "mestermino": 12}, headers=h_admin)
    assert r.status_code == 409


# ---------- Listado ----------


def test_hu_03_3_lista_del_mas_reciente_al_mas_antiguo(client, h_cap, h_admin):
    crear(client, h_admin, anio=2025, mesinicio=1)
    crear(client, h_admin, anio=2026, mesinicio=1, mestermino=6)
    crear(client, h_admin, anio=2025, mesinicio=8, mestermino=12)
    crear(client, h_admin, anio=2026, mesinicio=8, mestermino=12)
    r = client.get("/api/semestres", headers=h_cap)
    assert r.status_code == 200 and r.json()["total"] == 4
    assert [(s["anio"], s["mesinicio"]) for s in r.json()["items"]] == [(2026, 8), (2026, 1), (2025, 8), (2025, 1)]


def test_hu_03_3_paginacion_con_total_de_toda_la_consulta(client, db, h_cap):
    for i in range(25):
        db.add(Semestre(anio=2000 + i, mesinicio=1, mestermino=6))
    db.commit()
    pagina1 = client.get("/api/semestres", headers=h_cap).json()
    assert pagina1["total"] == 25 and len(pagina1["items"]) == 10
    assert pagina1["items"][0]["anio"] == 2024  # el más reciente primero
    pagina3 = client.get("/api/semestres?page=3", headers=h_cap).json()
    assert len(pagina3["items"]) == 5 and pagina3["page"] == 3
    vistos = []
    for pagina in (1, 2, 3):
        vistos += [s["idsemestre"] for s in client.get(f"/api/semestres?page={pagina}", headers=h_cap).json()["items"]]
    assert len(vistos) == 25 and len(set(vistos)) == 25
    assert client.get("/api/semestres?size=51", headers=h_cap).status_code == 422


def test_hu_03_3_sin_semestres_devuelve_lista_vacia(client, h_cap):
    r = client.get("/api/semestres", headers=h_cap)
    assert r.status_code == 200 and r.json()["items"] == [] and r.json()["total"] == 0


# ---------- 404 ----------


def test_hu_03_3_obtener_un_semestre_y_404_si_no_existe(client, h_cap, h_admin):
    idsem = crear(client, h_admin).json()["idsemestre"]
    assert client.get(f"/api/semestres/{idsem}", headers=h_cap).json()["anio"] == 2026
    assert client.get("/api/semestres/9999", headers=h_cap).status_code == 404


def test_hu_03_3_editar_o_eliminar_uno_inexistente_da_404(client, h_admin):
    assert client.put("/api/semestres/9999", json=SEMESTRE, headers=h_admin).status_code == 404
    assert client.delete("/api/semestres/9999", headers=h_admin).status_code == 404


# ---------- HU-03.3 CA3 Eliminar ----------


def test_hu_03_3_eliminar_sin_grupos_da_204_y_borra_el_registro(client, db, h_admin):
    idsem = crear(client, h_admin).json()["idsemestre"]
    r = client.delete(f"/api/semestres/{idsem}", headers=h_admin)
    assert r.status_code == 204 and r.content == b""
    assert db.get(Semestre, idsem) is None


def test_hu_03_3_eliminar_con_grupos_da_409_y_conserva_el_registro(client, db, h_admin, crear_grupo):
    grupo = crear_grupo(anio=2026, mesinicio=1)
    r = client.delete(f"/api/semestres/{grupo.idsemestre}", headers=h_admin)
    assert r.status_code == 409
    assert "grupo" in r.json()["detail"]
    assert db.get(Semestre, grupo.idsemestre) is not None  # sigue existiendo
