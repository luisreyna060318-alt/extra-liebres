"""Configuración común de las pruebas.

Las pruebas no necesitan un archivo .env: ponemos valores de prueba antes de importar la aplicación.
"""

import os

os.environ.setdefault("SECRET_KEY", "clave-solo-para-pruebas")
