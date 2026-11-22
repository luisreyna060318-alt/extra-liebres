# Exportación de inscritos (HU-07.2)

Solo el **administrador** puede exportar. Se hace desde la pantalla **Consultas** (botones *Exportar CSV* y *Exportar XML*)
o llamando a la API con sesión de administrador. La exportación trae **todos** los inscritos que cumplen los filtros
(no solo la página que se ve) y respeta los mismos filtros de la consulta:

| Parámetro | Qué filtra |
|---|---|
| `extraescolar` | id de la actividad |
| `semestre` | id del semestre |

```
GET /api/export/inscritos.csv?semestre=1
GET /api/export/inscritos.xml?extraescolar=2&semestre=1
```

Sin sesión responde `401`; con sesión de capturista, `403`.

## Columnas

Los datos salen de la misma consulta que `GET /api/consultas/inscritos`, ordenados por semestre (el más reciente primero),
actividad, grupo y apellidos.

| Campo (XML) | Título (CSV) | Ejemplo |
|---|---|---|
| `nocontrol` | No. de control | 26000046 |
| `alumno` | Alumno | Díaz Gutiérrez Mariana |
| `carrera` | Carrera | ING. MECATRÓNICA |
| `actividad` | Actividad | Ajedrez |
| `semestre` | Semestre | Enero-Junio 2024 |
| `idgrupo` | Grupo | 3 |
| `promotor` | Promotor | Carmen Ruiz López |
| `calificacion` | Calificación | 79 (vacío si aún no se evalúa) |
| `desempenio` | Desempeño | Bueno (vacío si aún no se evalúa) |

## CSV

- Codificación UTF-8 **con BOM**, comas y saltos de línea de Windows (`\r\n`): Excel lo abre con los acentos correctos.
- La primera fila trae los títulos. Si no hay inscritos, el archivo solo trae esa fila.
- Un texto que empieza con `=`, `+`, `-` o `@` se escribe con una comilla al inicio, para que la hoja de cálculo no lo
  ejecute como fórmula.

## XML

XML bien formado en UTF-8, con un elemento `<inscrito>` por renglón y el total como atributo de la raíz:

```xml
<?xml version='1.0' encoding='utf-8'?>
<inscritos total="2">
  <inscrito>
    <nocontrol>26000046</nocontrol>
    <alumno>Díaz Gutiérrez Mariana</alumno>
    <carrera>ING. MECATRÓNICA</carrera>
    <actividad>Ajedrez</actividad>
    <semestre>Enero-Junio 2024</semestre>
    <idgrupo>3</idgrupo>
    <promotor>Carmen Ruiz López</promotor>
    <calificacion>79</calificacion>
    <desempenio>Bueno</desempenio>
  </inscrito>
  <inscrito>
    <nocontrol>26000047</nocontrol>
    <alumno>Pérez Soto Luis</alumno>
    <carrera>ING. INDUSTRIAL</carrera>
    <actividad>Ajedrez</actividad>
    <semestre>Enero-Junio 2024</semestre>
    <idgrupo>3</idgrupo>
    <promotor>Carmen Ruiz López</promotor>
    <calificacion />
    <desempenio />
  </inscrito>
</inscritos>
```

Los caracteres especiales (`<`, `>`, `&`) se escapan solos. Los datos del ejemplo son ficticios.

## Cómo se comprobó

- `backend/tests/test_exportar.py`: 8 pruebas (permisos, encabezados, filtros, renglones sin evaluar, fórmulas en el CSV,
  XML bien formado y caracteres especiales).
- Descarga real desde el navegador contra el sistema en Docker: el CSV y el XML traen los mismos renglones.
- El CSV se abrió en Microsoft Excel: 9 columnas, encabezados y acentos correctos.
