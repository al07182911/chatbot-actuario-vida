
import pytest

from pydantic import ValidationError

from backend.cotizador import (
    DatosCotizacion,
    calcular_alternativa
)


def test_cotizacion_normal():
    datos = DatosCotizacion(
        suma_asegurada_actual=1000000,
        presupuesto_mensual=900
    )

    resultado = calcular_alternativa(datos)

    assert resultado["prima_actual"] == 1500
    assert resultado["nueva_suma_asegurada"] == 600000
    assert resultado["nueva_prima"] == 900
    assert resultado["ahorro_mensual"] == 600
    assert resultado["reduccion_cobertura_pct"] == 40


def test_reduccion_cincuenta_por_ciento():
    datos = DatosCotizacion(
        suma_asegurada_actual=500000,
        presupuesto_mensual=375
    )

    resultado = calcular_alternativa(datos)

    assert resultado["prima_actual"] == 750
    assert resultado["nueva_suma_asegurada"] == 250000
    assert resultado["nueva_prima"] == 375


def test_presupuesto_suficiente():
    datos = DatosCotizacion(
        suma_asegurada_actual=1000000,
        presupuesto_mensual=2000
    )

    resultado = calcular_alternativa(datos)

    assert resultado["nueva_suma_asegurada"] == 1000000
    assert resultado["nueva_prima"] == 1500
    assert resultado["ahorro_mensual"] == 0


def test_presupuesto_reducido():
    datos = DatosCotizacion(
        suma_asegurada_actual=200000,
        presupuesto_mensual=150
    )

    resultado = calcular_alternativa(datos)

    assert resultado["nueva_suma_asegurada"] == 100000
    assert resultado["nueva_prima"] == 150


@pytest.mark.parametrize(
    "suma,presupuesto",
    [
        (-1000, 900),
        (0, 900),
        (1000000, -100),
        (1000000, 0)
    ]
)
def test_valores_invalidos(suma, presupuesto):

    with pytest.raises(ValidationError):
        DatosCotizacion(
            suma_asegurada_actual=suma,
            presupuesto_mensual=presupuesto
        )
