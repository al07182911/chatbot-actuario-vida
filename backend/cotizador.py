from pydantic import BaseModel, Field
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

# Tarifa academica por cada $1,000 de suma asegurada
TARIFA_POR_MILLAR = Decimal("1.50")
MILLAR = Decimal("1000")


class DatosCotizacion(BaseModel):
    suma_asegurada_actual: Decimal = Field(gt=0)
    presupuesto_mensual: Decimal = Field(gt=0)


def calcular_alternativa(datos: DatosCotizacion):

    suma_actual = datos.suma_asegurada_actual
    presupuesto = datos.presupuesto_mensual

    prima_actual = (
        suma_actual / MILLAR * TARIFA_POR_MILLAR
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if presupuesto >= prima_actual:
        return {
            "prima_actual": float(prima_actual),
            "suma_asegurada_actual": float(suma_actual),
            "nueva_suma_asegurada": float(suma_actual),
            "nueva_prima": float(prima_actual),
            "ahorro_mensual": 0.0,
            "reduccion_cobertura_pct": 0.0,
            "mensaje": "El presupuesto permite mantener la cobertura actual."
        }

    # Calcular cobertura que puede pagar el cliente
    nueva_suma = (
        presupuesto / TARIFA_POR_MILLAR * MILLAR
    )

    # Redondear hacia abajo a pesos enteros
    nueva_suma = nueva_suma.quantize(
        Decimal("1"),
        rounding=ROUND_DOWN
    )

    nueva_prima = (
        nueva_suma / MILLAR * TARIFA_POR_MILLAR
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    ahorro = prima_actual - nueva_prima

    reduccion = (
        (Decimal("1") - nueva_suma / suma_actual)
        * Decimal("100")
    )

    return {
        "prima_actual": float(prima_actual),
        "suma_asegurada_actual": float(suma_actual),
        "nueva_suma_asegurada": float(nueva_suma),
        "nueva_prima": float(nueva_prima),
        "ahorro_mensual": float(ahorro),
        "reduccion_cobertura_pct": round(float(reduccion), 2),
        "mensaje": "Alternativa academica calculada correctamente."
    }
