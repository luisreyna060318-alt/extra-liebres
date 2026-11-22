from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Sistema"])


@router.get("/health", summary="Estado del servicio")
def health() -> dict[str, str]:
    """Responde 200 si el backend está encendido. Lo usan Docker y el despliegue para saber si está vivo."""
    return {"estado": "ok"}
