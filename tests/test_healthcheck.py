
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest
import healthcheck


def test_hc01_respuesta_http_200():

    respuesta = MagicMock()
    respuesta.__enter__.return_value.status = 200

    with patch(
        "healthcheck.urllib.request.urlopen",
        return_value=respuesta
    ) as llamada:

        resultado = healthcheck.comprobar_servicio(
            "FastAPI",
            "http://127.0.0.1:8000/health"
        )

    assert resultado is True

    llamada.assert_called_once_with(
        "http://127.0.0.1:8000/health",
        timeout=3
    )


def test_hc02_respuesta_http_503():

    error = HTTPError(
        "http://127.0.0.1:8000/health",
        503,
        "Service Unavailable",
        None,
        None
    )

    with patch(
        "healthcheck.urllib.request.urlopen",
        side_effect=error
    ):

        resultado = healthcheck.comprobar_servicio(
            "FastAPI",
            "http://127.0.0.1:8000/health"
        )

    assert resultado is False


def test_hc03_timeout():

    with patch(
        "healthcheck.urllib.request.urlopen",
        side_effect=TimeoutError("Timeout simulado")
    ):

        resultado = healthcheck.comprobar_servicio(
            "FastAPI",
            "http://127.0.0.1:8000/health"
        )

    assert resultado is False


def test_hc04_error_conexion():

    with patch(
        "healthcheck.urllib.request.urlopen",
        side_effect=URLError("Conexion rechazada")
    ):

        resultado = healthcheck.comprobar_servicio(
            "FastAPI",
            "http://127.0.0.1:8000/health"
        )

    assert resultado is False


@pytest.mark.parametrize(
    "backend_ok,frontend_ok,codigo_esperado",
    [
        (True, True, 0),
        (False, True, 1),
        (True, False, 1),
        (False, False, 1)
    ],
    ids=["HC-05", "HC-06", "HC-07", "HC-08"]
)
def test_estado_combinado(
    backend_ok,
    frontend_ok,
    codigo_esperado
):

    with patch(
        "healthcheck.comprobar_servicio",
        side_effect=[backend_ok, frontend_ok]
    ) as llamada:

        resultado = healthcheck.main()

    assert resultado == codigo_esperado
    assert llamada.call_count == 2


def test_hc09_puerto_personalizado(monkeypatch):

    monkeypatch.setenv("PORT", "10000")

    with patch(
        "healthcheck.comprobar_servicio",
        return_value=True
    ) as llamada:

        assert healthcheck.main() == 0

    llamada.assert_any_call(
        "FastAPI",
        "http://127.0.0.1:8000/health"
    )

    llamada.assert_any_call(
        "Streamlit",
        "http://127.0.0.1:10000/_stcore/health"
    )


def test_hc10_puerto_predeterminado(monkeypatch):

    monkeypatch.delenv("PORT", raising=False)

    with patch(
        "healthcheck.comprobar_servicio",
        return_value=True
    ) as llamada:

        assert healthcheck.main() == 0

    llamada.assert_any_call(
        "Streamlit",
        "http://127.0.0.1:8501/_stcore/health"
    )
