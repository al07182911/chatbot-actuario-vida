
from uuid import uuid4
from typing import Optional
from backend.conversacion_economia import ConversacionEconomia

from backend.conversacion_beneficios import ConversacionBeneficios

from backend.conversacion_nps import ConversacionNPS

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from openai import OpenAI
from backend.cotizador import DatosCotizacion, calcular_alternativa
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


class SolicitudConversacion(BaseModel):
    sesion_id: Optional[str] = None
    mensaje: Optional[str] = None
    
sesiones_economia = {}
sesiones_beneficios = {}
sesiones_nps = {}

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
    
@app.post("/cotizar")
def cotizar_seguro(datos: DatosCotizacion):
    """
    Genera una alternativa academica de cobertura
    utilizando una tarifa fija de $1.50 por millar.
    """

    resultado = calcular_alternativa(datos)

    return {
        "estado": "cotizacion_generada",
        "tipo": "simulacion_academica",
        "tarifa_por_millar": 1.50,
        "resultado": resultado,
        "advertencia": (
            "Esta simulacion es exclusivamente academica "
            "y no representa una cotizacion oficial."
        )
    }


@app.post("/conversacion/economia")
def conversar_economia(datos: SolicitudConversacion):

    # Crear una nueva conversacion
    if datos.sesion_id is None:

        if datos.mensaje is not None:
            raise HTTPException(
                status_code=422,
                detail="Para iniciar, no envies un mensaje."
            )

        sesion_id = str(uuid4())

        conversacion = ConversacionEconomia()
        respuesta = conversacion.iniciar()

        sesiones_economia[sesion_id] = conversacion

        return {
            "sesion_id": sesion_id,
            "estado": conversacion.estado,
            "respuesta": respuesta
        }

    # Recuperar una conversacion existente
    if datos.sesion_id not in sesiones_economia:
        raise HTTPException(
            status_code=404,
            detail="Sesion no encontrada."
        )

    if not datos.mensaje or not datos.mensaje.strip():
        raise HTTPException(
            status_code=422,
            detail="Debes enviar un mensaje."
        )

    conversacion = sesiones_economia[datos.sesion_id]

    # Evitar continuar una sesion finalizada
    if conversacion.estado == "cancelacion":
        return {
            "sesion_id": datos.sesion_id,
            "estado": "cancelacion",
            "respuesta": "La conversacion ha finalizado."
        }

    respuesta = conversacion.procesar(datos.mensaje)

    return {
        "sesion_id": datos.sesion_id,
        "estado": conversacion.estado,
        "respuesta": respuesta
    }


@app.post("/conversacion/beneficios")
def conversar_beneficios(datos: SolicitudConversacion):

    # Crear una nueva conversacion
    if datos.sesion_id is None:

        if datos.mensaje is not None:
            raise HTTPException(
                status_code=422,
                detail="Para iniciar, no envies un mensaje."
            )

        sesion_id = str(uuid4())

        conversacion = ConversacionBeneficios()
        respuesta = conversacion.iniciar()

        sesiones_beneficios[sesion_id] = conversacion

        return {
            "sesion_id": sesion_id,
            "estado": conversacion.estado,
            "respuesta": respuesta
        }

    # Verificar que exista la sesion
    if datos.sesion_id not in sesiones_beneficios:
        raise HTTPException(
            status_code=404,
            detail="Sesion no encontrada."
        )

    # Validar mensaje
    if not datos.mensaje or not datos.mensaje.strip():
        raise HTTPException(
            status_code=422,
            detail="Debes enviar un mensaje."
        )

    conversacion = sesiones_beneficios[datos.sesion_id]

    # Evitar continuar sesiones finalizadas
    if conversacion.estado in ["cancelacion", "asesor"]:
        return {
            "sesion_id": datos.sesion_id,
            "estado": conversacion.estado,
            "respuesta": "La conversacion ha finalizado."
        }

    respuesta = conversacion.procesar(datos.mensaje)

    return {
        "sesion_id": datos.sesion_id,
        "estado": conversacion.estado,
        "respuesta": respuesta
    }


@app.post("/conversacion/nps")
def conversar_nps(datos: SolicitudConversacion):

    # Iniciar una nueva conversacion
    if datos.sesion_id is None:

        if datos.mensaje is not None:
            raise HTTPException(
                status_code=422,
                detail="Para iniciar, no envies un mensaje."
            )

        sesion_id = str(uuid4())

        conversacion = ConversacionNPS()
        respuesta = conversacion.iniciar()

        sesiones_nps[sesion_id] = conversacion

        return {
            "sesion_id": sesion_id,
            "estado": conversacion.estado,
            "respuesta": respuesta,
            "folio": None
        }

    # Verificar que exista la sesion
    if datos.sesion_id not in sesiones_nps:
        raise HTTPException(
            status_code=404,
            detail="Sesion no encontrada."
        )

    # Validar el mensaje
    if not datos.mensaje or not datos.mensaje.strip():
        raise HTTPException(
            status_code=422,
            detail="Debes enviar un mensaje."
        )

    conversacion = sesiones_nps[datos.sesion_id]

    # Evitar continuar sesiones finalizadas
    if conversacion.estado in ["cancelacion", "asesor"]:
        return {
            "sesion_id": datos.sesion_id,
            "estado": conversacion.estado,
            "respuesta": "La conversacion ha finalizado.",
            "folio": conversacion.folio
        }

    respuesta = conversacion.procesar(datos.mensaje)

    return {
        "sesion_id": datos.sesion_id,
        "estado": conversacion.estado,
        "respuesta": respuesta,
        "folio": conversacion.folio
    }

