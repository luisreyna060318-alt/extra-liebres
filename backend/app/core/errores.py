"""Errores de negocio.

Los servicios (la capa de lógica) lanzan estos errores y no saben nada de HTTP. En main.py hay un manejador
que los convierte en una respuesta JSON con el código correcto: {"detail": "mensaje"}.
Así todas las respuestas de error de la API tienen la misma forma.
"""


class ErrorNegocio(Exception):
    status_code = 400

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoAutenticado(ErrorNegocio):
    """401: no hay sesión válida (o los datos de acceso son incorrectos)."""

    status_code = 401


class SinPermiso(ErrorNegocio):
    """403: hay sesión, pero el rol no alcanza para esta acción."""

    status_code = 403


class NoEncontrado(ErrorNegocio):
    """404: lo que se pidió no existe."""

    status_code = 404


class Conflicto(ErrorNegocio):
    """409: la acción choca con algo existente (duplicado, cruce de horario, registro referenciado...)."""

    status_code = 409
