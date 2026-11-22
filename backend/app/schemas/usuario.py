"""Esquemas de usuarios. Los de entrada y los de salida son distintos a propósito:
la salida nunca incluye password_hash."""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.core.constantes import ROLES
from app.core.security import MAX_BYTES_PASSWORD


class UsuarioRegistro(BaseModel):
    """Datos para crear una cuenta (HU-01.1). El rol NO se pide: siempre nace como capturista."""

    nombre: str = Field(min_length=2, max_length=100, examples=["Ana López"])
    correo: EmailStr = Field(examples=["ana@correo.com"])
    password: str = Field(min_length=8, examples=["Clave1234"], description="Mínimo 8 caracteres, con letras y números")

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v

    @field_validator("correo")
    @classmethod
    def correo_en_minusculas(cls, v: str) -> str:
        # Se guarda siempre en minúsculas para que Ana@x.com y ana@x.com sean la misma cuenta
        if len(v) > 120:
            raise ValueError("El correo no puede pasar de 120 caracteres")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("La contraseña debe combinar letras y números")
        if len(v.encode("utf-8")) > MAX_BYTES_PASSWORD:
            raise ValueError(f"La contraseña no puede pasar de {MAX_BYTES_PASSWORD} bytes")
        return v


class UsuarioSalida(BaseModel):
    """Lo que la API devuelve de un usuario (nunca la contraseña ni su hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    rol: str
    activo: bool
    creado_en: datetime


class UsuarioActualizar(BaseModel):
    """Cambios que puede hacer un administrador sobre otra cuenta (HU-01.4): rol y/o suspensión."""

    rol: str | None = Field(default=None, description="administrador o capturista")
    activo: bool | None = Field(default=None, description="false suspende la cuenta; true la reactiva")

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str | None) -> str | None:
        if v is not None and v not in ROLES:
            raise ValueError(f"El rol debe ser uno de: {', '.join(ROLES)}")
        return v

    @model_validator(mode="after")
    def al_menos_un_cambio(self) -> "UsuarioActualizar":
        if self.rol is None and self.activo is None:
            raise ValueError("Indica al menos un cambio: rol o activo")
        return self
