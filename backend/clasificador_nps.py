
import json
import os

from openai import OpenAI

MODELO_IA = os.getenv("OPENAI_MODEL", "gpt-6-luna")

INSTRUCCIONES_NPS = """
Eres un analista de experiencia del cliente
especializado en seguros de vida.

Clasifica las causas de insatisfaccion expresadas
en el mensaje de un cliente.

Categorias permitidas:
- mala_atencion
- tiempo_respuesta
- problema_no_resuelto
- informacion_incorrecta
- problemas_cobro

Areas permitidas:
- Atencion a clientes
- Operaciones
- Cobranza
- Producto
- Por determinar

Reglas:
1. Puedes identificar varias categorias.
2. No inventes causas ni hechos.
3. Las areas son sugerencias para revision.
4. No atribuyas culpabilidad individual.
5. Si no hay causas identificables, devuelve
   categorias y areas vacias.
6. No incluyas datos personales.
7. Devuelve exclusivamente JSON valido.

Formato:
{
  "categorias": ["categoria"],
  "areas_relacionadas": ["area"],
  "resumen": "Resumen objetivo y breve"
}
"""

CATEGORIAS_VALIDAS = {
    "mala_atencion",
    "tiempo_respuesta",
    "problema_no_resuelto",
    "informacion_incorrecta",
    "problemas_cobro"
}

AREAS_VALIDAS = {
    "Atencion a clientes",
    "Operaciones",
    "Cobranza",
    "Producto",
    "Por determinar"
}


def clasificar_insatisfaccion(mensaje):

    if not isinstance(mensaje, str):
        raise ValueError("El mensaje debe ser texto.")

    mensaje = mensaje.strip()

    if len(mensaje) < 10 or len(mensaje) > 2000:
        raise ValueError(
            "La descripcion debe tener entre 10 y 2000 caracteres."
        )

    cliente = OpenAI(
        timeout=30.0,
        max_retries=1
    )

    respuesta = cliente.responses.create(
        model=MODELO_IA,
        instructions=INSTRUCCIONES_NPS,
        input=mensaje,
        max_output_tokens=400,
        store=False
    )

    resultado = json.loads(respuesta.output_text)

    categorias = resultado["categorias"]
    areas = resultado["areas_relacionadas"]
    resumen = resultado["resumen"]

    if (
        not isinstance(categorias, list)
        or not isinstance(areas, list)
        or not isinstance(resumen, str)
        or any(
            not isinstance(c, str)
            or c not in CATEGORIAS_VALIDAS
            for c in categorias
        )
        or any(
            not isinstance(a, str)
            or a not in AREAS_VALIDAS
            for a in areas
        )
        or len(categorias) != len(set(categorias))
        or len(areas) != len(set(areas))
        or not resumen.strip()
    ):
        raise ValueError(
            "La respuesta de clasificacion NPS no es valida."
        )

    return resultado
