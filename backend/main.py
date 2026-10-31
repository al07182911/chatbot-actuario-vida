from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from openai import OpenAI
#from google.colab import userdata
import os
from typing import List
import json

app = FastAPI(
    title="Chatbot Actuario Vida",
    description="API academica de retencion responsable",
    version="0.2.0"
)

cliente_ia = OpenAI(
    #api_key=userdata.get("OPENAI_API_KEY"),
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=30.0,
    max_retries=1
)

CATEGORIAS = {
    "economia_personal",
    "falta_utilidad",
    "mala_experiencia"
}

INSTRUCCIONES = """
Eres el clasificador de motivos de cancelacion
de seguros de vida del proyecto Chatbot Actuario Vida.

Identifica exclusivamente las causas expresadas
en el mensaje del cliente.

Categorias:
- economia_personal
- falta_utilidad
- mala_experiencia

Reglas:
1. Permite multiples motivos.
2. No inventes motivos.
3. Si no hay causa identificable, devuelve [].
4. No calcules primas ni coberturas.
5. No intentes impedir la cancelacion.
6. Devuelve exclusivamente JSON valido.

Formato:
{
  "motivos": ["categoria"],
  "explicacion": "Explicacion breve"
}
"""

class MensajeCliente(BaseModel):
    mensaje: str = Field(
        min_length=1,
        max_length=2000
    )

class RespuestaChat(BaseModel):
    motivos: List[str]
    explicacion: str
    estado: str

@app.get("/health")
def verificar_estado():
    return {
        "estado": "activo",
        "aplicacion": "Chatbot Actuario Vida",
        "version": "0.2.0"
    }

@app.post("/chat", response_model=RespuestaChat)
def procesar_mensaje(datos: MensajeCliente):

    if not datos.mensaje.strip():
        raise HTTPException(
            status_code=422,
            detail="El mensaje no puede estar vacio."
        )

    try:
        respuesta = cliente_ia.responses.create(
            model="gpt-6-luna",
            instructions=INSTRUCCIONES,
            input=datos.mensaje,
            max_output_tokens=300,
            store=False
        )

        resultado = json.loads(
            respuesta.output_text
        )

        motivos = resultado["motivos"]
        explicacion = resultado["explicacion"]

        if (
            not isinstance(motivos, list)
            or not all(
                isinstance(m, str) and m in CATEGORIAS
                for m in motivos
            )
            or len(motivos) != len(set(motivos))
            or not isinstance(explicacion, str)
        ):
            raise ValueError(
                "Respuesta del modelo no valida"
            )

        return RespuestaChat(
            motivos=motivos,
            explicacion=explicacion,
            estado="clasificado"
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="No fue posible clasificar el mensaje."
        )
