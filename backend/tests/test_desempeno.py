import pytest

from app.services.desempeno import calcular_desempenio


@pytest.mark.parametrize(
    ("calificacion", "esperado"),
    [
        (100, "Excelente"),
        (95, "Excelente"),
        (94, "Notable"),
        (85, "Notable"),
        (84, "Bueno"),
        (75, "Bueno"),
        (74, "Suficiente"),
        (70, "Suficiente"),
        (69, "Insuficiente"),
        (0, "Insuficiente"),
    ],
)
def test_desempeno_en_los_bordes_de_la_escala(calificacion, esperado):
    assert calcular_desempenio(calificacion) == esperado


@pytest.mark.parametrize("calificacion", [-1, 101])
def test_desempeno_rechaza_calificaciones_fuera_de_rango(calificacion):
    with pytest.raises(ValueError):
        calcular_desempenio(calificacion)


@pytest.mark.parametrize("calificacion", [94.9, True, "90", None])
def test_desempeno_rechaza_valores_que_no_son_enteros(calificacion):
    # RN-05: la calificación es un entero; un decimal o un booleano no deben "colarse"
    with pytest.raises(TypeError):
        calcular_desempenio(calificacion)
