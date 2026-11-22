from pydantic import BaseModel


class Token(BaseModel):
    """Respuesta del inicio de sesión: el JWT que el cliente manda en cada petición (Authorization: Bearer ...)."""

    access_token: str
    token_type: str = "bearer"
