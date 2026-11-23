"""Datos semilla con información FICTICIA (nombres, números de control y RFC inventados).

Uso, desde la raíz del repositorio y con la base de datos ya migrada:
    python db/seed.py

Se puede ejecutar varias veces: si una tabla ya tiene datos, se omite. Los datos son siempre los mismos
(la semilla aleatoria está fija), así que todos ven lo mismo en la demo.
"""

import random
import string
import sys
from datetime import time
from pathlib import Path

# Para poder importar "app" (que vive en backend/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import func, select  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.constantes import CARRERAS  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import (  # noqa: E402
    Alumno,
    AlumnoGrupo,
    Extraescolar,
    Grupo,
    Promotor,
    Semestre,
    Usuario,
)
from app.services.desempeno import calcular_desempenio  # noqa: E402

random.seed(2026)

NOMBRES_H = ["Juan", "Luis", "Carlos", "Miguel", "José", "Diego", "Jorge", "Pedro", "Andrés", "Raúl",
             "Daniel", "Fernando", "Ricardo", "Eduardo", "Mario", "Sergio", "Iván", "Héctor", "Óscar", "Tomás"]
NOMBRES_M = ["María", "Ana", "Laura", "Sofía", "Daniela", "Fernanda", "Valeria", "Karla", "Paola", "Andrea",
             "Gabriela", "Mariana", "Carmen", "Alejandra", "Lucía", "Diana", "Rosa", "Elena", "Jimena", "Renata"]
APELLIDOS = ["García", "Martínez", "López", "Hernández", "González", "Pérez", "Rodríguez", "Sánchez",
             "Ramírez", "Flores", "Torres", "Rivera", "Gómez", "Díaz", "Cruz", "Morales", "Reyes", "Ortiz",
             "Gutiérrez", "Chávez", "Ruiz", "Mendoza", "Aguilar", "Castillo", "Vargas", "Medina", "Herrera",
             "Jiménez", "Navarro", "Ramos"]
CAMPUS = ["Campus I", "Campus II"]
ACTIVIDADES = [  # (nombre, tipo, al aire libre)
    ("Fútbol", "deportiva", True), ("Básquetbol", "deportiva", True), ("Voleibol", "deportiva", True),
    ("Atletismo", "deportiva", True), ("Ajedrez", "cultural", False), ("Danza folclórica", "cultural", False),
    ("Rondalla", "cultural", False), ("Escolta y banda de guerra", "civica", True),
]
AULAS = ["Aula A-101", "Aula A-102", "Auditorio", "Sala de usos múltiples", "Salón de danza"]
# Dónde se imparte cada actividad (las que no están aquí usan AULAS)
LUGARES = {
    "Fútbol": ["Cancha de fútbol"],
    "Básquetbol": ["Cancha de básquetbol", "Gimnasio"],
    "Voleibol": ["Cancha de voleibol", "Gimnasio"],
    "Atletismo": ["Pista de atletismo"],
    "Escolta y banda de guerra": ["Explanada cívica"],
}
SEMESTRES = [(2024, 1, 6), (2024, 8, 12), (2025, 1, 6), (2025, 8, 12), (2026, 1, 6), (2026, 8, 12)]
DIAS_SEMANA = ["lunes", "martes", "miercoles", "jueves", "viernes"]


def tabla_vacia(db, modelo) -> bool:
    return db.scalar(select(func.count()).select_from(modelo)) == 0


def rfc_falso() -> str:
    """RFC inventado de 13 caracteres: 4 letras, 6 dígitos y 3 caracteres."""
    letras = "".join(random.choices(string.ascii_uppercase, k=4))
    digitos = "".join(random.choices(string.digits, k=6))
    clave = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return letras + digitos + clave


def se_traslapan(inicio1, fin1, inicio2, fin2) -> bool:
    """Dos horarios se traslapan si cada uno empieza antes de que el otro termine."""
    return inicio1 < fin2 and inicio2 < fin1


def sembrar_usuarios(db) -> None:
    pruebas = [
        ("Administrador de prueba", settings.seed_admin_correo, settings.seed_admin_password, "administrador"),
        ("Capturista de prueba", settings.seed_capturista_correo, settings.seed_capturista_password, "capturista"),
        ("Lector de prueba", settings.seed_lector_correo, settings.seed_lector_password, "lector"),
    ]
    for nombre, correo, password, rol in pruebas:
        if not correo or not password:
            print(f"  Usuarios: faltan SEED_*_CORREO/PASSWORD en .env, se omite el rol {rol}")
            continue
        if settings.entorno == "produccion" and password.startswith("cambia-"):
            raise SystemExit(f"En producción no se crea el usuario {rol} con la contraseña de ejemplo: define la tuya")
        correo = correo.strip().lower()  # el correo se guarda siempre en minúsculas
        if db.scalar(select(Usuario).where(Usuario.correo == correo)):
            print(f"  Usuarios: {rol} ya existe, se omite")
            continue
        db.add(Usuario(nombre=nombre, correo=correo, password_hash=hash_password(password), rol=rol))
        print(f"  Usuarios: creado {rol} ({correo})")


