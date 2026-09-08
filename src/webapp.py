"""
Interfaz web: las 3 búsquedas del contrato — Cliente, Agente Productor,
Comercial. Pensada para correr local (http://127.0.0.1:5000) o desplegada
en internet (ver DEPLOY.md) — en ese caso, protegida con usuario/contraseña
(HTTP Basic Auth) porque expone datos reales de clientes.

No usa ninguna API paga (ver DECISIONES.md, Análisis económico).
"""
import functools
import os

from flask import Flask, jsonify, render_template, request, Response

from .config import Config
from .agent import buscar

app = Flask(__name__)


def _auth_habilitada() -> bool:
    return bool(os.getenv("BASIC_AUTH_USER") and os.getenv("BASIC_AUTH_PASS"))


def _credenciales_validas(auth) -> bool:
    if not auth:
        return False
    return (
        auth.username == os.getenv("BASIC_AUTH_USER")
        and auth.password == os.getenv("BASIC_AUTH_PASS")
    )


def requiere_login(vista):
    """Si BASIC_AUTH_USER / BASIC_AUTH_PASS están seteadas (típicamente en
    el despliegue público), exige usuario y contraseña. Si no están
    seteadas (uso local en tu compu), no pide nada — igual que antes."""
    @functools.wraps(vista)
    def envoltura(*args, **kwargs):
        if not _auth_habilitada():
            return vista(*args, **kwargs)
        auth = request.authorization
        if not _credenciales_validas(auth):
            return Response(
                "Acceso restringido — usuario y contraseña requeridos.",
                401,
                {"WWW-Authenticate": 'Basic realm="Agente de Productores"'},
            )
        return vista(*args, **kwargs)
    return envoltura


@app.route("/")
@requiere_login
def index():
    return render_template("index.html")


@app.route("/api/buscar")
@requiere_login
def api_buscar():
    modo = request.args.get("modo", "").strip().lower()
    nombre = request.args.get("nombre", "").strip()
    if modo not in ("cliente", "productor", "comercial"):
        return jsonify({"error": "Modo inválido."}), 400
    if not nombre:
        return jsonify({"error": "Escribí un nombre para buscar."}), 400
    try:
        Config.validate()
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    try:
        return jsonify(buscar(modo, nombre))
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error buscando información: {e}"}), 500


def main():
    print("=" * 60)
    print(" Agente de Productores v2 — abriendo en el navegador")
    print(" http://127.0.0.1:5000")
    if _auth_habilitada():
        print(" (Usuario y contraseña activados)")
    print("=" * 60)
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0" if os.getenv("PORT") else "127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
