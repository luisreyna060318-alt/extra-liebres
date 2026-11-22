"""Punto de entrada de la API. Se arranca con: uvicorn app.main:app --reload"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errores import ErrorNegocio
from app.routers import (
    alumnos,
    auth,
    busqueda,
    clima,
    consultas,
    dashboard,
    export,
    extraescolares,
    grupos,
    health,
    inscripciones,
    promotores,
    semestres,
    usuarios,
)

app = FastAPI(
    title="Extra-Liebres API",
    description=(
        "API REST de Extra-Liebres: registros históricos de actividades extraescolares del "
        "Instituto Tecnológico de Ciudad Juárez. Proyecto final de Programación Web.\n\n"
        "Para probar las rutas protegidas: inicia sesión en `/api/auth/login`, o usa el botón **Authorize**."
    ),
    version="0.2.0",
)

# CORS: el navegador solo deja que el frontend (y nadie más) llame a la API. Nunca se usa "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_lista,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(ErrorNegocio)
async def manejar_error_de_negocio(request: Request, error: ErrorNegocio) -> JSONResponse:
    """Convierte los errores de los servicios en respuestas JSON con la misma forma que los errores de FastAPI."""
    headers = {"WWW-Authenticate": "Bearer"} if error.status_code == 401 else None
    return JSONResponse(status_code=error.status_code, content={"detail": error.mensaje}, headers=headers)


@app.middleware("http")
async def cabeceras_de_seguridad(request: Request, call_next):
    """Agrega a TODAS las respuestas las cabeceras de seguridad que el navegador respeta (OWASP A02)."""
    respuesta = await call_next(request)
    respuesta.headers["X-Content-Type-Options"] = "nosniff"  # el navegador no "adivina" el tipo de un archivo
    respuesta.headers["X-Frame-Options"] = "DENY"  # nadie puede incrustar la API dentro de otra página
    respuesta.headers["Referrer-Policy"] = "no-referrer"  # no se filtra de qué página venimos
    if request.url.path.startswith("/api"):
        respuesta.headers["Cache-Control"] = "no-store"  # son datos personales: que nadie los guarde en caché
    if settings.entorno == "produccion":
        # Solo por HTTPS en producción: el navegador recuerda que este sitio nunca debe usar http://
        respuesta.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return respuesta


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(alumnos.router)
app.include_router(dashboard.router)
app.include_router(grupos.router)
app.include_router(inscripciones.router)
app.include_router(consultas.router)
app.include_router(busqueda.router)
app.include_router(export.router)
app.include_router(promotores.router)
app.include_router(extraescolares.router)
app.include_router(semestres.router)
app.include_router(clima.router)
