"""Carga de configuración desde variables de entorno (.env)."""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ruta_absoluta(path: str) -> str:
    if not path or os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)


class Config:
    # Firebase — el mismo proyecto/base que usa la app de Google AI Studio
    # (Clientes y Cuentas / Dashboard / Aperturas / Calificaciones).
    FIREBASE_CREDENTIALS_PATH = _ruta_absoluta(
        os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-service-account.json")
    )
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "gen-lang-client-0521346376")
    FIREBASE_DATABASE_ID = os.getenv(
        "FIREBASE_DATABASE_ID", "ai-studio-3edb5f30-58ca-4d7c-9631-c6ddd3537670"
    )

    @classmethod
    def validate(cls):
        faltantes = []
        if not os.path.exists(cls.FIREBASE_CREDENTIALS_PATH):
            faltantes.append(
                f"FIREBASE_CREDENTIALS_PATH (no se encontró el archivo: {cls.FIREBASE_CREDENTIALS_PATH})"
            )
        if faltantes:
            raise RuntimeError(
                "Faltan variables en tu .env: " + "; ".join(faltantes) +
                "\nRevisá el README para completar cada una."
            )
