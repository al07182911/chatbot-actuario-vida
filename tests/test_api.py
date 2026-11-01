
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend import main


cliente = TestClient(main.app)


@pytest.fixture(autouse=True)
def limpiar_sesiones():
    main.sesiones_economia.clear()
    main.sesiones_beneficios.clear()
    main.sesiones_nps.clear()
    main.sesiones_unificadas.clear()
    yield
    main.sesiones_economia.clear()
    main.sesiones_beneficios.clear()
    main.sesiones_nps.clear()
    main.sesiones_unificadas.clear()


def respuesta_ia(motivos):
    return SimpleNamespace(
        output_text=json.dumps({
            "motivos": motivos,
            "explicacion": "Clasificacion simulada."
        })
    )


# P01: Estado de la API
def test_health():
    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "activo"


# P02: Cotizacion correcta
def test_cotizar():
    respuesta = cliente.post(
        "/cotizar",
        json={
            "suma_asegurada_actual": 1000000,
            "presupuesto_mensual": 900
        }
    )

    assert respuesta.status_code == 200
    assert (
        respuesta.json()["resultado"]["nueva_suma_asegurada"]
        == 600000
    )


# P03: Cotizacion invalida
def test_cotizar_invalido():
    respuesta = cliente.post(
        "/cotizar",
        json={
            "suma_asegurada_actual": -100,
            "presupuesto_mensual": 900
        }
    )

    assert respuesta.status_code == 422


# P04: Clasificacion mediante API
def test_chat_clasificacion():
    with patch.object(
        main.cliente_ia.responses,
        "create",
        return_value=respuesta_ia(["economia_personal"])
    ):
        respuesta = cliente.post(
            "/chat",
            json={
                "mensaje": "No puedo pagar mi seguro."
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.json()["motivos"] == [
        "economia_personal"
    ]


# P05: Error simulado de OpenAI
def test_chat_error_openai():
    with patch.object(
        main.cliente_ia.responses,
        "create",
        side_effect=Exception("Fallo simulado")
    ):
        respuesta = cliente.post(
            "/chat",
            json={
                "mensaje": "No puedo pagar mi seguro."
            }
        )

    assert respuesta.status_code == 503


# P06: Inicio de Ruta A
def test_inicio_economia():
    respuesta = cliente.post(
        "/conversacion/economia",
        json={}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "esperando_suma"


# P07: Ruta A con presupuesto
def test_flujo_economia():
    inicio = cliente.post(
        "/conversacion/economia",
        json={}
    )

    sesion = inicio.json()["sesion_id"]

    cliente.post(
        "/conversacion/economia",
        json={
            "sesion_id": sesion,
            "mensaje": "1000000"
        }
    )

    respuesta = cliente.post(
        "/conversacion/economia",
        json={
            "sesion_id": sesion,
            "mensaje": "900"
        }
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "propuesta"
    assert "$600,000.00" in respuesta.json()["respuesta"]


# P08: Consulta de beneficios
def test_flujo_beneficios():
    inicio = cliente.post(
        "/conversacion/beneficios",
        json={}
    )

    sesion = inicio.json()["sesion_id"]

    respuesta = cliente.post(
        "/conversacion/beneficios",
        json={
            "sesion_id": sesion,
            "mensaje": "VIDA-001"
        }
    )

    assert respuesta.status_code == 200
    assert "Asistencia funeraria" in respuesta.json()["respuesta"]
    assert "Promocion de bienestar" not in respuesta.json()["respuesta"]


# P09: Cancelacion en Ruta C
def test_cancelacion_nps():
    inicio = cliente.post(
        "/conversacion/nps",
        json={}
    )

    sesion = inicio.json()["sesion_id"]

    respuesta = cliente.post(
        "/conversacion/nps",
        json={
            "sesion_id": sesion,
            "mensaje": "cancelar"
        }
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "cancelacion"
    assert respuesta.json()["folio"] is None


# P10: Chat unificado
def test_chat_unificado():
    with patch.object(
        main.cliente_ia.responses,
        "create",
        return_value=respuesta_ia(["falta_utilidad"])
    ):
        respuesta = cliente.post(
            "/chat/unificado",
            json={
                "mensaje": "No veo beneficios en mi seguro."
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.json()["ruta_activa"] == "falta_utilidad"


# P11: Multicausalidad
def test_chat_multicausal():
    with patch.object(
        main.cliente_ia.responses,
        "create",
        return_value=respuesta_ia([
            "economia_personal",
            "mala_experiencia"
        ])
    ):
        respuesta = cliente.post(
            "/chat/unificado",
            json={
                "mensaje": (
                    "No puedo pagar mi seguro "
                    "y me atendieron mal."
                )
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "seleccion_ruta"
    assert len(respuesta.json()["motivos"]) == 2
