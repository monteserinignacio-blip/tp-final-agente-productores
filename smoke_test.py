"""Prueba de humo con datos SINTÉTICOS (mockeando Firestore) para validar la
lógica de agent.py antes de correr contra datos reales. No es una de las 3
corridas reales del TP (esas se hacen con datos reales, en la compu de
Chicho) — esto es solo control de calidad del código."""
import sys
from unittest.mock import patch

sys.path.insert(0, ".")

COMERCIALES = [
    {"id": "com1", "nombre": "Nacho"},
    {"id": "com2", "nombre": "Santi"},
]
APS = [
    {"id": "ap1", "nombre": "Pedro Longobardi", "comercialId": "com1"},
    {"id": "ap2", "nombre": "Diego Ruggeri", "comercialId": "com2"},
]
CLIENTES = [
    {"id": "cl1", "nombre": "Pedro Carafi", "numeroCuenta": "51450", "agenteProductorId": "ap1", "comercialId": None},
    {"id": "cl2", "nombre": "Pedro Carafi", "numeroCuenta": "4272", "agenteProductorId": "ap1", "comercialId": "com1"},
    {"id": "cl3", "nombre": "Rodrigo Carafi", "numeroCuenta": "3048", "agenteProductorId": "ap2", "comercialId": None},
    {"id": "cl4", "nombre": "Sin Cuenta SA", "numeroCuenta": "", "agenteProductorId": "ap1", "comercialId": "com1"},
]
COMPANIES = [
    {"id": "co1", "businessName": "Pedro Carafi", "producer": "Pedro Longobardi", "currentStage": "Prospecto",
     "checklist": [{"name": "EECC 2024", "isPresent": True}, {"name": "Manifestación de Bienes", "isPresent": False}]},
    {"id": "co2", "businessName": "Sin Cuenta SA", "producer": "Nacho", "currentStage": "Calificada",
     "checklist": [], "qualifiedData": {"multi": 500000, "currency": "ARS", "vencimiento": "2027-05-28"}},
]
APERTURAS = [
    {"id": "ap_1", "cliente": "Sin Cuenta SA", "agenteProductorId": "ap1", "comercialId": "com1", "estado": "REVISION", "fechaSolicitud": "2026-09-01"},
    {"id": "ap_2", "cliente": "Otro Cliente", "agenteProductorId": "ap1", "comercialId": "com1", "estado": "FINALIZADA", "fechaSolicitud": "2026-08-01"},
]
REMINDERS = [
    {"id": "r1", "agenteProductorId": "ap1", "comercialId": "com1", "mensaje": "Llamar por apertura", "fecha": "2026-09-10", "completado": False},
    {"id": "r2", "agenteProductorId": "ap1", "comercialId": "com1", "mensaje": "Recordatorio viejo ya resuelto", "fecha": "2026-08-01", "completado": True},
]
PENDIENTES = [
    {"id": "p1", "comercialId": "com1", "descripcion": "Firmar documentos Carlos Walton", "completado": False},
    {"id": "p2", "comercialId": "com1", "descripcion": "Pendiente viejo ya resuelto", "completado": True},
]

DATA = {
    "comerciales": COMERCIALES, "agentesProductores": APS, "clientes": CLIENTES,
    "companies": COMPANIES, "aperturas": APERTURAS, "reminders": REMINDERS,
    "pendientes": PENDIENTES,
}


def fake_fetch(nombre):
    return DATA.get(nombre, [])


def fake_news(query, **kwargs):
    return []  # sin red en este entorno de prueba


with patch("src.connectors.firestore_crm.fetch_collection", side_effect=fake_fetch), \
     patch("src.connectors.news.search_news", side_effect=fake_news):
    from src.agent import buscar_texto, buscar

    print("### MODO CLIENTE — 'Carafi' (debe dar 2 fichas: Pedro y Rodrigo) ###")
    print(buscar_texto("cliente", "Carafi"))

    print("\n\n### MODO CLIENTE — 'Sin Cuenta SA' (numeroCuenta vacío + Calificada) ###")
    print(buscar_texto("cliente", "Sin Cuenta SA"))

    print("\n\n### MODO PRODUCTOR — 'Longobardi' ###")
    print(buscar_texto("productor", "Longobardi"))

    print("\n\n### MODO COMERCIAL — 'Nacho' (aperturas: 1 debe quedar afuera por Finalizada;")
    print("### pendiente/recordatorio ya resueltos tampoco deben verse) ###")
    txt_nacho = buscar_texto("comercial", "Nacho")
    print(txt_nacho)
    assert "ya resuelto" not in txt_nacho, "Un pendiente/recordatorio completado se está mostrando igual"
    print("OK: los pendientes/recordatorios completados no aparecen.")

    print("\n\n### MODO CLIENTE — 'Inexistente' (0 coincidencias) ###")
    r = buscar("cliente", "Zzzznadie")
    assert r["encontrado"] is False
    print("OK: reporta 'no encontrado' explícito, no inventa nada.")

print("\n\nTODAS LAS PRUEBAS DE HUMO PASARON SIN EXCEPCIONES.")
