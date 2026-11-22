"""Pruebas de alumnos (HU-02.1 a HU-02.4)."""

from datetime import time

import pytest

from app.models import Alumno
from tests.conftest import encabezado_de

ALUMNO = {
    "nocontrol": "19110001",
    "nombre": "Ana",
    "apaterno": "López",
    "amaterno": "García",
    "sexo": "F",
    "carrera": "Ingeniería Industrial",
    "campus": "Campus I",
}


@pytest.fixture()
def h(capturista):
    """Encabezado de sesión de un capturista (también pueden usar alumnos los administradores)."""
    return encabezado_de(capturista)


# ---------- Todas las rutas exigen sesión ----------


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", "/api/alumnos"),
        ("get", "/api/alumnos/opciones"),
        ("post", "/api/alumnos"),
        ("get", "/api/alumnos/19110001"),
        ("put", "/api/alumnos/19110001"),
        ("delete", "/api/alumnos/19110001"),
        ("get", "/api/alumnos/19110001/historial"),
    ],
)
def test_alumnos_sin_sesion_da_401(client, metodo, ruta):
    assert getattr(client, metodo)(ruta).status_code == 401


def test_el_administrador_tambien_puede_usar_alumnos(client, admin):
    assert client.get("/api/alumnos", headers=encabezado_de(admin)).status_code == 200


# ---------- HU-02.1 Dar de alta un alumno ----------


def test_hu_02_1_alta_correcta_devuelve_201_y_el_alumno_activo(client, h):
    r = client.post("/api/alumnos", json=ALUMNO, headers=h)
    assert r.status_code == 201
    assert r.json() == {**ALUMNO, "activo": True}


def test_hu_02_1_el_numero_de_control_se_guarda_en_mayusculas_y_sin_espacios(client, h):
    r = client.post("/api/alumnos", json={**ALUMNO, "nocontrol": " b19110001 "}, headers=h)
    assert r.status_code == 201
    assert r.json()["nocontrol"] == "B19110001"


def test_hu_02_1_numero_de_control_duplicado_da_409(client, h):
    client.post("/api/alumnos", json=ALUMNO, headers=h)
    r = client.post("/api/alumnos", json={**ALUMNO, "nombre": "Otra"}, headers=h)
    assert r.status_code == 409
    assert "número de control" in r.json()["detail"]


def test_hu_02_1_duplicado_tambien_se_detecta_con_otra_escritura_del_mismo_numero(client, h):
    client.post("/api/alumnos", json={**ALUMNO, "nocontrol": "B19110001"}, headers=h)
    r = client.post("/api/alumnos", json={**ALUMNO, "nocontrol": "b19110001"}, headers=h)
    assert r.status_code == 409


@pytest.mark.parametrize(
    "cambio",
    [
        {"nocontrol": "123"},  # muy corto
        {"nocontrol": "1911 0001"},  # con espacio
        {"nocontrol": "19110001; DROP TABLE alumno"},  # caracteres no permitidos
        {"nombre": ""},
        {"nombre": "   "},
        {"apaterno": ""},
        {"sexo": "X"},
        {"carrera": ""},
        {"campus": "C" * 41},
    ],
)
def test_hu_02_1_datos_invalidos_dan_422_y_no_guardan_nada(client, db, h, cambio):
    r = client.post("/api/alumnos", json={**ALUMNO, **cambio}, headers=h)
    assert r.status_code == 422
    assert db.query(Alumno).count() == 0


def test_hu_02_1_faltan_campos_obligatorios_da_422(client, h):
    assert client.post("/api/alumnos", json={"nocontrol": "19110001"}, headers=h).status_code == 422


def test_hu_02_1_el_segundo_apellido_es_opcional(client, h):
    sin_amaterno = {k: v for k, v in ALUMNO.items() if k != "amaterno"}
    r = client.post("/api/alumnos", json=sin_amaterno, headers=h)
    assert r.status_code == 201 and r.json()["amaterno"] is None
    en_blanco = client.post("/api/alumnos", json={**ALUMNO, "nocontrol": "19110002", "amaterno": "  "}, headers=h)
    assert en_blanco.status_code == 201 and en_blanco.json()["amaterno"] is None


