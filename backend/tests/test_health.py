from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_responde_ok():
    respuesta = client.get("/api/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_documentacion_openapi_disponible():
    # La materia pide que /docs (OpenAPI) esté disponible
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200
