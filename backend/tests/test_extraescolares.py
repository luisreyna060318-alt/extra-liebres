"""Pruebas del catálogo de actividades extraescolares (HU-03.2)."""

import pytest

from app.models import Extraescolar
from tests.conftest import encabezado_de

ACTIVIDAD = {"nombreextra": "Fútbol", "tipo": "deportiva", "al_aire_libre": True}


@pytest.fixture()
def h_admin(admin):
    return encabezado_de(admin)


@pytest.fixture()
def h_cap(capturista):
    return encabezado_de(capturista)


def crear(client, h, **cambio):
    return client.post("/api/extraescolares", json={**ACTIVIDAD, **cambio}, headers=h)


# ---------- Permisos: leer cualquier sesión, escribir solo administrador ----------


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", "/api/extraescolares"),
        ("post", "/api/extraescolares"),
        ("get", "/api/extraescolares/1"),
        ("put", "/api/extraescolares/1"),
        ("delete", "/api/extraescolares/1"),
    ],
)
def test_extraescolares_sin_sesion_da_401(client, metodo, ruta):
    assert getattr(client, metodo)(ruta).status_code == 401


def test_el_capturista_puede_leer_actividades(client, h_cap, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    assert client.get("/api/extraescolares", headers=h_cap).status_code == 200
    assert client.get(f"/api/extraescolares/{idextra}", headers=h_cap).status_code == 200


def test_el_capturista_no_puede_escribir_actividades_da_403(client, db, h_cap, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    assert crear(client, h_cap, nombreextra="Otra").status_code == 403
    assert client.put(f"/api/extraescolares/{idextra}", json=ACTIVIDAD, headers=h_cap).status_code == 403
    assert client.delete(f"/api/extraescolares/{idextra}", headers=h_cap).status_code == 403
    assert db.query(Extraescolar).count() == 1


# ---------- HU-03.2 CA1 Crear y editar ----------


def test_hu_03_2_alta_correcta_devuelve_201_y_la_actividad_activa(client, h_admin):
    r = crear(client, h_admin)
    assert r.status_code == 201
    assert r.json() == {"idextraescolar": r.json()["idextraescolar"], **ACTIVIDAD, "activo": True}


def test_hu_03_2_al_aire_libre_es_false_por_defecto(client, h_admin):
    r = client.post("/api/extraescolares", json={"nombreextra": "Ajedrez", "tipo": "cultural"}, headers=h_admin)
    assert r.status_code == 201 and r.json()["al_aire_libre"] is False


@pytest.mark.parametrize("tipo", ["deportiva", "cultural", "civica"])
def test_hu_03_2_acepta_los_tres_tipos(client, h_admin, tipo):
    assert crear(client, h_admin, tipo=tipo).status_code == 201


@pytest.mark.parametrize(
    "cambio",
    [
        {"tipo": "recreativa"},
        {"tipo": ""},
        {"nombreextra": ""},
        {"nombreextra": "   "},
        {"nombreextra": "N" * 81},
        {"al_aire_libre": "quizás"},
    ],
)
def test_hu_03_2_datos_invalidos_dan_422_y_no_guardan_nada(client, db, h_admin, cambio):
    assert crear(client, h_admin, **cambio).status_code == 422
    assert db.query(Extraescolar).count() == 0


def test_hu_03_2_faltan_campos_obligatorios_da_422(client, h_admin):
    assert client.post("/api/extraescolares", json={"nombreextra": "Fútbol"}, headers=h_admin).status_code == 422


def test_hu_03_2_nombre_repetido_da_409_sin_distinguir_mayusculas(client, db, h_admin):
    crear(client, h_admin, nombreextra="Danza")
    assert crear(client, h_admin, nombreextra="Danza").status_code == 409
    r = crear(client, h_admin, nombreextra="DANZA")
    assert r.status_code == 409 and "nombre" in r.json()["detail"]
    assert db.query(Extraescolar).count() == 1


def test_hu_03_2_editar_cambia_los_datos(client, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    cambios = {"nombreextra": "Fútbol soccer", "tipo": "deportiva", "al_aire_libre": False}
    r = client.put(f"/api/extraescolares/{idextra}", json=cambios, headers=h_admin)
    assert r.status_code == 200
    assert r.json()["nombreextra"] == "Fútbol soccer" and r.json()["al_aire_libre"] is False
    assert client.get(f"/api/extraescolares/{idextra}", headers=h_admin).json()["nombreextra"] == "Fútbol soccer"


def test_hu_03_2_editar_puede_conservar_su_propio_nombre_pero_no_el_de_otra(client, h_admin):
    uno = crear(client, h_admin, nombreextra="Fútbol").json()["idextraescolar"]
    crear(client, h_admin, nombreextra="Danza", tipo="cultural")
    # mismo nombre (con otras mayúsculas) en la misma actividad: se permite
    assert client.put(f"/api/extraescolares/{uno}", json={**ACTIVIDAD, "nombreextra": "FÚTBOL"},
                      headers=h_admin).status_code == 200
    # nombre de otra actividad: 409
    assert client.put(f"/api/extraescolares/{uno}", json={**ACTIVIDAD, "nombreextra": "danza"},
                      headers=h_admin).status_code == 409


def test_hu_03_2_editar_valida_igual_que_crear(client, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    assert client.put(f"/api/extraescolares/{idextra}", json={**ACTIVIDAD, "tipo": "x"},
                      headers=h_admin).status_code == 422


def test_hu_03_2_desactivar_y_reactivar_con_put_activo(client, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    r = client.put(f"/api/extraescolares/{idextra}", json={**ACTIVIDAD, "activo": False}, headers=h_admin)
    assert r.status_code == 200 and r.json()["activo"] is False
    r = client.put(f"/api/extraescolares/{idextra}", json={**ACTIVIDAD, "activo": True}, headers=h_admin)
    assert r.json()["activo"] is True


def test_hu_03_2_editar_sin_indicar_activo_no_cambia_el_estado(client, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    client.put(f"/api/extraescolares/{idextra}", json={**ACTIVIDAD, "activo": False}, headers=h_admin)
    assert client.put(f"/api/extraescolares/{idextra}", json=ACTIVIDAD, headers=h_admin).json()["activo"] is False


# ---------- HU-03.2 CA3 Buscar por nombre y paginar ----------


@pytest.fixture()
def varias(client, h_admin):
    crear(client, h_admin, nombreextra="Fútbol")
    crear(client, h_admin, nombreextra="Fútbol americano")
    crear(client, h_admin, nombreextra="Ajedrez", tipo="cultural", al_aire_libre=False)
    inactiva = crear(client, h_admin, nombreextra="Banda de guerra", tipo="civica").json()["idextraescolar"]
    cuerpo = {"nombreextra": "Banda de guerra", "tipo": "civica", "activo": False}
    client.put(f"/api/extraescolares/{inactiva}", json=cuerpo, headers=h_admin)


def nombres(respuesta):
    return [a["nombreextra"] for a in respuesta.json()["items"]]


def test_hu_03_2_por_defecto_lista_solo_las_activas_ordenadas_por_nombre(client, h_cap, varias):
    r = client.get("/api/extraescolares", headers=h_cap)
    assert r.status_code == 200 and r.json()["total"] == 3
    assert nombres(r) == ["Ajedrez", "Fútbol", "Fútbol americano"]  # la inactiva no aparece


def test_hu_03_2_filtra_por_estado(client, h_cap, varias):
    assert nombres(client.get("/api/extraescolares?estado=bajas", headers=h_cap)) == ["Banda de guerra"]
    assert client.get("/api/extraescolares?estado=todos", headers=h_cap).json()["total"] == 4
    assert client.get("/api/extraescolares?estado=cualquiera", headers=h_cap).status_code == 422


def test_hu_03_2_busca_por_nombre_sin_distinguir_mayusculas(client, h_cap, varias):
    # (letras sin acento: el LOWER de SQLite solo conoce ASCII; PostgreSQL sí maneja acentos)
    assert nombres(client.get("/api/extraescolares?q=AMERICANO", headers=h_cap)) == ["Fútbol americano"]
    assert nombres(client.get("/api/extraescolares?q=bol", headers=h_cap)) == ["Fútbol", "Fútbol americano"]
    assert nombres(client.get("/api/extraescolares?q=AJED", headers=h_cap)) == ["Ajedrez"]
    assert nombres(client.get("/api/extraescolares?q=zzzz", headers=h_cap)) == []


def test_hu_03_2_los_simbolos_de_comodin_se_buscan_tal_cual(client, h_cap, varias):
    assert client.get("/api/extraescolares?q=%25", headers=h_cap).json()["total"] == 0
    assert client.get("/api/extraescolares?q=_", headers=h_cap).json()["total"] == 0


def test_hu_03_2_paginacion_con_total_de_toda_la_consulta(client, db, h_cap):
    for i in range(25):
        db.add(Extraescolar(nombreextra=f"Actividad {i:02d}", tipo="cultural"))
    db.commit()
    pagina1 = client.get("/api/extraescolares", headers=h_cap).json()
    assert pagina1["total"] == 25 and len(pagina1["items"]) == 10
    pagina3 = client.get("/api/extraescolares?page=3", headers=h_cap).json()
    assert len(pagina3["items"]) == 5 and pagina3["page"] == 3
    vistos = []
    for pagina in (1, 2, 3):
        vistos += nombres(client.get(f"/api/extraescolares?page={pagina}", headers=h_cap))
    assert len(vistos) == 25 and len(set(vistos)) == 25
    assert client.get("/api/extraescolares?size=51", headers=h_cap).status_code == 422


# ---------- 404 ----------


def test_hu_03_2_obtener_una_actividad_y_404_si_no_existe(client, h_cap, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    assert client.get(f"/api/extraescolares/{idextra}", headers=h_cap).json()["nombreextra"] == "Fútbol"
    assert client.get("/api/extraescolares/9999", headers=h_cap).status_code == 404


def test_hu_03_2_editar_o_eliminar_una_inexistente_da_404(client, h_admin):
    assert client.put("/api/extraescolares/9999", json=ACTIVIDAD, headers=h_admin).status_code == 404
    assert client.delete("/api/extraescolares/9999", headers=h_admin).status_code == 404


# ---------- HU-03.2 CA2 Eliminar ----------


def test_hu_03_2_eliminar_sin_grupos_da_204_y_borra_el_registro(client, db, h_admin):
    idextra = crear(client, h_admin).json()["idextraescolar"]
    r = client.delete(f"/api/extraescolares/{idextra}", headers=h_admin)
    assert r.status_code == 204 and r.content == b""
    assert db.get(Extraescolar, idextra) is None


def test_hu_03_2_eliminar_con_grupos_da_409_sugiere_desactivar_y_conserva_el_registro(
    client, db, h_admin, crear_grupo
):
    grupo = crear_grupo(actividad="Fútbol")
    r = client.delete(f"/api/extraescolares/{grupo.idextraescolar}", headers=h_admin)
    assert r.status_code == 409
    assert "activo=false" in r.json()["detail"]
    assert db.get(Extraescolar, grupo.idextraescolar) is not None  # sigue existiendo
