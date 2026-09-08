"""Acceso de solo lectura a las colecciones de Firestore del CRM (la misma
base que usa la app de Google AI Studio: Clientes y Cuentas / Dashboard /
Aperturas / Calificaciones).

Este agente NUNCA escribe en Firestore — solo `fetch_collection` (lectura).
Ver contrato (prompts/system_prompt.md §4.4) y DECISIONES.md (Gobierno y
riesgo) para el detalle de por qué es una restricción deliberada, no una
limitación técnica.
"""
import firebase_admin
from firebase_admin import credentials, firestore

from ..config import Config

_app = None


def _get_client():
    global _app
    if _app is None:
        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
        _app = firebase_admin.initialize_app(cred)
    if Config.FIREBASE_DATABASE_ID:
        return firestore.client(app=_app, database_id=Config.FIREBASE_DATABASE_ID)
    return firestore.client(app=_app)


def fetch_collection(nombre_coleccion: str) -> list[dict]:
    """Trae todos los documentos de una colección de primer nivel (no hay
    subcolecciones en este esquema — confirmado) como lista de dicts, cada
    uno con su "id" de documento incluido."""
    db = _get_client()
    resultados = []
    for doc in db.collection(nombre_coleccion).stream():
        data = doc.to_dict()
        data.setdefault("id", doc.id)
        resultados.append(data)
    return resultados
