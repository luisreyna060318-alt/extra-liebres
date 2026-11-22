import pytest

from app.core.config import Settings


def test_produccion_rechaza_la_secret_key_de_ejemplo():
    with pytest.raises(ValueError):
        Settings(_env_file=None, entorno="produccion", secret_key="cambia-esta-clave-por-una-larga-y-aleatoria")
    with pytest.raises(ValueError):
        Settings(_env_file=None, entorno="produccion", secret_key="corta")


def test_produccion_acepta_una_secret_key_larga():
    ajustes = Settings(_env_file=None, entorno="produccion", secret_key="x" * 40)
    assert ajustes.entorno == "produccion"


def test_desarrollo_acepta_la_secret_key_de_ejemplo():
    ajustes = Settings(_env_file=None, secret_key="cambia-esta-clave-por-una-larga-y-aleatoria")
    assert ajustes.entorno == "desarrollo"


def test_url_de_neon_usa_el_driver_psycopg():
    # Neon/Render dan "postgresql://..."; SQLAlchemy necesita saber qué driver usar
    ajustes = Settings(_env_file=None, secret_key="x", database_url="postgresql://u:p@host.neon.tech/bd")
    assert ajustes.sqlalchemy_url.drivername == "postgresql+psycopg"
    assert ajustes.sqlalchemy_url.host == "host.neon.tech"


def test_cors_origins_acepta_varios_dominios():
    ajustes = Settings(_env_file=None, secret_key="x", cors_origins="http://a.com, https://b.com")
    assert ajustes.cors_origins_lista == ["http://a.com", "https://b.com"]


def test_el_error_de_configuracion_no_imprime_los_valores_recibidos():
    # Los errores terminan en los logs del servidor. Pydantic normalmente agrega "input_value={...}" con los
    # valores recibidos (recortados con "..."), que pueden ser la SECRET_KEY o la contraseña de la BD.
    with pytest.raises(ValueError) as error:
        Settings(
            _env_file=None, entorno="produccion", secret_key="cambia-clave-de-ejemplo", postgres_password="privada"
        )
    texto = str(error.value)
    assert "input_value" not in texto
    assert "cambia-clave-de-ejemplo" not in texto
    assert "privada" not in texto
