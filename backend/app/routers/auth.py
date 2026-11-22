from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import SesionDB, UsuarioActual
from app.core.security import crear_token
from app.schemas.auth import Token
from app.schemas.usuario import UsuarioRegistro, UsuarioSalida
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UsuarioSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una cuenta",
    responses={409: {"description": "El correo ya está registrado"}},
)
def registrar(datos: UsuarioRegistro, db: SesionDB):
    """Crea una cuenta nueva con rol **capturista**. Solo un administrador puede cambiar el rol después.

    La contraseña debe tener al menos 8 caracteres, con letras y números."""
    return auth_service.registrar_usuario(db, datos)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    responses={401: {"description": "Correo o contraseña incorrectos"}, 403: {"description": "Cuenta suspendida"}},
)
def iniciar_sesion(formulario: Annotated[OAuth2PasswordRequestForm, Depends()], db: SesionDB):
    """Devuelve un token JWT. En el campo `username` va el **correo**.

    El cliente lo manda después en el encabezado `Authorization: Bearer <token>`."""
    usuario = auth_service.autenticar(db, formulario.username, formulario.password)
    return Token(access_token=crear_token(usuario.id))


@router.get(
    "/me",
    response_model=UsuarioSalida,
    summary="Usuario de la sesión actual",
    responses={401: {"description": "Sin sesión o sesión expirada"}},
)
def quien_soy(usuario: UsuarioActual):
    """Devuelve los datos del usuario dueño del token (nombre, correo y rol)."""
    return usuario
