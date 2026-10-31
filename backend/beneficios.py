
import json
from pathlib import Path


def consultar_beneficios(id_poliza, ruta_archivo=None):

    # Localizar el catalogo de beneficios
    if ruta_archivo is None:
        ruta_archivo = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "beneficios_polizas.json"
        )

    # Leer el archivo JSON
    with open(
        ruta_archivo,
        "r",
        encoding="utf-8"
    ) as archivo:
        catalogo = json.load(archivo)

    # Normalizar identificador
    id_poliza = id_poliza.strip().upper()

    # Verificar que exista la poliza
    if id_poliza not in catalogo:
        return {
            "id_poliza": id_poliza,
            "encontrada": False,
            "beneficios": [],
            "mensaje": (
                "Poliza no encontrada "
                "en el catalogo academico."
            )
        }

    # Seleccionar exclusivamente beneficios vigentes
    beneficios_vigentes = [
        {
            "nombre": beneficio["nombre"],
            "descripcion": beneficio["descripcion"]
        }
        for beneficio in catalogo[id_poliza]
        if beneficio["vigente"] is True
    ]

    return {
        "id_poliza": id_poliza,
        "encontrada": True,
        "beneficios": beneficios_vigentes,
        "mensaje": (
            "Consulta academica realizada correctamente."
        )
    }
