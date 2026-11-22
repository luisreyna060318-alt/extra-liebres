"""Pruebas del tablero de resumen (HU-07.1).

Los datos son conocidos, así que los totales esperados están escritos a mano (y se comparan además
con una consulta SQL directa, distinta a la del servicio).
"""

import pytest
from sqlalchemy import text

from app.core.constantes import DESEMPENOS
from tests.conftest import encabezado_de

RUTA = "/api/dashboard/resumen"


@pytest.fixture()
def h(capturista):
    return encabezado_de(capturista)


@pytest.fixture()
def datos(db, crear_alumno, crear_grupo, inscribir):
    """Tres semestres con datos conocidos.

    Alumnos: 6, de los cuales 1 (a6) está de baja -> 5 activos.

    S1 = 2025 (mes 8): 2 grupos (Fútbol, Ajedrez), 3 inscripciones.
        Fútbol: a1 100 (Excelente), a2 80 (Bueno) · Ajedrez: a3 60 (Insuficiente)
        promedio = (100 + 80 + 60) / 3 = 80.0
    S2 = 2026 (mes 1): 3 grupos (Fútbol x2, Danza), 6 inscripciones, 4 calificadas.
        Fútbol g3: a1 90 (Notable), a2 95 (Excelente) · Fútbol g5: a3 85 (Notable), a6 sin calificación
        Danza: a4 sin calificación, a5 71 (Suficiente)
        promedio = (90 + 95 + 85 + 71) / 4 = 85.25
    S3 = 2026 (mes 8): 1 grupo (Ajedrez) sin inscripciones. Es el más reciente.
    """
    a = {n: crear_alumno(f"1911000{n}", nombre=f"Alumno{n}", activo=(n != 6)) for n in range(1, 7)}

    s1_futbol = crear_grupo(anio=2025, mesinicio=8, mestermino=12, actividad="Fútbol")
    s1_ajedrez = crear_grupo(anio=2025, mesinicio=8, mestermino=12, actividad="Ajedrez", tipo="cultural", aula="Aula 1")
    inscribir(a[1], s1_futbol, 100, "Excelente")
    inscribir(a[2], s1_futbol, 80, "Bueno")
    inscribir(a[3], s1_ajedrez, 60, "Insuficiente")

    s2_futbol_a = crear_grupo(anio=2026, mesinicio=1, mestermino=6, actividad="Fútbol")
    s2_danza = crear_grupo(anio=2026, mesinicio=1, mestermino=6, actividad="Danza", tipo="cultural", aula="Aula 2")
    s2_futbol_b = crear_grupo(anio=2026, mesinicio=1, mestermino=6, actividad="Fútbol", dia="martes")
    inscribir(a[1], s2_futbol_a, 90, "Notable")
    inscribir(a[2], s2_futbol_a, 95, "Excelente")
    inscribir(a[3], s2_futbol_b, 85, "Notable")
    inscribir(a[6], s2_futbol_b)
    inscribir(a[4], s2_danza)
    inscribir(a[5], s2_danza, 71, "Suficiente")

    crear_grupo(anio=2026, mesinicio=8, mestermino=12, actividad="Ajedrez", tipo="cultural", aula="Aula 1")


def id_semestre(db, anio, mesinicio):
    return db.execute(
        text("SELECT idsemestre FROM semestre WHERE anio = :a AND mesinicio = :m"), {"a": anio, "m": mesinicio}
    ).scalar_one()


def distribucion(**cuentas):
    """Las cinco categorías en orden; las que no se mencionan valen 0."""
    return [{"desempenio": d, "total": cuentas.get(d, 0)} for d in DESEMPENOS]


# ---------- Sesión ----------


def test_resumen_sin_sesion_da_401(client):
    assert client.get(RUTA).status_code == 401


def test_el_administrador_tambien_ve_el_resumen(client, admin):
    assert client.get(RUTA, headers=encabezado_de(admin)).status_code == 200


# ---------- Totales exactos por semestre (CA1 a CA3) ----------


def test_resumen_del_primer_semestre(client, h, db, datos):
    r = client.get(RUTA, params={"semestre": id_semestre(db, 2025, 8)}, headers=h)
    assert r.status_code == 200
    assert r.json() == {
        "totales": {"alumnos_activos": 5, "grupos": 2, "inscripciones": 3},
        "inscritos_por_actividad": [{"actividad": "Fútbol", "total": 2}, {"actividad": "Ajedrez", "total": 1}],
        "distribucion_desempenio": distribucion(Excelente=1, Bueno=1, Insuficiente=1),
        "promedio_calificacion": 80.0,
    }


def test_resumen_del_segundo_semestre(client, h, db, datos):
    r = client.get(RUTA, params={"semestre": id_semestre(db, 2026, 1)}, headers=h)
    assert r.status_code == 200
    assert r.json() == {
        "totales": {"alumnos_activos": 5, "grupos": 3, "inscripciones": 6},
        "inscritos_por_actividad": [{"actividad": "Fútbol", "total": 4}, {"actividad": "Danza", "total": 2}],
        # a6 y a4 no tienen calificación: no entran a la distribución ni al promedio
        "distribucion_desempenio": distribucion(Excelente=1, Notable=2, Suficiente=1),
        "promedio_calificacion": 85.25,
    }


