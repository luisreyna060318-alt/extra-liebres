"""Lógica de registro e inicio de sesión (HU-01.1 y HU-01.2)."""

from functools import cache

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, NoAutenticado, SinPermiso
from app.core.security import hash_password, verify_password
from app.models import Usuario
from app.schemas.usuario import UsuarioRegistro


@cache
def _hash_falso() -> str:
    """Hash de una contraseña inventada. Se compara cuando el correo no existe para que el login tarde
    lo mismo con un correo inexistente que con uno existente (así no se puede adivinar qué correos hay)."""
    return hash_password("contrasena-inexistente-1")


def registrar_usuario(db: Session, datos: UsuarioRegistro) -> Usuario:
    """Crea una cuenta nueva. Siempre con rol capturista: solo un administrador puede cambiarlo después."""
    if db.scalar(select(Usuario).where(Usuario.correo == datos.correo)):
        raise Conflicto("Ese correo ya está registrado")
    usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        password_hash=hash_password(datos.password),
        rol="capturista",
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        # Dos registros simultáneos con el mismo correo: la restricción UNIQUE de la BD lo detecta
        db.rollback()
        raise Conflicto("Ese correo ya está registrado") from None
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, correo: str, password: str) -> Usuario:
    """Comprueba correo y contraseña. El mensaje de error es el mismo si falla cualquiera de los dos."""
    usuario = db.scalar(select(Usuario).where(Usuario.correo == correo.strip().lower()))
    hash_guardado = usuario.password_hash if usuario else _hash_falso()
    contrasena_correcta = verify_password(password, hash_guardado)
    if usuario is None or not contrasena_correcta:
        raise NoAutenticado("Correo o contraseña incorrectos")
    if not usuario.activo:
        # Solo se llega aquí con la contraseña correcta, así que no revela nada a un extraño
        raise SinPermiso("Tu cuenta está suspendida. Habla con el administrador")
    return usuario
