
import runpy
import signal
import subprocess

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


RUTA_SUPERVISOR = (
    Path(__file__).resolve().parent.parent
    / "start_render.py"
)


def ejecutar_supervisor(
    escenario,
    monkeypatch
):

    monkeypatch.setenv("PORT", "8501")
    monkeypatch.setenv(
        "BACKEND_URL",
        "http://127.0.0.1:8000"
    )

    backend = MagicMock()
    frontend = MagicMock()

    backend.poll.return_value = None
    frontend.poll.return_value = None

    respuesta = MagicMock()
    respuesta.__enter__.return_value.status = 200

    manejadores = {}

    def registrar_senal(senal, manejador):
        manejadores[senal] = manejador

    def simular_espera(segundos):

        if escenario == "fallo_arranque":
            return

        if escenario == "cierre_normal":
            manejadores[signal.SIGTERM]()

        elif escenario == "sigterm":
            manejadores[signal.SIGTERM](
                signal.SIGTERM, None
            )

        elif escenario == "sigint":
            manejadores[signal.SIGINT](
                signal.SIGINT, None
            )

        elif escenario == "detenidos":
            backend.poll.return_value = 0
            frontend.poll.return_value = 0

            manejadores[signal.SIGTERM](
                signal.SIGTERM, None
            )

        elif escenario == "timeout_cierre":
            frontend.wait.side_effect = (
                subprocess.TimeoutExpired(
                    cmd="streamlit",
                    timeout=10
                )
            )

            manejadores[signal.SIGTERM](
                signal.SIGTERM, None
            )

        else:
            raise AssertionError(
                "Espera inesperada en supervisor"
            )

    if escenario == "fallo_backend":
        backend.poll.return_value = 1

    if escenario == "fallo_frontend":
        frontend.poll.return_value = 1

    if escenario == "fallo_arranque":
        backend.poll.return_value = 1

    with patch(
        "subprocess.Popen",
        side_effect=[backend, frontend]
    ) as popen:

        with patch(
            "urllib.request.urlopen",
            return_value=respuesta
        ) as urlopen:

            if escenario == "fallo_arranque":
                urlopen.side_effect = (
                    ConnectionError(
                        "Backend no disponible"
                    )
                )

            with patch(
                "signal.signal",
                side_effect=registrar_senal
            ):

                with patch(
                    "time.sleep",
                    side_effect=simular_espera
                ):

                    with pytest.raises(
                        SystemExit
                    ) as salida:

                        runpy.run_path(
                            str(RUTA_SUPERVISOR),
                            run_name="__main__"
                        )

    return (
        salida.value.code,
        backend,
        frontend,
        popen
    )


def test_sup01_cierre_normal(monkeypatch):

    codigo, backend, frontend, _ = (
        ejecutar_supervisor(
            "cierre_normal",
            monkeypatch
        )
    )

    assert codigo == 0

    backend.terminate.assert_called_once()
    frontend.terminate.assert_called_once()


def test_sup02_sigterm(monkeypatch):

    codigo, _, _, _ = ejecutar_supervisor(
        "sigterm",
        monkeypatch
    )

    assert codigo == 0


def test_sup03_sigint(monkeypatch):

    codigo, _, _, _ = ejecutar_supervisor(
        "sigint",
        monkeypatch
    )

    assert codigo == 0


def test_sup04_fallo_arranque(monkeypatch):

    codigo, backend, _, popen = (
        ejecutar_supervisor(
            "fallo_arranque",
            monkeypatch
        )
    )

    assert codigo == 1
    assert popen.call_count == 1

    backend.terminate.assert_called_once()


def test_sup05_fallo_backend(monkeypatch):

    codigo, _, frontend, _ = (
        ejecutar_supervisor(
            "fallo_backend",
            monkeypatch
        )
    )

    assert codigo == 1

    frontend.terminate.assert_called_once()


def test_sup06_fallo_frontend(monkeypatch):

    codigo, backend, _, _ = (
        ejecutar_supervisor(
            "fallo_frontend",
            monkeypatch
        )
    )

    assert codigo == 1

    backend.terminate.assert_called_once()


def test_sup07_procesos_detenidos(monkeypatch):

    codigo, backend, frontend, _ = (
        ejecutar_supervisor(
            "detenidos",
            monkeypatch
        )
    )

    assert codigo == 0

    backend.terminate.assert_not_called()
    frontend.terminate.assert_not_called()


def test_sup08_timeout_cierre(monkeypatch):

    codigo, _, frontend, _ = (
        ejecutar_supervisor(
            "timeout_cierre",
            monkeypatch
        )
    )

    assert codigo == 0

    frontend.kill.assert_called_once()
