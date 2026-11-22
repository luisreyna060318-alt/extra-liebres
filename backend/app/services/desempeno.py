"""Cálculo del desempeño a partir de la calificación (RN-05)."""

# (calificación mínima, desempeño), de mayor a menor. Escala del TecNM.
ESCALA = (
    (95, "Excelente"),
    (85, "Notable"),
    (75, "Bueno"),
    (70, "Suficiente"),
)
DESEMPENO_MINIMO = "Insuficiente"  # menos de 70


def calcular_desempenio(calificacion: int) -> str:
    """Devuelve el desempeño que corresponde a una calificación entera de 0 a 100.

    Ejemplos: 100 -> "Excelente", 94 -> "Notable", 70 -> "Suficiente", 69 -> "Insuficiente".
    Es una función pura (no usa la base de datos), por eso se prueba fácilmente.
    """
    # bool es subclase de int en Python (True == 1), por eso se descarta aparte
    if isinstance(calificacion, bool) or not isinstance(calificacion, int):
        raise TypeError("La calificación debe ser un número entero")
    if not 0 <= calificacion <= 100:
        raise ValueError("La calificación debe estar entre 0 y 100")
    for minimo, desempenio in ESCALA:
        if calificacion >= minimo:
            return desempenio
    return DESEMPENO_MINIMO
