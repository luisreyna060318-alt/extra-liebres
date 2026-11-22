"""Valores permitidos que se usan en la base de datos, en la API y en el seed.

Se guardan sin acentos (son valores "de máquina"); la interfaz muestra la etiqueta bonita.
"""

ROLES = ("administrador", "capturista")
SEXOS = ("M", "F")
TIPOS_ACTIVIDAD = ("deportiva", "cultural", "civica")
DIAS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado")
DESEMPENOS = ("Excelente", "Notable", "Bueno", "Suficiente", "Insuficiente")

# Lugares para las actividades deportivas (el formulario de grupo muestra esta lista)
INSTALACIONES = (
    "Cancha de fútbol",
    "Cancha de básquetbol",
    "Cancha de voleibol",
    "Gimnasio",
    "Pista de atletismo",
    "Alberca",
)
