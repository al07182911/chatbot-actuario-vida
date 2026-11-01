
import os
from pathlib import Path

from streamlit.testing.v1 import AppTest


RUTA_APP = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "app.py"
)


def test_seg03_sin_password(monkeypatch):

    # Eliminar la contraseña del entorno de prueba
    monkeypatch.delenv(
        "CHATBOT_ACCESS_PASSWORD",
        raising=False
    )

    app = AppTest.from_file(
        str(RUTA_APP),
        default_timeout=15
    )

    app.run()

    assert not app.exception

    mensajes_error = [
    str(elemento.value)
    for elemento in app.error
]

    assert any(
        "El acceso no esta configurado"
        in mensaje
        for mensaje in mensajes_error
    )

    # El chatbot no debe mostrar el campo de mensajes
    assert len(app.chat_input) == 0


def test_pantalla_de_acceso(monkeypatch):

    monkeypatch.setenv(
        "CHATBOT_ACCESS_PASSWORD",
        "clave-ficticia-para-pruebas"
    )

    app = AppTest.from_file(
        str(RUTA_APP),
        default_timeout=15
    )

    app.run()

    assert not app.exception

    # Debe aparecer el formulario de contraseña
    assert len(app.text_input) >= 1

    # No debe aparecer el chat antes de autenticarse
    assert len(app.chat_input) == 0
