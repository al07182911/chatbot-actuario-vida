
from datetime import datetime, timezone
from uuid import uuid4
from typing import List
from pydantic import BaseModel, Field


CATEGORIAS_NPS = {
    "mala_atencion",
    "tiempo_respuesta",
    "problema_no_resuelto",
    "informacion_incorrecta",
    "problemas_cobro"
}

AREAS_NPS = {
    "Atencion a clientes",
    "Operaciones",
    "Cobranza",
    "Producto",
    "Por determinar"
}


class DatosCasoNPS(BaseModel):
    descripcion: str = Field(
        min_length=10,
        max_length=2000
    )
    categorias: List[str]
    areas_relacionadas: List[str]
    resumen: str = Field(
        min_length=5,
        max_length=1000
    )


# Almacenamiento temporal del prototipo
registro_nps = {}


def registrar_caso_nps(datos: DatosCasoNPS):

    # Validar las categorias
    if (
        not datos.categorias
        or any(
            categoria not in CATEGORIAS_NPS
            for categoria in datos.categorias
        )
        or len(datos.categorias) != len(set(datos.categorias))
    ):
        raise ValueError(
            "Categorias NPS invalidas."
        )

    # Validar las areas
    if (
        not datos.areas_relacionadas
        or any(
            area not in AREAS_NPS
            for area in datos.areas_relacionadas
        )
        or len(datos.areas_relacionadas)
        != len(set(datos.areas_relacionadas))
    ):
        raise ValueError(
            "Areas NPS invalidas."
        )

    folio = "NPS-" + uuid4().hex[:8].upper()

    caso = {
        "folio": folio,
        "fecha_registro": datetime.now(
            timezone.utc
        ).isoformat(),
        "descripcion": datos.descripcion,
        "categorias": datos.categorias,
        "areas_relacionadas": datos.areas_relacionadas,
        "resumen": datos.resumen,
        "estado": "pendiente_revision",
        "origen": "Chatbot Actuario Vida",
        "tipo": "simulacion_academica"
    }

    registro_nps[folio] = caso

    return caso
