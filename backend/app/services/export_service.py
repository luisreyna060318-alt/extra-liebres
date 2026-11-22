"""Exportación de los inscritos (HU-07.2) a CSV y a XML. Solo genera texto; no consulta la base."""

import csv
import io
import xml.etree.ElementTree as ET

from app.schemas.consulta import InscritoConsulta

# (campo del esquema, título de la columna en el CSV)
COLUMNAS = [
    ("nocontrol", "No. de control"),
    ("alumno", "Alumno"),
    ("carrera", "Carrera"),
    ("actividad", "Actividad"),
    ("semestre", "Semestre"),
    ("idgrupo", "Grupo"),
    ("promotor", "Promotor"),
    ("calificacion", "Calificación"),
    ("desempenio", "Desempeño"),
]


def _celda(valor) -> str:
    """Texto de una celda. Si empieza con =, +, - o @, Excel lo tomaría como fórmula: se le antepone una comilla."""
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto[:1] in ("=", "+", "-", "@") else texto


def a_csv(filas: list[InscritoConsulta]) -> str:
    """CSV con comas y saltos de línea de Windows. Empieza con BOM para que Excel respete los acentos."""
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\r\n")
    escritor.writerow([titulo for _, titulo in COLUMNAS])
    for fila in filas:
        escritor.writerow([_celda(getattr(fila, campo)) for campo, _ in COLUMNAS])
    return "\ufeff" + salida.getvalue()


def a_xml(filas: list[InscritoConsulta]) -> bytes:
    """XML bien formado: <inscritos total="N"> con un <inscrito> por renglón. ElementTree escapa <, > y &."""
    raiz = ET.Element("inscritos", total=str(len(filas)))
    for fila in filas:
        inscrito = ET.SubElement(raiz, "inscrito")
        for campo, _ in COLUMNAS:
            valor = getattr(fila, campo)
            ET.SubElement(inscrito, campo).text = "" if valor is None else str(valor)
    ET.indent(raiz)  # sangría para que sea legible
    return ET.tostring(raiz, encoding="utf-8", xml_declaration=True)
