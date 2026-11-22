"""Configuración de la aplicación.

Todo viene de variables de entorno (factor III de The Twelve-Factor App). En desarrollo se leen del
archivo `.env` de la raíz del repositorio; en producción las pone la plataforma (Render, Docker...).
"""

from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

# backend/app/core/config.py -> subimos 3 niveles para llegar a la raíz del repositorio
RAIZ = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # hide_input_in_errors: si la configuración es inválida, el error NO imprime los valores recibidos
    # (podrían ser la SECRET_KEY o la contraseña de la BD, y los errores terminan en los logs del servidor).
    model_config = SettingsConfigDict(env_file=RAIZ / ".env", extra="ignore", hide_input_in_errors=True)

    # --- Base de datos ---
    # En producción (Neon) la plataforma da una DATABASE_URL completa. En desarrollo se arma con las
    # piezas POSTGRES_*, que son las mismas que usa el contenedor de PostgreSQL.
    database_url: str | None = None
    postgres_user: str = "extra_liebres"
    postgres_password: str = ""
    postgres_db: str = "extra_liebres"
    postgres_host: str = "127.0.0.1"  # no "localhost": en Windows resuelve primero a IPv6 y tarda
    postgres_port: int = 5432

    # "desarrollo" o "produccion". En producción se exigen valores seguros (ver _validar_produccion).
    entorno: str = "desarrollo"

    # --- Seguridad ---
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"  # varios dominios separados por comas

    # --- Servicio externo (clima) ---
    clima_url: str = "https://api.open-meteo.com/v1/forecast"
    clima_respaldo_url: str = "https://wttr.in"  # se usa si Open-Meteo falla (por ejemplo, 429)
    clima_umbral_lluvia: int = 50

    # --- Usuarios de prueba del seed (solo desarrollo) ---
    seed_admin_correo: str | None = None
    seed_admin_password: str | None = None
    seed_capturista_correo: str | None = None
    seed_capturista_password: str | None = None

    @model_validator(mode="after")
    def _validar_produccion(self) -> "Settings":
        """El .env.example trae una clave de ejemplo pública: en producción no se acepta."""
        if self.entorno == "produccion" and (len(self.secret_key) < 32 or self.secret_key.startswith("cambia-")):
            raise ValueError("En producción SECRET_KEY debe ser larga (32+ caracteres) y aleatoria, no la del ejemplo")
        return self

    @property
    def sqlalchemy_url(self) -> URL:
        """URL de conexión para SQLAlchemy con el driver psycopg 3."""
        if self.database_url:
            # Neon/Render entregan "postgresql://..."; SQLAlchemy necesita indicar el driver.
            return make_url(self.database_url.replace("postgresql://", "postgresql+psycopg://", 1))
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def cors_origins_lista(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
