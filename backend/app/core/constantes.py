"""Valores permitidos que se usan en la base de datos, en la API y en el seed.

Se guardan sin acentos (son valores "de máquina"); la interfaz muestra la etiqueta bonita.
"""

ROLES = ("administrador", "capturista")
SEXOS = ("M", "F")
TIPOS_ACTIVIDAD = ("deportiva", "cultural", "civica")
DIAS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado")
DESEMPENOS = ("Excelente", "Notable", "Bueno", "Suficiente", "Insuficiente")

# Lugares permitidos para las actividades deportivas (canchas, gimnasio, pista, alberca).
# El formulario de grupo muestra esta lista y el servidor la exige (P9, HU-04.2): 422 si el lugar no está.
# Las actividades culturales y cívicas usan un aula de texto libre.
INSTALACIONES = (
    "Cancha de fútbol",
    "Cancha de básquetbol",
    "Cancha de voleibol",
    "Gimnasio",
    "Pista de atletismo",
    "Alberca",
)