# ---------- HU-02.2 Buscar y listar alumnos ----------


@pytest.fixture()
def varios(crear_alumno):
    crear_alumno("19110001", "Ana", "López", "García", "F", "Ingeniería Industrial", "Campus I")
    crear_alumno("19110002", "Luis", "Martínez", "López", "M", "Ingeniería Industrial", "Campus II")
    crear_alumno("19110003", "María", "Pérez", "Ruiz", "F", "Arquitectura", "Campus I")
    crear_alumno("19110004", "Pedro", "Gómez", None, "M", "Arquitectura", "Campus II", activo=False)


def numeros(respuesta):
    return [a["nocontrol"] for a in respuesta.json()["items"]]


def test_hu_02_2_sin_filtros_lista_solo_los_activos_con_total(client, h, varios):
    r = client.get("/api/alumnos", headers=h)
    assert r.status_code == 200
    assert r.json()["total"] == 3
    assert "19110004" not in numeros(r)  # el de baja no aparece por defecto
    assert (r.json()["page"], r.json()["size"]) == (1, 10)


def test_hu_02_2_busca_por_nombre_sin_distinguir_mayusculas(client, h, varios):
    assert numeros(client.get("/api/alumnos?q=ANA", headers=h)) == ["19110001"]


def test_hu_02_2_busca_en_cualquiera_de_los_dos_apellidos(client, h, varios):
    # "López" es primer apellido de Ana y segundo apellido de Luis
    assert sorted(numeros(client.get("/api/alumnos?q=lópez", headers=h))) == ["19110001", "19110002"]


def test_hu_02_2_busca_por_numero_de_control_completo_o_parcial(client, h, varios):
    assert numeros(client.get("/api/alumnos?q=19110003", headers=h)) == ["19110003"]
    assert len(numeros(client.get("/api/alumnos?q=1911", headers=h))) == 3


def test_hu_02_2_varias_palabras_deben_coincidir_todas(client, h, varios):
    assert numeros(client.get("/api/alumnos?q=ana lópez", headers=h)) == ["19110001"]
    assert numeros(client.get("/api/alumnos?q=ana pérez", headers=h)) == []


def test_hu_02_2_los_simbolos_de_comodin_se_buscan_tal_cual(client, h, varios):
    # Si % se tratara como comodín, devolvería a todos los alumnos
    assert client.get("/api/alumnos?q=%25", headers=h).json()["total"] == 0
    assert client.get("/api/alumnos?q=_", headers=h).json()["total"] == 0


def test_hu_02_2_filtra_por_carrera_y_por_campus(client, h, varios):
    assert sorted(numeros(client.get("/api/alumnos?carrera=Arquitectura", headers=h))) == ["19110003"]
    assert sorted(numeros(client.get("/api/alumnos?campus=Campus I", headers=h))) == ["19110001", "19110003"]


def test_hu_02_2_los_filtros_se_combinan_con_y(client, h, varios):
    r = client.get("/api/alumnos?carrera=Ingeniería Industrial&campus=Campus II&q=luis", headers=h)
    assert numeros(r) == ["19110002"]
    sin_coincidencia = client.get("/api/alumnos?carrera=Arquitectura&campus=Campus II", headers=h)
    assert sin_coincidencia.json()["total"] == 0  # el único de Campus II en Arquitectura está de baja


def test_hu_02_2_filtra_por_estado(client, h, varios):
    assert numeros(client.get("/api/alumnos?estado=bajas", headers=h)) == ["19110004"]
    assert client.get("/api/alumnos?estado=todos", headers=h).json()["total"] == 4
    assert client.get("/api/alumnos?estado=cualquiera", headers=h).status_code == 422


def test_hu_02_2_sin_resultados_devuelve_lista_vacia_y_total_cero(client, h, varios):
    r = client.get("/api/alumnos?q=zzzz", headers=h)
    assert r.status_code == 200
    assert r.json()["items"] == [] and r.json()["total"] == 0


