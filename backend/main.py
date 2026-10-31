from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Chatbot Actuario Vida",
    description="API academica para la atencion de solicitudes de cancelacion de seguros de vida",
    version="0.1.0"
)

class MensajeCliente(BaseModel):
    mensaje: str

@app.get("/health")
def verificar_estado():
    return {
        "estado": "activo",
        "aplicacion": "Chatbot Actuario Vida",
        "version": "0.1.0"
    }

@app.post("/chat")
def procesar_mensaje(datos: MensajeCliente):
    return {
        "mensaje_recibido": datos.mensaje,
        "respuesta": "Mensaje recibido correctamente.",
        "estado": "procesado"
    }
