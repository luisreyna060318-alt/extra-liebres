from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.clima import ClimaSalida
from app.services import clima as clima_service

# Cualquier usuario con sesión puede ver el clima (401 si no hay sesión).
router = APIRouter(
    prefix="/api/clima",
    tags=["Clima"],
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Sin sesión"}},
)


@router.get("", response_model=ClimaSalida, response_model_exclude_none=True, summary="Clima de Ciudad Juárez")
def clima():
    """Temperatura actual y probabilidad máxima de lluvia en las próximas 12 horas (Open-Meteo, caché de 1 hora).

    Si el servicio externo falla responde 200 con `{"disponible": false, "mensaje": ...}` para no romper el tablero."""
    return clima_service.obtener_clima()
