
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.limite_ia import CuotaIAAgotada


cliente = TestClient(main.app)


@pytest.fixture(autouse=True)
def limpiar_sesiones():
    main.sesiones_nps.clear()
    main.sesiones_unificadas.clear()

    yield

    main.sesiones_nps.clear()
    main.sesiones_unificadas.clear()


def simular_cuota_agotada():
    raise CuotaIAAgotada(120)


# NPS-429-01
def test_limite_endpoint_nps():

    inicio = cliente.post(
        "/conversacion/nps",
        json={}
    )

    assert inicio.status_code == 200

    sesion = inicio.json()["sesion_id"]

    with patch(
        "backend.conversacion_nps.clasificar_insatisfaccion",
        side_effect=simular_cuota_agotada
    ):
        respuesta = cliente.post(
            "/conversacion/nps",
            json={
                "sesion_id": sesion,
                "mensaje": (
                    "Llevo tres semanas esperando "
                    "una respuesta y nadie resuelve "
                    "mi problema."
                )
            }
        )

    assert respuesta.status_code == 429


# NPS-429-02
def test_limite_chat_unificado():

    coordinador = main.CoordinadorChatbot()

    coordinador.recibir_clasificacion([
        "mala_experiencia"
    ])

    sesion_id = "sesion-nps-prueba"

    main.sesiones_unificadas[sesion_id] = coordinador

    with patch(
        "backend.conversacion_nps.clasificar_insatisfaccion",
        side_effect=simular_cuota_agotada
    ):
        respuesta = cliente.post(
            "/chat/unificado",
            json={
                "sesion_id": sesion_id,
                "mensaje": (
                    "El asesor me dio informacion "
                    "incorrecta y nunca resolvio "
                    "mi solicitud."
                )
            }
        )

    assert respuesta.status_code == 429


# NPS-429-03
def test_retry_after_nps():

    inicio = cliente.post(
        "/conversacion/nps",
        json={}
    )

    sesion = inicio.json()["sesion_id"]

    with patch(
        "backend.conversacion_nps.clasificar_insatisfaccion",
        side_effect=simular_cuota_agotada
    ):
        respuesta = cliente.post(
            "/conversacion/nps",
            json={
                "sesion_id": sesion,
                "mensaje": (
                    "No han resuelto mi reclamacion "
                    "despues de varias semanas."
                )
            }
        )

    assert respuesta.status_code == 429
    assert int(
        respuesta.headers["retry-after"]
    ) == 120


# NPS-429-04
def test_cancelacion_sin_consumir_ia():

    inicio = cliente.post(
        "/conversacion/nps",
        json={}
    )

    sesion = inicio.json()["sesion_id"]

    with patch(
        "backend.conversacion_nps.clasificar_insatisfaccion",
        side_effect=AssertionError(
            "No debe consultar OpenAI"
        )
    ) as clasificador:

        respuesta = cliente.post(
            "/conversacion/nps",
            json={
                "sesion_id": sesion,
                "mensaje": "cancelar"
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "cancelacion"
    clasificador.assert_not_called()