def sembrar_catalogos(db) -> None:
    if tabla_vacia(db, Promotor):
        usados: set[str] = set()
        for _ in range(10):
            rfc = rfc_falso()
            while rfc in usados:
                rfc = rfc_falso()
            usados.add(rfc)
            nombre = random.choice(NOMBRES_H + NOMBRES_M)
            db.add(Promotor(rfc=rfc, nombre=nombre, apaterno=random.choice(APELLIDOS),
                            amaterno=random.choice(APELLIDOS)))
    if tabla_vacia(db, Extraescolar):
        for nombre, tipo, aire_libre in ACTIVIDADES:
            db.add(Extraescolar(nombreextra=nombre, tipo=tipo, al_aire_libre=aire_libre))
    if tabla_vacia(db, Semestre):
        for anio, mes_inicio, mes_termino in SEMESTRES:
            db.add(Semestre(anio=anio, mesinicio=mes_inicio, mestermino=mes_termino))
    db.flush()  # asigna los ids para poder usarlos abajo


def sembrar_alumnos(db) -> None:
    if not tabla_vacia(db, Alumno):
        return
    for numero in range(1, 201):
        # 8 dígitos, todos distintos y por debajo del máximo (26999999): 26000001, 26000002, ...
        nocontrol = f"26{numero:06d}"
        sexo = random.choice(["M", "F"])
        nombres = NOMBRES_H if sexo == "M" else NOMBRES_M
        db.add(Alumno(
            nocontrol=nocontrol, nombre=random.choice(nombres), apaterno=random.choice(APELLIDOS),
            amaterno=random.choice(APELLIDOS) if random.random() > 0.03 else None,
            sexo=sexo, carrera=random.choice(CARRERAS), campus=random.choice(CAMPUS),
            activo=random.random() > 0.05,  # ~5% de alumnos dados de baja
        ))
    db.flush()


def sembrar_grupos_e_inscripciones(db) -> None:
    if not tabla_vacia(db, Grupo):
        return
    promotores = list(db.scalars(select(Promotor)))
    actividades = list(db.scalars(select(Extraescolar)))
    semestres = list(db.scalars(select(Semestre).order_by(Semestre.anio, Semestre.mesinicio)))
    alumnos = list(db.scalars(select(Alumno)))
    activos = [a for a in alumnos if a.activo]
    if len(promotores) < 1 or len(actividades) < 7 or not semestres or len(activos) < 18:
        print("  Grupos: faltan catálogos o alumnos (se necesitan 7+ actividades y 18+ alumnos activos); se omiten")
        return
    ultimo_semestre = semestres[-1]

    for semestre in semestres:
        grupos_del_semestre: list[Grupo] = []
        for actividad in random.sample(actividades, 7):  # 7 grupos por semestre = 42 en total
            for _ in range(300):  # reintenta hasta encontrar un horario sin cruces (RN-03)
                inicio = time(random.randint(8, 17))
                fin = time(inicio.hour + random.choice([1, 2]))
                dia = random.choice(DIAS_SEMANA)
                promotor = random.choice(promotores)
                lugar = random.choice(LUGARES.get(actividad.nombreextra, AULAS))
                cruce = any(
                    g.dia == dia and (g.rfcpromotor == promotor.rfc or g.aula == lugar)
                    and se_traslapan(inicio, fin, g.horainicio, g.horatermino)
                    for g in grupos_del_semestre
                )
                if not cruce:
                    break
            else:
                raise RuntimeError("No se encontró un horario sin cruces; cambia la semilla")
            grupo = Grupo(dia=dia, horainicio=inicio, horatermino=fin, aula=lugar,
                          idsemestre=semestre.idsemestre, idextraescolar=actividad.idextraescolar,
                          rfcpromotor=promotor.rfc)
            db.add(grupo)
            grupos_del_semestre.append(grupo)
        db.flush()

        for grupo in grupos_del_semestre:
            candidatos = activos if semestre is ultimo_semestre else alumnos
            for alumno in random.sample(candidatos, random.randint(12, 18)):
                calificacion = desempenio = None
                # En el semestre en curso solo se ha evaluado a una parte de los alumnos
                if semestre is not ultimo_semestre or random.random() < 0.4:
                    calificacion = max(0, min(100, round(random.gauss(86, 9))))
                    desempenio = calcular_desempenio(calificacion)
                db.add(AlumnoGrupo(nocontrol=alumno.nocontrol, idgrupo=grupo.idgrupo,
                                   calificacion=calificacion, desempenio=desempenio))
        db.flush()


def main() -> None:
    with SessionLocal() as db:
        sembrar_usuarios(db)
        sembrar_catalogos(db)
        sembrar_alumnos(db)
        sembrar_grupos_e_inscripciones(db)
        db.commit()

        print("Resumen de la base de datos:")
        for modelo in (Usuario, Alumno, Promotor, Extraescolar, Semestre, Grupo, AlumnoGrupo):
            total = db.scalar(select(func.count()).select_from(modelo))
            print(f"  {modelo.__tablename__:<14} {total}")


if __name__ == "__main__":
    main()
