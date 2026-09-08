"""Chat simple en la terminal: elegís el modo (Cliente / Productor / Comercial)."""
import sys

from .config import Config
from .agent import buscar_texto

MODOS = {"c": "cliente", "p": "productor", "m": "comercial"}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("=" * 60)
    print(" Agente de Productores v2 (CRM en Firebase + noticias)")
    print("=" * 60)

    try:
        Config.validate()
    except RuntimeError as e:
        print(f"\n⚠️  {e}\n")
        return

    print("\nModos: 'c' Cliente, 'p' Agente Productor, 'm' Comercial, 'salir' para terminar.\n")

    modo = None
    while True:
        if modo is None:
            eleccion = input("Modo (c/p/m) > ").strip().lower()
            if eleccion in ("salir", "exit", "quit"):
                break
            if eleccion not in MODOS:
                print("Escribí 'c' (cliente), 'p' (productor), 'm' (comercial) o 'salir'.\n")
                continue
            modo = MODOS[eleccion]
            continue

        nombre = input(f"{modo.capitalize()} > ").strip()
        if not nombre:
            continue
        if nombre.lower() in ("salir", "exit", "quit"):
            break
        if nombre.lower() == "cambiar":
            modo = None
            continue

        try:
            resumen = buscar_texto(modo, nombre)
        except Exception as e:
            print(f"\n⚠️  Ocurrió un error buscando información: {e}\n")
            continue

        print("\n" + "-" * 60)
        print(resumen)
        print("-" * 60)
        print("(Escribí 'cambiar' para pasar a otro modo de búsqueda)\n")


if __name__ == "__main__":
    main()
