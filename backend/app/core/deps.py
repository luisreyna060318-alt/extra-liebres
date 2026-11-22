"""Dependencias de FastAPI para proteger las rutas (inyección de dependencias).

Uso en una ruta:
    UsuarioActual                          -> exige sesión (401 si no hay)
    dependencies=[Depends(require_role("administrador"))]   -> exige además ese rol (403 si no)
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errores import SinPermiso
from app.core.security import leer_token
from app.models import Usuario

# tokenUrl hace que el botón "Authorize" de /docs sepa dónde iniciar sesión
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SesionDB = Annotated[Session, Depends(get_db)]


def _no_autenticado(detalle: str = "Sesión inválida o expirada. Inicia sesión de nuevo") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detalle,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SesionDB) -> Usuario:
    """Devuelve el usuario dueño del token. El rol y el estado se leen de la BD en cada petición,
    así un cambio de rol o una suspensión se aplican en la siguiente acción del usuario (HU-01.4)."""
    try:
        usuario_id = leer_token(token)
    except (jwt.PyJWTError, ValueError):
        raise _no_autenticado() from None
    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise _no_autenticado()
    return usuario


UsuarioActual = Annotated[Usuario, Depends(get_current_user)]


def require_role(*roles: str):
    """Crea una dependencia que deja pasar solo a los usuarios con alguno de esos roles.

    La autorización se verifica SIEMPRE aquí, en el servidor: ocultar un botón en React no protege nada.
    """

    def comprobar(usuario: UsuarioActual) -> Usuario:
        if usuario.rol not in roles:
            raise SinPermiso("No tienes permiso para realizar esta acción")
        return usuario

    return comprobar
