
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend import limite_ia as modulo_limite


cliente = TestClient(main.app)


@pytest.fixture
def cuota_controlada(monkeypatch):
    # Crear un contador independiente para cada prueba
    contador = modulo_limite.LimiteIA(
        max_solicitudes=1,
        ventana=3600
    )

    monkeypatch.setattr(
        modulo_limite,
        "limite_ia",
        contador
    )

    main.sesiones_unificadas.clear()

    yield contador

    main.sesiones_unificadas.clear()


def respuesta_simulada():
    return SimpleNamespace(
        output_text=json.dumps({
            "motivos": ["economia_personal"],
            "explicacion": "Problema economico."
        })
    )


def test_primera_solicitud_permitida(cuota_controlada):

    with patch.object(
        main.cliente_ia.responses,
        "create",
        return_value=respuesta_simulada()
    ) as llamada:

        respuesta = cliente.post(
            "/chat/unificado",
            json={
                "mensaje": "No puedo pagar mi seguro."
            }
        )

    assert respuesta.status_code == 200
    assert llamada.call_count == 1


def test_segunda_solicitud_rechazada(cuota_controlada):

    with patch.object(
        main.cliente_ia.responses,
        "create",
        return_value=respuesta_simulada()
    ) as llamada:

        primera = cliente.post(
            "/chat/unificado",
            json={
                "mensaje": "No puedo pagar mi seguro."
            }
        )

        segunda = cliente.post(
            "/chat/unificado",
            json={
                "mensaje": "Tengo problemas economicos."
            }
        )

    assert primera.status_code == 200
    assert segunda.status_code == 429
    assert llamada.call_count == 1


def test_encabezado_retry_after(cuota_controlada):

    with patch.object(
        main.cliente_ia.responses,
        "create",
        return_value=respuesta_simulada()
    ):

        cliente.post(
            "/chat/unificado",
            json={
                "mensaje": "No puedo pagar mi seguro."
            }
        )

        respuesta = cliente.post(
            "/chat/unificado",
            json={
                "mensaje": "No puedo pagar la prima."
            }
        )

    assert respuesta.status_code == 429
    assert "retry-after" in respuesta.headers
    assert int(respuesta.headers["retry-after"]) > 0


def test_cancelacion_no_consume_cuota(cuota_controlada):

    with patch.object(
        main.cliente_ia.responses,
        "create"
    ) as llamada:

        respuesta = cliente.post(
            "/chat/unificado",
            json={
                "mensaje": "cancelar"
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "finalizada"
    assert llamada.call_count == 0
    assert len(cuota_controlada.solicitudes) == 0
