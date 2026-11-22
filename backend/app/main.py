"""Punto de entrada de la API. Se arranca con: uvicorn app.main:app --reload"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import health

app = FastAPI(
    title="Extra-Liebres API",
    description=(
        "API REST de Extra-Liebres: registros históricos de actividades extraescolares del "
        "Instituto Tecnológico de Ciudad Juárez. Proyecto final de Programación Web."
    ),
    version="0.1.0",
)

# CORS: el navegador solo deja que el frontend (y nadie más) llame a la API. Nunca se usa "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_lista,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router)