def test_hu_02_2_paginacion_con_total_de_toda_la_consulta(client, h, crear_alumno):
    for i in range(25):
        crear_alumno(f"2011{i:04d}", nombre=f"Alumno{i:02d}", apaterno="Prueba")
    pagina1 = client.get("/api/alumnos", headers=h).json()
    assert pagina1["total"] == 25 and len(pagina1["items"]) == 10
    pagina3 = client.get("/api/alumnos?page=3", headers=h).json()
    assert len(pagina3["items"]) == 5 and pagina3["page"] == 3
    pequeno = client.get("/api/alumnos?size=7&page=2", headers=h).json()
    assert len(pequeno["items"]) == 7 and pequeno["total"] == 25
    # las páginas no se repiten ni se saltan alumnos: entre las 3 suman los 25, todos distintos
    vistos = []
    for pagina in (1, 2, 3):
        vistos += numeros(client.get(f"/api/alumnos?page={pagina}", headers=h))
    assert len(vistos) == 25 and len(set(vistos)) == 25


def test_hu_02_2_el_tamano_de_pagina_esta_limitado(client, h):
    assert client.get("/api/alumnos?size=51", headers=h).status_code == 422
    assert client.get("/api/alumnos?size=0", headers=h).status_code == 422
    assert client.get("/api/alumnos?page=0", headers=h).status_code == 422


def test_hu_02_2_opciones_devuelve_carreras_y_campus_sin_repetir(client, h, varios):
    r = client.get("/api/alumnos/opciones", headers=h)
    assert r.status_code == 200
    assert r.json() == {"carreras": ["Arquitectura", "Ingeniería Industrial"], "campus": ["Campus I", "Campus II"]}


# ---------- HU-02.3 Editar y dar de baja ----------


def test_hu_02_3_obtener_un_alumno_y_404_si_no_existe(client, h, varios):
    assert client.get("/api/alumnos/19110001", headers=h).json()["nombre"] == "Ana"
    assert client.get("/api/alumnos/19110001".lower(), headers=h).status_code == 200
    assert client.get("/api/alumnos/00000000", headers=h).status_code == 404


def test_hu_02_3_editar_cambia_los_datos_pero_no_el_numero_de_control(client, h, varios):
    cambios = {k: v for k, v in ALUMNO.items() if k != "nocontrol"} | {"nombre": "Ana María", "campus": "Campus II"}
    r = client.put("/api/alumnos/19110001", json={**cambios, "nocontrol": "99999999"}, headers=h)
    assert r.status_code == 200
    assert r.json()["nocontrol"] == "19110001"  # el número de control del cuerpo se ignora
    assert r.json()["nombre"] == "Ana María" and r.json()["campus"] == "Campus II"
    assert client.get("/api/alumnos/19110001", headers=h).json()["campus"] == "Campus II"


def test_hu_02_3_editar_valida_igual_que_crear(client, h, varios):
    mal = {k: v for k, v in ALUMNO.items() if k != "nocontrol"} | {"sexo": "Z"}
    assert client.put("/api/alumnos/19110001", json=mal, headers=h).status_code == 422


def test_hu_02_3_editar_un_alumno_inexistente_da_404(client, h):
    cuerpo = {k: v for k, v in ALUMNO.items() if k != "nocontrol"}
    assert client.put("/api/alumnos/00000000", json=cuerpo, headers=h).status_code == 404


def test_hu_02_3_baja_logica_no_borra_al_alumno_ni_su_historial(client, db, h, varios, crear_grupo, inscribir):
    inscribir(db.get(Alumno, "19110001"), crear_grupo(), 90, "Notable")

    r = client.delete("/api/alumnos/19110001", headers=h)
    assert r.status_code == 204 and r.content == b""

    assert db.get(Alumno, "19110001") is not None  # la fila sigue existiendo
    assert db.get(Alumno, "19110001").activo is False
    assert "19110001" not in numeros(client.get("/api/alumnos", headers=h))  # ya no sale por defecto
    assert "19110001" in numeros(client.get("/api/alumnos?estado=bajas", headers=h))
    assert len(client.get("/api/alumnos/19110001/historial", headers=h).json()) == 1  # historial intacto


