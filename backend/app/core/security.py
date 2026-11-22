"""Seguridad: hash de contraseñas (bcrypt) y tokens de sesión (JWT).

Sesión sin estado: al iniciar sesión el servidor firma un JWT con su SECRET_KEY y el cliente lo manda en
cada petición. No hay "cerrar sesión" en el servidor: el cliente simplemente descarta el token. Por eso el
token expira solo (ACCESS_TOKEN_EXPIRE_MINUTES) y el rol/estado del usuario se lee de la BD en cada petición.
"""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import settings

# bcrypt solo procesa los primeros 72 BYTES (no caracteres: una "é" ocupa 2 bytes) y desde la versión 5
# lanza ValueError si se pasa de ahí.
MAX_BYTES_PASSWORD = 72


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de la contraseña (con sal aleatoria). La contraseña nunca se guarda."""
    datos = password.encode("utf-8")
    if len(datos) > MAX_BYTES_PASSWORD:
        raise ValueError(f"La contraseña no puede pasar de {MAX_BYTES_PASSWORD} bytes")
    return bcrypt.hashpw(datos, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """True si la contraseña corresponde al hash guardado."""
    datos = password.encode("utf-8")
    if len(datos) > MAX_BYTES_PASSWORD:
        return False  # una contraseña tan larga no pudo haberse guardado: login rechazado (401), no error 500
    return bcrypt.checkpw(datos, password_hash.encode("utf-8"))


def crear_token(usuario_id: int, expira_en: timedelta | None = None) -> str:
    """Crea un JWT firmado. Solo lleva el id del usuario ("sub") y la fecha de expiración ("exp")."""
    ahora = datetime.now(UTC)
    if expira_en is None:
        expira_en = timedelta(minutes=settings.access_token_expire_minutes)
    datos = {"sub": str(usuario_id), "iat": ahora, "exp": ahora + expira_en}
    return jwt.encode(datos, settings.secret_key, algorithm=settings.jwt_algorithm)


def leer_token(token: str) -> int:
    """Verifica la firma y la expiración del JWT y devuelve el id del usuario.

    Lanza jwt.PyJWTError (o ValueError) si el token está manipulado, vencido o mal formado.
    Se indica la lista de algoritmos permitidos para rechazar tokens "alg: none" y similares.
    """
    datos = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "sub"]},
    )
    return int(datos["sub"])
