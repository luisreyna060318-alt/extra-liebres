"""Genera los diagramas del proyecto. Solo usa la biblioteca estándar de Python (no agrega dependencias).

    python docs/diagramas/generar.py             # SVG + PNG de los dos diagramas
    python docs/diagramas/generar.py --solo-svg  # solo los SVG (no necesita navegador)

Qué hace:
  1. Lee la migración de Alembic (db/migrations/versions/) con el módulo `ast`, sin ejecutarla, y saca de ahí
     las tablas, columnas, llaves y restricciones. Con eso dibuja docs/diagramas/er.svg.
  2. docs/diagramas/arquitectura.svg está escrito a mano (es la fuente editable de ese diagrama).
  3. Convierte los dos SVG a PNG con Microsoft Edge o Google Chrome en modo "headless" (sin ventana).
     Resultado: docs/arquitectura.png y db/er.png.

Si tu navegador está en otra ruta, define la variable de entorno NAVEGADOR con la ruta del ejecutable.
"""

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = Path(__file__).resolve().parent
MIGRACIONES = RAIZ / "db" / "migrations" / "versions"

# ---------------------------------------------------------------------------
# 1. Leer la migración
# ---------------------------------------------------------------------------

# Cómo se escribe cada tipo de SQLAlchemy en PostgreSQL
TIPOS_SQL = {
    "Integer": "INTEGER",
    "Boolean": "BOOLEAN",
    "Time": "TIME",
    "DateTime": "TIMESTAMPTZ",
}


def valor(nodo):
    """Valor de un nodo del código: un literal, o el primer argumento de op.f('nombre') / sa.text('x')."""
    if isinstance(nodo, ast.Call) and nodo.args:
        return valor(nodo.args[0])
    return ast.literal_eval(nodo)


def tipo_sql(nodo) -> str:
    """sa.String(length=15) -> VARCHAR(15); sa.Integer() -> INTEGER."""
    nombre = nodo.func.attr
    if nombre == "String":
        return f"VARCHAR({valor(nodo.keywords[0].value)})"
    return TIPOS_SQL[nombre]


def leer_tablas() -> dict:
    """Devuelve {tabla: {columnas, pk, fks, checks, uniques}} a partir de las llamadas op.create_table(...)."""
    archivos = sorted(MIGRACIONES.glob("*.py"))
    if len(archivos) > 1:
        print("Aviso: hay varias migraciones; solo se leen las llamadas create_table (no los ALTER).")
    tablas = {}
    for archivo in archivos:
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            es_create = (
                isinstance(nodo, ast.Call)
                and isinstance(nodo.func, ast.Attribute)
                and nodo.func.attr == "create_table"
            )
            if es_create:
                tablas[valor(nodo.args[0])] = leer_tabla(nodo.args[1:])
    return tablas


def leer_tabla(elementos) -> dict:
    tabla = {"columnas": [], "pk": [], "fks": {}, "checks": [], "uniques": []}
    for e in elementos:
        tipo = e.func.attr
        if tipo == "Column":
            opciones = {k.arg: k.value for k in e.keywords}
            tabla["columnas"].append(
                {
                    "nombre": valor(e.args[0]),
                    "tipo": tipo_sql(e.args[1]),
                    "nulo": valor(opciones["nullable"]),
                }
            )
        elif tipo == "PrimaryKeyConstraint":
            tabla["pk"] = [valor(a) for a in e.args]
        elif tipo == "ForeignKeyConstraint":
            columnas = valor(e.args[0])
            destinos = valor(e.args[1])
            for col, destino in zip(columnas, destinos):
                tabla["fks"][col] = destino  # por ejemplo "promotor.rfc"
        elif tipo == "CheckConstraint":
            tabla["checks"].append(valor(e.args[0]))
        elif tipo == "UniqueConstraint":
            tabla["uniques"].append([valor(a) for a in e.args])
    return tabla


def ondelete_usados() -> set:
    """Los valores de ondelete que aparecen en las llaves foráneas de la migración."""
    usados = set()
    for archivo in MIGRACIONES.glob("*.py"):
        usados |= set(re.findall(r"ondelete='(\w+)'", archivo.read_text(encoding="utf-8")))
    return usados


# ---------------------------------------------------------------------------
# 2. Dibujar el diagrama entidad-relación (SVG)
# ---------------------------------------------------------------------------

ANCHO_ER, ALTO_ER = 2000, 1280
ALTO_TITULO, ALTO_FILA, ALTO_RESTR = 50, 30, 22

