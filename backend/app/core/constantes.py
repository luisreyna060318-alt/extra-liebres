"""Valores permitidos que se usan en la base de datos, en la API y en el seed.

Se guardan sin acentos (son valores "de máquina"); la interfaz muestra la etiqueta bonita.
"""

# "lector" es el rol de las cuentas que se crean solas desde el registro: solo ve el tablero y las listas de grupos
# y catálogos. Solo un administrador puede subirlo a capturista o administrador.
ROLES = ("administrador", "capturista", "lector")
# Los roles que pueden ver datos de alumnos y registrar o cambiar información
ROLES_DE_PERSONAL = ("administrador", "capturista")
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

# Carreras del ITCJ que se pueden elegir al capturar un alumno. El formulario y el filtro muestran esta lista y el
# servidor la exige (422 si la carrera no está). El orden es el de la lista.
CARRERAS = (
    "LIC. ADMINISTRACIÓN",
    "CONTADOR PÚBLICO",
    "ING. ELECTROMECÁNICA",
    "ING. MECÁNICA",
    "ING. SISTEMAS COMPUTACIONALES",
    "ING. ELECTRÓNICA",
    "ING. EN TECNOLOGÍAS DE LA INFORMACIÓN Y COMUNICACIONES",
    "ING. EN GESTIÓN EMPRESARIAL",
    "ING. ELÉCTRICA",
    "ING. INDUSTRIAL",
    "ING. LOGÍSTICA",
    "ING. MECATRÓNICA",
    "ING. INDUSTRIAL (EAD)",
    "ING. SISTEMAS COMPUTACIONALES (EAD)",
    "ING. EN GESTIÓN EMPRESARIAL (EAD)",
    "ING. INDUSTRIAL MODALIDAD MIXTA",
)

# Número de control: exactamente 8 dígitos (solo números) y, de momento, nunca mayor a este valor.
NOCONTROL_MAXIMO = 26999999

# Semestres: años permitidos de momento y los únicos dos periodos (enero-junio y agosto-diciembre).
ANIO_SEMESTRE_MINIMO = 2000
ANIO_SEMESTRE_MAXIMO = 2027
PERIODOS_SEMESTRE = ((1, 6), (8, 12))

# Un grupo debe durar al menos 1 hora
DURACION_MINIMA_GRUPO_MINUTOS = 60
