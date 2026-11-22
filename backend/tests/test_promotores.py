"""Pruebas del catálogo de promotores (HU-03.1)."""

import pytest

from app.models import Promotor
from tests.conftest import encabezado_de

PROMOTOR = {"rfc": "RUSP800101AB1", "nombre": "Pedro", "apaterno": "Ruiz", "amaterno": "Soto"}
EDICION = {"nombre": "Pedro", "apaterno": "Ruiz", "amaterno": "Soto"}  # lo que acepta el PUT (sin RFC)


@pytest.fixture()
def h_admin(admin):
    return encabezado_de(admin)


@pytest.fixture()
def h_cap(capturista):
    return encabezado_de(capturista)


# ---------- Permisos: leer cualquier sesión, escribir solo administrador ----------


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", "/api/promotores"),
        ("post", "/api/promotores"),
        ("get", "/api/promotores/RUSP800101AB1"),
        ("put", "/api/promotores/RUSP800101AB1"),
        ("delete", "/api/promotores/RUSP800101AB1"),
    ],
)
def test_promotores_sin_sesion_da_401(client, metodo, ruta):
    assert getattr(client, metodo)(ruta).status_code == 401


def test_el_capturista_puede_leer_promotores(client, h_cap, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    assert client.get("/api/promotores", headers=h_cap).status_code == 200
    assert client.get("/api/promotores/RUSP800101AB1", headers=h_cap).status_code == 200


def test_el_capturista_no_puede_escribir_promotores_da_403(client, db, h_cap, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    assert client.post("/api/promotores", json={**PROMOTOR, "rfc": "AAAA000101AAA"}, headers=h_cap).status_code == 403
    assert client.put("/api/promotores/RUSP800101AB1", json=EDICION, headers=h_cap).status_code == 403
    assert client.delete("/api/promotores/RUSP800101AB1", headers=h_cap).status_code == 403
    assert db.query(Promotor).count() == 1  # no se creó ni se borró nada


# ---------- HU-03.1 CA1 Crear, editar y desactivar ----------


def test_hu_03_1_alta_correcta_devuelve_201_y_el_promotor_activo(client, h_admin):
    r = client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    assert r.status_code == 201
    assert r.json() == {**PROMOTOR, "activo": True}


def test_hu_03_1_el_rfc_se_guarda_en_mayusculas_y_sin_espacios(client, h_admin):
    r = client.post("/api/promotores", json={**PROMOTOR, "rfc": " rusp 800101ab1 "}, headers=h_admin)
    assert r.status_code == 201
    assert r.json()["rfc"] == "RUSP800101AB1"


def test_hu_03_1_acepta_rfc_de_12_caracteres(client, h_admin):
    r = client.post("/api/promotores", json={**PROMOTOR, "rfc": "ABC800101XY2"}, headers=h_admin)
    assert r.status_code == 201


def test_hu_03_1_el_segundo_apellido_es_opcional(client, h_admin):
    sin = {k: v for k, v in PROMOTOR.items() if k != "amaterno"}
    r = client.post("/api/promotores", json=sin, headers=h_admin)
    assert r.status_code == 201 and r.json()["amaterno"] is None
    otro = {**PROMOTOR, "rfc": "AAAA000101AAA", "amaterno": " "}
    en_blanco = client.post("/api/promotores", json=otro, headers=h_admin)
    assert en_blanco.status_code == 201 and en_blanco.json()["amaterno"] is None


def test_hu_03_1_editar_cambia_los_datos_pero_no_el_rfc(client, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    r = client.put("/api/promotores/rusp800101ab1", json={**EDICION, "nombre": "Pablo", "rfc": "ZZZZ000101ZZZ"},
                   headers=h_admin)
    assert r.status_code == 200
    assert r.json()["rfc"] == "RUSP800101AB1"  # el RFC del cuerpo se ignora
    assert r.json()["nombre"] == "Pablo"
    assert client.get("/api/promotores/RUSP800101AB1", headers=h_admin).json()["nombre"] == "Pablo"


def test_hu_03_1_editar_valida_igual_que_crear(client, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    r = client.put("/api/promotores/RUSP800101AB1", json={**EDICION, "nombre": ""}, headers=h_admin)
    assert r.status_code == 422


def test_hu_03_1_desactivar_y_reactivar_con_put_activo(client, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    r = client.put("/api/promotores/RUSP800101AB1", json={**EDICION, "activo": False}, headers=h_admin)
    assert r.status_code == 200 and r.json()["activo"] is False
    r = client.put("/api/promotores/RUSP800101AB1", json={**EDICION, "activo": True}, headers=h_admin)
    assert r.json()["activo"] is True


def test_hu_03_1_editar_sin_indicar_activo_no_cambia_el_estado(client, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    client.put("/api/promotores/RUSP800101AB1", json={**EDICION, "activo": False}, headers=h_admin)
    r = client.put("/api/promotores/RUSP800101AB1", json={**EDICION, "nombre": "Otro"}, headers=h_admin)
    assert r.json()["activo"] is False


# ---------- HU-03.1 CA2 RFC repetido o con formato inválido ----------


def test_hu_03_1_rfc_duplicado_da_409(client, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    r = client.post("/api/promotores", json={**PROMOTOR, "nombre": "Otro"}, headers=h_admin)
    assert r.status_code == 409
    assert "RFC" in r.json()["detail"]


def test_hu_03_1_duplicado_tambien_se_detecta_con_otra_escritura_del_rfc(client, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    r = client.post("/api/promotores", json={**PROMOTOR, "rfc": "rusp800101ab1"}, headers=h_admin)
    assert r.status_code == 409


@pytest.mark.parametrize(
    "cambio",
    [
        {"rfc": "RUSP800101"},  # muy corto
        {"rfc": "RUSP800101AB12"},  # muy largo (14)
        {"rfc": "1USP800101AB1"},  # empieza con número
        {"rfc": "RUSP80010XAB1"},  # la fecha debe ser numérica
        {"rfc": "RUSP800101AB-"},  # símbolo no permitido en la homoclave
        {"rfc": ""},
        {"nombre": ""},
        {"nombre": "   "},
        {"apaterno": ""},
        {"nombre": "N" * 61},
    ],
)
def test_hu_03_1_datos_invalidos_dan_422_y_no_guardan_nada(client, db, h_admin, cambio):
    r = client.post("/api/promotores", json={**PROMOTOR, **cambio}, headers=h_admin)
    assert r.status_code == 422
    assert db.query(Promotor).count() == 0


def test_hu_03_1_faltan_campos_obligatorios_da_422(client, h_admin):
    assert client.post("/api/promotores", json={"rfc": "RUSP800101AB1"}, headers=h_admin).status_code == 422


# ---------- Listado: búsqueda, estado y paginación ----------


@pytest.fixture()
def varios(client, h_admin):
    for rfc, nombre, ap, am in [
        ("AAAA000101AAA", "Ana", "López", "García"),
        ("BBBB000101BBB", "Luis", "Martínez", "López"),
        ("CCCC000101CCC", "María", "Pérez", None),
    ]:
        client.post("/api/promotores", json={"rfc": rfc, "nombre": nombre, "apaterno": ap, "amaterno": am},
                    headers=h_admin)
    client.post("/api/promotores", json={"rfc": "DDDD000101DDD", "nombre": "Pedro", "apaterno": "Gómez"},
                headers=h_admin)
    client.put("/api/promotores/DDDD000101DDD", json={"nombre": "Pedro", "apaterno": "Gómez", "activo": False},
               headers=h_admin)


def rfcs(respuesta):
    return [p["rfc"] for p in respuesta.json()["items"]]


def test_hu_03_1_por_defecto_lista_solo_los_activos(client, h_cap, varios):
    r = client.get("/api/promotores", headers=h_cap)
    assert r.status_code == 200 and r.json()["total"] == 3
    assert "DDDD000101DDD" not in rfcs(r)
    assert (r.json()["page"], r.json()["size"]) == (1, 10)


def test_hu_03_1_filtra_por_estado(client, h_cap, varios):
    assert rfcs(client.get("/api/promotores?estado=bajas", headers=h_cap)) == ["DDDD000101DDD"]
    assert client.get("/api/promotores?estado=todos", headers=h_cap).json()["total"] == 4
    assert client.get("/api/promotores?estado=cualquiera", headers=h_cap).status_code == 422


def test_hu_03_1_busca_por_nombre_apellidos_o_rfc(client, h_cap, varios):
    assert rfcs(client.get("/api/promotores?q=ANA", headers=h_cap)) == ["AAAA000101AAA"]
    # "López" es primer apellido de Ana y segundo apellido de Luis
    assert sorted(rfcs(client.get("/api/promotores?q=lópez", headers=h_cap))) == ["AAAA000101AAA", "BBBB000101BBB"]
    assert rfcs(client.get("/api/promotores?q=cccc", headers=h_cap)) == ["CCCC000101CCC"]
    assert rfcs(client.get("/api/promotores?q=ana lópez", headers=h_cap)) == ["AAAA000101AAA"]
    assert rfcs(client.get("/api/promotores?q=ana pérez", headers=h_cap)) == []


def test_hu_03_1_los_simbolos_de_comodin_se_buscan_tal_cual(client, h_cap, varios):
    assert client.get("/api/promotores?q=%25", headers=h_cap).json()["total"] == 0
    assert client.get("/api/promotores?q=_", headers=h_cap).json()["total"] == 0


def test_hu_03_1_paginacion_con_total_de_toda_la_consulta(client, db, h_cap):
    for i in range(25):
        db.add(Promotor(rfc=f"PPPP0001{i:02d}AAA", nombre=f"Promotor{i:02d}", apaterno="Prueba"))
    db.commit()
    pagina1 = client.get("/api/promotores", headers=h_cap).json()
    assert pagina1["total"] == 25 and len(pagina1["items"]) == 10
    pagina3 = client.get("/api/promotores?page=3", headers=h_cap).json()
    assert len(pagina3["items"]) == 5 and pagina3["page"] == 3
    vistos = []
    for pagina in (1, 2, 3):
        vistos += rfcs(client.get(f"/api/promotores?page={pagina}", headers=h_cap))
    assert len(vistos) == 25 and len(set(vistos)) == 25
    assert client.get("/api/promotores?size=51", headers=h_cap).status_code == 422


# ---------- 404 ----------


def test_hu_03_1_obtener_un_promotor_y_404_si_no_existe(client, h_cap, varios):
    assert client.get("/api/promotores/aaaa000101aaa", headers=h_cap).json()["nombre"] == "Ana"
    assert client.get("/api/promotores/ZZZZ000101ZZZ", headers=h_cap).status_code == 404


def test_hu_03_1_editar_o_eliminar_un_inexistente_da_404(client, h_admin):
    assert client.put("/api/promotores/ZZZZ000101ZZZ", json=EDICION, headers=h_admin).status_code == 404
    assert client.delete("/api/promotores/ZZZZ000101ZZZ", headers=h_admin).status_code == 404


# ---------- HU-03.1 CA3 Eliminar ----------


def test_hu_03_1_eliminar_sin_grupos_da_204_y_borra_el_registro(client, db, h_admin):
    client.post("/api/promotores", json=PROMOTOR, headers=h_admin)
    r = client.delete("/api/promotores/RUSP800101AB1", headers=h_admin)
    assert r.status_code == 204 and r.content == b""
    assert db.get(Promotor, "RUSP800101AB1") is None


def test_hu_03_1_eliminar_con_grupos_da_409_sugiere_desactivar_y_conserva_el_registro(
    client, db, h_admin, crear_grupo
):
    crear_grupo(rfc="AAAA000101AAA")
    r = client.delete("/api/promotores/AAAA000101AAA", headers=h_admin)
    assert r.status_code == 409
    assert "activo=false" in r.json()["detail"]
    assert db.get(Promotor, "AAAA000101AAA") is not None  # sigue existiendo
    # y la alternativa que se sugiere sí funciona
    cuerpo = {"nombre": "Pedro", "apaterno": "Ruiz", "amaterno": "Soto", "activo": False}
    assert client.put("/api/promotores/AAAA000101AAA", json=cuerpo, headers=h_admin).json()["activo"] is False