# Posición (x, y) y ancho de cada tabla. Las tres de arriba son los catálogos que apuntan a grupo.
DISPOSICION = {
    "promotor": (60, 130, 480),
    "extraescolar": (740, 130, 480),
    "semestre": (1420, 130, 480),
    "usuario": (60, 520, 540),
    "grupo": (740, 520, 480),
    "alumno_grupo": (1420, 520, 480),
    "alumno": (1420, 900, 480),
}


def lineas_restricciones(tabla: dict, ancho: int) -> list:
    """Texto de los CHECK y UNIQUE, partido en renglones que quepan en la caja."""
    letras = int((ancho - 28) / 7.6)
    textos = [f"CHECK {c}" for c in tabla["checks"]]
    textos += [f"UNIQUE ({', '.join(u)})" for u in tabla["uniques"] if len(u) > 1]
    renglones = []
    for t in textos:
        renglones += textwrap.wrap(t, letras, subsequent_indent="    ")
    return renglones


def marcas(tabla: dict, columna: str) -> str:
    """PK, FK y UQ de una columna (una columna puede ser PK y FK a la vez)."""
    m = []
    if columna in tabla["pk"]:
        m.append("PK")
    if columna in tabla["fks"]:
        m.append("FK")
    if any(u == [columna] for u in tabla["uniques"]):
        m.append("UQ")
    return " ".join(m)


def caja_tabla(nombre: str, tabla: dict, x: int, y: int, ancho: int):
    """SVG de una tabla. Devuelve (svg, alto)."""
    restr = lineas_restricciones(tabla, ancho)
    alto = ALTO_TITULO + len(tabla["columnas"]) * ALTO_FILA + 14
    if restr:
        alto += 12 + len(restr) * ALTO_RESTR
    s = [f'<rect class="tabla" x="{x}" y="{y}" width="{ancho}" height="{alto}" rx="10"/>']
    s.append(f'<path class="cab" d="M{x},{y + ALTO_TITULO} V{y + 10} Q{x},{y} {x + 10},{y} H{x + ancho - 10} '
             f'Q{x + ancho},{y} {x + ancho},{y + 10} V{y + ALTO_TITULO} Z"/>')
    s.append(f'<text class="nombre" x="{x + 16}" y="{y + 33}">{escape(nombre)}</text>')
    fila_y = y + ALTO_TITULO
    for col in tabla["columnas"]:
        base = fila_y + 21
        m = marcas(tabla, col["nombre"])
        if m:
            s.append(f'<text class="marca" x="{x + 14}" y="{base}">{m}</text>')
        peso = ' class="col pk"' if col["nombre"] in tabla["pk"] else ' class="col"'
        s.append(f'<text{peso} x="{x + 80}" y="{base}">{escape(col["nombre"])}</text>')
        s.append(f'<text class="tipo" x="{x + int(ancho * 0.58)}" y="{base}">{escape(col["tipo"])}</text>')
        if col["nulo"]:
            s.append(f'<text class="nulo" x="{x + ancho - 14}" y="{base}" text-anchor="end">NULL</text>')
        fila_y += ALTO_FILA
    if restr:
        linea_y = fila_y + 4
        s.append(f'<line class="sep" x1="{x}" y1="{linea_y}" x2="{x + ancho}" y2="{linea_y}"/>')
        ry = linea_y + 26
        for r in restr:
            s.append(f'<text class="restr" xml:space="preserve" x="{x + 14}" y="{ry}">{escape(r)}</text>')
            ry += ALTO_RESTR
    return "\n".join(s), alto


