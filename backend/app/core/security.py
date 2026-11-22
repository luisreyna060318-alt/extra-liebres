"""Seguridad: hash de contraseñas con bcrypt.

Aquí solo está el hash (lo necesita el seed). El JWT y la autorización por rol se agregan en la
historia de inicio de sesión (HU-01.2 y HU-01.3).
"""

import bcrypt

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
