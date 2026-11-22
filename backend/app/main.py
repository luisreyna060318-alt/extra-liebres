"""Punto de entrada de la API. Se arranca con: uvicorn app.main:app --reload"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errores import ErrorNegocio
from app.routers import alumnos, auth, clima, extraescolares, grupos, health, promotores, semestres, usuarios

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


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(alumnos.router)
app.include_router(grupos.router)
app.include_router(promotores.router)
app.include_router(extraescolares.router)
app.include_router(semestres.router)
app.include_router(clima.router)
