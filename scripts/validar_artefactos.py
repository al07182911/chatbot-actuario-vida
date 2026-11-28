
import hashlib
import json
import sys
from pathlib import Path


def validar_artefactos(manifiesto_path, repo_path):

    manifiesto_path = Path(manifiesto_path).resolve()
    repo_path = Path(repo_path).resolve()

    with open(
        manifiesto_path,
        "r",
        encoding="utf-8"
    ) as f:
        manifiesto = json.load(f)

    artefactos = manifiesto.get("artefactos", [])

    if not artefactos:
        raise ValueError("Manifiesto sin artefactos.")

    rutas = set()

    for artefacto in artefactos:

        nombre = artefacto["archivo"]
        esperado = artefacto["sha256"]

        ruta = (repo_path / nombre).resolve()

        if not ruta.is_relative_to(repo_path):
            raise ValueError(
                "Ruta fuera del repositorio."
            )

        if nombre in rutas:
            raise ValueError(
                "Artefacto duplicado."
            )

        rutas.add(nombre)

        if not ruta.is_file():
            raise FileNotFoundError(nombre)

        actual = hashlib.sha256(
            ruta.read_bytes()
        ).hexdigest()

        if actual != esperado:
            raise ValueError(
                f"Integridad no valida: {nombre}"
            )

        print("OK:", nombre)

    print(
        "\nIntegridad verificada:",
        len(artefactos),
        "artefactos."
    )

    return True


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(
            "Uso: python validar_artefactos.py "
            "MANIFIESTO REPOSITORIO"
        )
        sys.exit(2)

    try:
        validar_artefactos(
            sys.argv[1],
            sys.argv[2]
        )
    except Exception as error:
        print("ERROR:", error)
        sys.exit(1)