def test_hu_02_3_dar_de_baja_dos_veces_o_a_un_inexistente(client, h, varios):
    assert client.delete("/api/alumnos/19110001", headers=h).status_code == 204
    assert client.delete("/api/alumnos/19110001", headers=h).status_code == 204
    assert client.delete("/api/alumnos/00000000", headers=h).status_code == 404


def test_hu_02_3_reactivar_a_un_alumno_dado_de_baja(client, h, varios):
    cuerpo = {"nombre": "Pedro", "apaterno": "Gómez", "sexo": "M", "carrera": "Arquitectura",
              "campus": "Campus II", "activo": True}
    r = client.put("/api/alumnos/19110004", json=cuerpo, headers=h)
    assert r.status_code == 200 and r.json()["activo"] is True
    assert "19110004" in numeros(client.get("/api/alumnos", headers=h))


def test_hu_02_3_editar_sin_indicar_activo_no_cambia_el_estado(client, h, varios):
    cuerpo = {"nombre": "Pedro", "apaterno": "Gómez", "sexo": "M", "carrera": "Arquitectura", "campus": "Campus II"}
    assert client.put("/api/alumnos/19110004", json=cuerpo, headers=h).json()["activo"] is False


# ---------- HU-02.4 Historial del alumno ----------


def test_hu_02_4_historial_ordenado_del_semestre_mas_reciente_al_mas_antiguo(
    client, h, crear_alumno, crear_grupo, inscribir
):
    alumno = crear_alumno("19110001")
    inscribir(alumno, crear_grupo(anio=2025, mesinicio=8, mestermino=12, actividad="Ajedrez", tipo="cultural",
                                  aula="Aula A-101"), 78, "Bueno")
    inscribir(alumno, crear_grupo(anio=2026, mesinicio=1, mestermino=6, actividad="Fútbol"), 96, "Excelente")
    inscribir(alumno, crear_grupo(anio=2024, mesinicio=1, mestermino=6, actividad="Rondalla", tipo="cultural",
                                  aula="Auditorio"), None, None)

    r = client.get("/api/alumnos/19110001/historial", headers=h)
    assert r.status_code == 200
    historial = r.json()
    assert [(i["semestre_anio"], i["actividad"]) for i in historial] == [
        (2026, "Fútbol"),
        (2025, "Ajedrez"),
        (2024, "Rondalla"),
    ]
    primero = historial[0]
    assert primero["calificacion"] == 96 and primero["desempenio"] == "Excelente"
    assert primero["promotor"] == "Pedro Ruiz Soto"
    assert (primero["semestre_mesinicio"], primero["semestre_mestermino"]) == (1, 6)
    assert primero["dia"] == "lunes" and primero["horainicio"] == "08:00:00" and primero["aula"] == "Cancha de fútbol"
    assert historial[2]["calificacion"] is None  # aún sin evaluar


def test_hu_02_4_solo_muestra_las_inscripciones_de_ese_alumno(client, h, crear_alumno, crear_grupo, inscribir):
    ana, luis = crear_alumno("19110001"), crear_alumno("19110002", nombre="Luis")
    grupo = crear_grupo()
    inscribir(ana, grupo, 90, "Notable")
    inscribir(luis, grupo, 70, "Suficiente")
    assert len(client.get("/api/alumnos/19110001/historial", headers=h).json()) == 1


def test_hu_02_4_alumno_sin_inscripciones_devuelve_lista_vacia(client, h, crear_alumno):
    crear_alumno("19110001")
    r = client.get("/api/alumnos/19110001/historial", headers=h)
    assert r.status_code == 200 and r.json() == []


def test_hu_02_4_historial_de_un_alumno_inexistente_da_404(client, h):
    assert client.get("/api/alumnos/00000000/historial", headers=h).status_code == 404


def test_hu_02_4_el_historial_de_un_alumno_de_baja_sigue_disponible(client, h, crear_alumno, crear_grupo, inscribir):
    alumno = crear_alumno("19110001", activo=False)
    inscribir(alumno, crear_grupo(inicio=time(10), fin=time(11)), 88, "Notable")
    assert len(client.get("/api/alumnos/19110001/historial", headers=h).json()) == 1
