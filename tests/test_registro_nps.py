
import pytest

from pydantic import ValidationError

from backend.registro_nps import (
    DatosCasoNPS,
    registrar_caso_nps,
    registro_nps
)


@pytest.fixture(autouse=True)
def limpiar_registro():
    registro_nps.clear()
    yield
    registro_nps.clear()


def crear_datos_validos():
    return DatosCasoNPS(
        descripcion=(
            "El cliente reporta un cobro duplicado "
            "en su seguro de vida."
        ),
        categorias=["problemas_cobro"],
        areas_relacionadas=["Cobranza"],
        resumen="Posible cobro duplicado."
    )


def test_registro_correcto():
    caso = registrar_caso_nps(
        crear_datos_validos()
    )

    assert caso["estado"] == "pendiente_revision"
    assert caso["tipo"] == "simulacion_academica"


def test_folio_generado():
    caso = registrar_caso_nps(
        crear_datos_validos()
    )

    assert caso["folio"].startswith("NPS-")
    assert caso["folio"] in registro_nps


def test_folios_diferentes():
    datos = crear_datos_validos()

    caso1 = registrar_caso_nps(datos)
    caso2 = registrar_caso_nps(datos)

    assert caso1["folio"] != caso2["folio"]


def test_fecha_registro():
    caso = registrar_caso_nps(
        crear_datos_validos()
    )

    assert caso["fecha_registro"]
    assert "T" in caso["fecha_registro"]


def test_categoria_invalida():
    datos = DatosCasoNPS(
        descripcion="El cliente reporta mala atencion.",
        categorias=["categoria_inexistente"],
        areas_relacionadas=["Operaciones"],
        resumen="Problema de servicio."
    )

    with pytest.raises(ValueError):
        registrar_caso_nps(datos)


def test_descripcion_vacia():
    with pytest.raises(ValidationError):
        DatosCasoNPS(
            descripcion="",
            categorias=["mala_atencion"],
            areas_relacionadas=["Atencion a clientes"],
            resumen="Mala atencion reportada."
        )


def test_area_invalida():
    datos = DatosCasoNPS(
        descripcion="El cliente reporta una demora.",
        categorias=["tiempo_respuesta"],
        areas_relacionadas=["Area inexistente"],
        resumen="Demora en la atencion."
    )

    with pytest.raises(ValueError):
        registrar_caso_nps(datos)
