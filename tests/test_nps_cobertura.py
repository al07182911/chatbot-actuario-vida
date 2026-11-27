
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from backend.clasificador_nps import clasificar_insatisfaccion
from backend.conversacion_nps import ConversacionNPS
from backend.limite_ia import CuotaIAAgotada


@pytest.mark.parametrize("mensaje", [
    None,
    123,
    [],
    {},
    "corto",
    "x" * 2001
])
def test_clasificador_rechaza_entradas_invalidas(mensaje):
    with pytest.raises(ValueError):
        clasificar_insatisfaccion(mensaje)


def test_clasificador_respuesta_valida():
    datos = {
        "categorias": ["mala_atencion"],
        "areas_relacionadas": ["Atencion a clientes"],
        "resumen": "El cliente reporta mala atencion."
    }

    respuesta = SimpleNamespace(
        output_text=json.dumps(datos)
    )

    with patch(
        "backend.clasificador_nps.OpenAI"
    ) as cliente_mock, patch(
        "backend.clasificador_nps.ejecutar_con_limite",
        return_value=respuesta
    ):
        resultado = clasificar_insatisfaccion(
            "Recibi una atencion deficiente."
        )

    assert resultado == datos
    cliente_mock.assert_called_once()


@pytest.mark.parametrize("datos", [
    {
        "categorias": ["categoria_invalida"],
        "areas_relacionadas": ["Operaciones"],
        "resumen": "Descripcion valida"
    },
    {
        "categorias": ["mala_atencion", "mala_atencion"],
        "areas_relacionadas": ["Operaciones"],
        "resumen": "Descripcion valida"
    },
    {
        "categorias": ["mala_atencion"],
        "areas_relacionadas": ["Area inventada"],
        "resumen": "Descripcion valida"
    },
    {
        "categorias": ["mala_atencion"],
        "areas_relacionadas": ["Operaciones"],
        "resumen": " "
    }
])
def test_clasificador_rechaza_respuestas_invalidas(datos):
    respuesta = SimpleNamespace(
        output_text=json.dumps(datos)
    )

    with patch(
        "backend.clasificador_nps.OpenAI"
    ), patch(
        "backend.clasificador_nps.ejecutar_con_limite",
        return_value=respuesta
    ):
        with pytest.raises(ValueError):
            clasificar_insatisfaccion(
                "El servicio fue insatisfactorio."
            )


def test_conversacion_solicitud_asesor():
    conversacion = ConversacionNPS()
    conversacion.iniciar()

    respuesta = conversacion.procesar("asesor")

    assert conversacion.estado == "asesor"
    assert "atencion humana" in respuesta.lower()
    assert "finalizado" in conversacion.procesar(
        "otro mensaje"
    ).lower()


def test_conversacion_entrada_no_textual():
    conversacion = ConversacionNPS()
    conversacion.iniciar()

    respuesta = conversacion.procesar(None)

    assert "escribe" in respuesta.lower()


def test_conversacion_descripcion_invalida():
    conversacion = ConversacionNPS()
    conversacion.iniciar()

    respuesta = conversacion.procesar("corto")

    assert "10 a 2000" in respuesta


def test_conversacion_sin_categorias():
    clasificador = Mock(return_value={
        "categorias": [],
        "areas_relacionadas": [],
        "resumen": "Sin causa identificable."
    })

    conversacion = ConversacionNPS(
        clasificador=clasificador
    )
    conversacion.iniciar()

    respuesta = conversacion.procesar(
        "No tengo claro que sucedio."
    )

    assert "mas detalle" in respuesta.lower()
    assert conversacion.estado == "esperando_descripcion"


def test_conversacion_registro_exitoso():
    clasificador = Mock(return_value={
        "categorias": ["mala_atencion"],
        "areas_relacionadas": ["Atencion a clientes"],
        "resumen": "El cliente reporta mala atencion."
    })

    conversacion = ConversacionNPS(
        clasificador=clasificador
    )
    conversacion.iniciar()

    respuesta = conversacion.procesar(
        "Recibi una atencion deficiente."
    )

    assert conversacion.estado == "caso_registrado"
    assert conversacion.folio is not None
    assert "Folio academico" in respuesta

    seguimiento = conversacion.procesar(
        "Quiero conocer el estado"
    )

    assert conversacion.folio in seguimiento


def test_conversacion_error_clasificador():
    clasificador = Mock(
        side_effect=RuntimeError("Error simulado")
    )

    conversacion = ConversacionNPS(
        clasificador=clasificador
    )
    conversacion.iniciar()

    respuesta = conversacion.procesar(
        "La atencion fue muy deficiente."
    )

    assert "No fue posible" in respuesta


def test_conversacion_propaga_cuota_agotada():
    clasificador = Mock(
        side_effect=CuotaIAAgotada(60)
    )

    conversacion = ConversacionNPS(
        clasificador=clasificador
    )
    conversacion.iniciar()

    with pytest.raises(CuotaIAAgotada):
        conversacion.procesar(
            "La atencion fue muy deficiente."
        )


def test_conversacion_antes_de_iniciar():
    conversacion = ConversacionNPS()

    respuesta = conversacion.procesar(
        "Necesito ayuda con mi seguro"
    )

    assert "iniciar" in respuesta.lower()