def generar_er(tablas: dict) -> str:
    cajas = {}
    svg_cajas = []
    for nombre, (x, y, ancho) in DISPOSICION.items():
        svg, alto = caja_tabla(nombre, tablas[nombre], x, y, ancho)
        cajas[nombre] = (x, y, ancho, alto)
        svg_cajas.append(svg)

    def borde(nombre, lado):
        x, y, w, h = cajas[nombre]
        return {"arriba": y, "abajo": y + h, "izq": x, "der": x + w}[lado]

    lineas = []

    def linea(d, etiqueta=None, ex=0, ey=0, ancla="middle"):
        lineas.append(f'<path class="rel" d="{d}"/>')
        if etiqueta:
            lineas.append(f'<text class="etq" x="{ex}" y="{ey}" text-anchor="{ancla}">{escape(etiqueta)}</text>')

    def uno_n(texto, x, y, ancla="middle"):
        lineas.append(f'<text class="card" x="{x}" y="{y}" text-anchor="{ancla}">{texto}</text>')

    # Cada FK de grupo hacia su catálogo (1:N). La línea lleva el nombre de la columna FK de grupo.
    fila_baja = max(borde(t, "abajo") for t in ("promotor", "extraescolar", "semestre"))
    medio = fila_baja + 45  # altura de los tramos horizontales
    arriba_grupo = borde("grupo", "arriba")
    gx, _, gw, _ = cajas["grupo"]

    destinos = {"rfcpromotor": ("promotor", gx + 70), "idextraescolar": ("extraescolar", gx + gw // 2),
                "idsemestre": ("semestre", gx + gw - 70)}
    for col, (padre, x_destino) in destinos.items():
        px, _, pw, _ = cajas[padre]
        x_origen = px + pw // 2
        abajo = borde(padre, "abajo")
        rotulo = col
        if x_origen == x_destino:
            linea(f"M{x_origen},{abajo} V{arriba_grupo}", rotulo, x_origen + 12, (medio + arriba_grupo) // 2, "start")
        else:
            linea(f"M{x_origen},{abajo} V{medio} H{x_destino} V{arriba_grupo}", rotulo,
                  (x_origen + x_destino) // 2, medio - 10)
        uno_n("1", x_origen + 14 if x_origen != x_destino else x_origen - 14, abajo + 24,
              "start" if x_origen != x_destino else "end")
        uno_n("N", x_destino + 14 if x_origen != x_destino else x_destino - 14, arriba_grupo - 10,
              "start" if x_origen != x_destino else "end")

    # alumno_grupo -> grupo (horizontal) y alumno_grupo -> alumno (vertical): la relación N:M
    ag_fks = tablas["alumno_grupo"]["fks"]
    yh = borde("grupo", "arriba") + 90
    x_g_der, x_ag_izq = borde("grupo", "der"), borde("alumno_grupo", "izq")
    linea(f"M{x_g_der},{yh} H{x_ag_izq}", "idgrupo", (x_g_der + x_ag_izq) // 2, yh - 12)
    uno_n("1", x_g_der + 16, yh - 10, "start")
    uno_n("N", x_ag_izq - 16, yh - 10, "end")
    lineas.append(f'<text class="etq" x="{(x_g_der + x_ag_izq) // 2}" y="{yh + 24}" text-anchor="middle">'
                  f'→ {escape(ag_fks["idgrupo"])}</text>')

    agx, _, agw, _ = cajas["alumno_grupo"]
    xv = agx + agw // 2
    y_ag_abajo, y_al_arriba = borde("alumno_grupo", "abajo"), borde("alumno", "arriba")
    linea(f"M{xv},{y_ag_abajo} V{y_al_arriba}", f"nocontrol → {ag_fks['nocontrol']}", xv + 14,
          (y_ag_abajo + y_al_arriba) // 2 + 5, "start")
    uno_n("N", xv - 14, y_ag_abajo + 28, "end")
    uno_n("1", xv - 14, y_al_arriba - 10, "end")
    # Aviso de la relación muchos a muchos, a la izquierda de la línea vertical
    cy = (y_ag_abajo + y_al_arriba) // 2
    for i, t in enumerate(["Relación N:M", "alumno ↔ grupo, resuelta", "por la tabla alumno_grupo"]):
        clase = "nm" if i == 0 else "nm2"
        lineas.append(f'<text class="{clase}" x="{xv - 60}" y="{cy - 14 + i * 22}" text-anchor="end">{t}</text>')

    # Recuadro de notas
    nx, ny, nw = 740, 920, 560
    usados = ", ".join(sorted(ondelete_usados())) or "ninguno"
    notas = [
        ("PK llave primaria · FK llave foránea · UQ valor único", False),
        ("Las columnas sin la marca NULL son obligatorias (NOT NULL).", False),
        ("1 —— N  relación uno a muchos: la N es la tabla que tiene la FK.", False),
        (f"Todas las FK usan ON DELETE {usados}: no se puede borrar", False),
        ("un catálogo, alumno ni grupo que ya tenga registros (RN-08).", False),
        ("alumno_grupo: su PK es compuesta (nocontrol, idgrupo), así un", False),
        ("alumno no se inscribe dos veces al mismo grupo.", False),
        ("usuario no se relaciona con las demás tablas: son las cuentas", False),
        ("de acceso (correo único, rol administrador o capturista).", False),
    ]
    alto_notas = 56 + len(notas) * 24
    leyenda = [f'<rect class="notas" x="{nx}" y="{ny}" width="{nw}" height="{alto_notas}" rx="10"/>',
               f'<text class="nombre2" x="{nx + 16}" y="{ny + 34}">Cómo leer el diagrama</text>']
    for i, (t, _) in enumerate(notas):
        leyenda.append(f'<text class="nota" x="{nx + 16}" y="{ny + 64 + i * 24}">{escape(t)}</text>')

    estilos = """
      .tabla { fill: #ffffff; stroke: #1f2937; stroke-width: 2.5; }
      .cab { fill: #dbeafe; stroke: #1f2937; stroke-width: 2.5; }
      .notas { fill: #f9fafb; stroke: #6b7280; stroke-width: 1.5; stroke-dasharray: 6 4; }
      .sep { stroke: #9ca3af; stroke-width: 1.5; }
      .rel { stroke: #1f2937; stroke-width: 2.5; fill: none; }
      .titulo { font-size: 36px; font-weight: 700; fill: #111827; }
      .sub { font-size: 19px; fill: #374151; }
      .nombre { font-size: 24px; font-weight: 700; fill: #111827; font-family: Consolas, 'Courier New', monospace; }
      .nombre2 { font-size: 20px; font-weight: 700; fill: #111827; }
      .col { font-size: 18px; fill: #111827; font-family: Consolas, 'Courier New', monospace; }
      .pk { font-weight: 700; }
      .marca { font-size: 14px; font-weight: 700; fill: #1d4ed8; }
      .tipo { font-size: 17px; fill: #4b5563; font-family: Consolas, 'Courier New', monospace; }
      .nulo { font-size: 14px; fill: #92400e; font-weight: 700; }
      .restr { font-size: 14px; fill: #7c2d12; font-family: Consolas, 'Courier New', monospace; }
      .etq { font-size: 15px; fill: #111827; font-family: Consolas, 'Courier New', monospace; }
      .card { font-size: 22px; font-weight: 700; fill: #b91c1c; }
      .nm { font-size: 19px; font-weight: 700; fill: #6d28d9; }
      .nm2 { font-size: 16px; fill: #6d28d9; }
      .nota { font-size: 16px; fill: #1f2937; }
    """
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO_ER}" height="{ALTO_ER}" '
            f'viewBox="0 0 {ANCHO_ER} {ALTO_ER}" font-family="Segoe UI, Arial, sans-serif">',
            "<title>Modelo entidad-relación de Extra-Liebres</title>",
            "<desc>Siete tablas de PostgreSQL con sus columnas, llaves y restricciones, "
            "generadas desde la migración de Alembic.</desc>",
            f"<style>{estilos}</style>",
            f'<rect width="{ANCHO_ER}" height="{ALTO_ER}" fill="#ffffff"/>',
            '<text class="titulo" x="40" y="55">Extra-Liebres · Modelo entidad-relación</text>',
            '<text class="sub" x="40" y="90">PostgreSQL · 7 tablas · generado desde '
            "db/migrations/versions/20261121_0001_esquema_inicial.py</text>",
            *lineas,
            *svg_cajas,
            *leyenda,
            "</svg>",
        ]
    )


# ---------------------------------------------------------------------------
# 3. SVG -> PNG con Edge o Chrome sin ventana
# ---------------------------------------------------------------------------

def buscar_navegador() -> str:
    candidatos = [
        os.environ.get("NAVEGADOR", ""),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("msedge") or "",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
    ]
    for c in candidatos:
        if c and Path(c).exists():
            return c
    sys.exit("No encontré Edge ni Chrome. Define NAVEGADOR con la ruta del ejecutable.")


def svg_a_png(svg: Path, png: Path) -> None:
    texto = svg.read_text(encoding="utf-8")
    ancho = int(re.search(r'<svg[^>]*\swidth="(\d+)"', texto).group(1))
    alto = int(re.search(r'<svg[^>]*\sheight="(\d+)"', texto).group(1))
    png.parent.mkdir(parents=True, exist_ok=True)
    # perfil temporal: no choca con un navegador ya abierto. En Windows Edge puede dejar archivos en uso al cerrar
    # y borrar la carpeta fallaba al final, aunque la imagen ya estuviera guardada (por eso se ignoran esos errores)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as perfil:
        subprocess.run(
            [
                buscar_navegador(),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--user-data-dir={perfil}",
                f"--window-size={ancho},{alto}",
                f"--screenshot={png}",
                svg.resolve().as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
    print(f"{png.relative_to(RAIZ)}  ({ancho} x {alto})")


def main() -> None:
    er_svg = CARPETA / "er.svg"
    er_svg.write_text(generar_er(leer_tablas()), encoding="utf-8")
    print(er_svg.relative_to(RAIZ))
    if "--solo-svg" in sys.argv:
        return
    svg_a_png(CARPETA / "arquitectura.svg", RAIZ / "docs" / "arquitectura.png")
    svg_a_png(er_svg, RAIZ / "db" / "er.png")


if __name__ == "__main__":
    main()