def test_cambiar_de_semestre_recalcula_todo_menos_los_alumnos_activos(client, h, db, datos):
    s1 = client.get(RUTA, params={"semestre": id_semestre(db, 2025, 8)}, headers=h).json()
    s2 = client.get(RUTA, params={"semestre": id_semestre(db, 2026, 1)}, headers=h).json()
    assert s1["totales"]["alumnos_activos"] == s2["totales"]["alumnos_activos"] == 5
    assert s1["totales"]["grupos"] != s2["totales"]["grupos"]
    assert s1["totales"]["inscripciones"] != s2["totales"]["inscripciones"]
    assert s1["inscritos_por_actividad"] != s2["inscritos_por_actividad"]
    assert s1["distribucion_desempenio"] != s2["distribucion_desempenio"]
    assert s1["promedio_calificacion"] != s2["promedio_calificacion"]


def test_las_cifras_coinciden_con_una_consulta_sql_directa(client, h, db, datos):
    """Revisión independiente: SQL escrito a mano contra las tablas, sin usar el servicio."""
    for anio, mes in [(2025, 8), (2026, 1), (2026, 8)]:
        ids = id_semestre(db, anio, mes)
        grupos = db.execute(text("SELECT COUNT(*) FROM grupo WHERE idsemestre = :s"), {"s": ids}).scalar_one()
        inscripciones = db.execute(
            text("SELECT COUNT(*) FROM alumno_grupo ag JOIN grupo g ON g.idgrupo = ag.idgrupo WHERE g.idsemestre = :s"),
            {"s": ids},
        ).scalar_one()
        promedio = db.execute(
            text(
                "SELECT AVG(ag.calificacion) FROM alumno_grupo ag JOIN grupo g ON g.idgrupo = ag.idgrupo "
                "WHERE g.idsemestre = :s"
            ),
            {"s": ids},
        ).scalar_one()
        por_actividad = db.execute(
            text(
                "SELECT e.nombreextra, COUNT(*) FROM alumno_grupo ag JOIN grupo g ON g.idgrupo = ag.idgrupo "
                "JOIN extraescolar e ON e.idextraescolar = g.idextraescolar WHERE g.idsemestre = :s "
                "GROUP BY e.nombreextra"
            ),
            {"s": ids},
        ).all()

        cuerpo = client.get(RUTA, params={"semestre": ids}, headers=h).json()
        assert cuerpo["totales"]["grupos"] == grupos
        assert cuerpo["totales"]["inscripciones"] == inscripciones
        assert cuerpo["promedio_calificacion"] == (None if promedio is None else round(promedio, 2))
        assert {f["actividad"]: f["total"] for f in cuerpo["inscritos_por_actividad"]} == dict(por_actividad)

    activos = db.execute(text("SELECT COUNT(*) FROM alumno WHERE activo")).scalar_one()
    assert client.get(RUTA, headers=h).json()["totales"]["alumnos_activos"] == activos == 5


def test_la_distribucion_siempre_trae_las_cinco_categorias(client, h, db, datos):
    cuerpo = client.get(RUTA, params={"semestre": id_semestre(db, 2025, 8)}, headers=h).json()
    assert [f["desempenio"] for f in cuerpo["distribucion_desempenio"]] == [
        "Excelente", "Notable", "Bueno", "Suficiente", "Insuficiente",
    ]  # fmt: skip
    # Notable y Suficiente valen 0 en este semestre pero aparecen
    assert {f["desempenio"]: f["total"] for f in cuerpo["distribucion_desempenio"]}["Notable"] == 0


# ---------- Semestre por omisión ----------


def test_sin_semestre_usa_el_mas_reciente_por_anio_y_luego_por_mes(client, h, datos):
    # El más reciente es 2026 mes 8: un grupo y ninguna inscripción
    r = client.get(RUTA, headers=h)
    assert r.status_code == 200
    assert r.json() == {
        "totales": {"alumnos_activos": 5, "grupos": 1, "inscripciones": 0},
        "inscritos_por_actividad": [],
        "distribucion_desempenio": distribucion(),
        "promedio_calificacion": None,
    }


def test_un_semestre_sin_calificaciones_da_promedio_null(client, h, db, crear_alumno, crear_grupo, inscribir):
    grupo = crear_grupo(anio=2026, mesinicio=1)
    inscribir(crear_alumno("19119999"), grupo)  # inscrito pero sin calificar
    cuerpo = client.get(RUTA, headers=h).json()
    assert cuerpo["totales"] == {"alumnos_activos": 1, "grupos": 1, "inscripciones": 1}
    assert cuerpo["inscritos_por_actividad"] == [{"actividad": "Fútbol", "total": 1}]
    assert cuerpo["distribucion_desempenio"] == distribucion()
    assert cuerpo["promedio_calificacion"] is None


# ---------- Casos límite ----------


def test_sin_semestres_todo_en_cero_y_promedio_null(client, h, crear_alumno):
    crear_alumno("19110001")
    r = client.get(RUTA, headers=h)
    assert r.status_code == 200
    assert r.json() == {
        "totales": {"alumnos_activos": 1, "grupos": 0, "inscripciones": 0},
        "inscritos_por_actividad": [],
        "distribucion_desempenio": distribucion(),
        "promedio_calificacion": None,
    }


def test_base_totalmente_vacia(client, h):
    r = client.get(RUTA, headers=h)
    assert r.status_code == 200
    assert r.json()["totales"] == {"alumnos_activos": 0, "grupos": 0, "inscripciones": 0}
    assert r.json()["promedio_calificacion"] is None


def test_semestre_inexistente_da_404(client, h, datos):
    r = client.get(RUTA, params={"semestre": 9999}, headers=h)
    assert r.status_code == 404
    assert r.json() == {"detail": "El semestre no existe"}


def test_semestre_inexistente_da_404_aunque_no_haya_semestres(client, h):
    assert client.get(RUTA, params={"semestre": 1}, headers=h).status_code == 404


def test_semestre_que_no_es_numero_da_422(client, h):
    assert client.get(RUTA, params={"semestre": "abc"}, headers=h).status_code == 422
