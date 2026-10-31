from decimal import Decimal, InvalidOperation
from backend.cotizador import (
    DatosCotizacion,
    calcular_alternativa
)

class ConversacionEconomia:

    def __init__(self):
        self.estado = "inicio"
        self.suma_asegurada = None
        self.resultado = None

    def iniciar(self):
        self.estado = "esperando_suma"
        return (
            "Entiendo que deseas reducir el costo de tu seguro. "
            "Podemos explorar una alternativa academica "
            "sin compromiso. "
            "¿Cual es tu suma asegurada actual en pesos?"
        )

    def procesar(self, mensaje):

        texto = mensaje.strip()

        if texto.lower() in [
            "cancelar",
            "quiero cancelar",
            "continuar cancelacion"
        ]:
            self.estado = "cancelacion"
            return (
                "Puedes continuar con tu solicitud de "
                "cancelacion. En este prototipo no se "
                "realizan cancelaciones reales."
            )

        if self.estado == "esperando_suma":

            try:
                suma = Decimal(
                    texto.replace(",", "").replace("$", "")
                )

                if not suma.is_finite() or suma <= 0:
                    raise ValueError()

            except (InvalidOperation, ValueError):
                return (
                    "Por favor, indica una suma asegurada "
                    "valida, mayor que cero."
                )

            self.suma_asegurada = suma

            prima = (
                suma / Decimal("1000")
                * Decimal("1.50")
            )

            self.estado = "esperando_presupuesto"

            return (
                f"Con una suma asegurada de ${suma:,.2f}, "
                f"tu prima mensual simulada es "
                f"${prima:,.2f}. "
                "¿Cuanto puedes pagar mensualmente?"
            )

        if self.estado == "esperando_presupuesto":

            try:
                presupuesto = Decimal(
                    texto.replace(",", "").replace("$", "")
                )

                if not presupuesto.is_finite() or presupuesto <= 0:
                    raise ValueError()

            except (InvalidOperation, ValueError):
                return (
                    "Indica un presupuesto mensual "
                    "valido, mayor que cero."
                )

            datos = DatosCotizacion(
                suma_asegurada_actual=self.suma_asegurada,
                presupuesto_mensual=presupuesto
            )

            self.resultado = calcular_alternativa(datos)
            self.estado = "propuesta"

            r = self.resultado

            return (
                "Resultado de la simulacion academica:\n"
                f"Prima actual: ${r['prima_actual']:,.2f}\n"
                f"Nueva suma asegurada: "
                f"${r['nueva_suma_asegurada']:,.2f}\n"
                f"Nueva prima: ${r['nueva_prima']:,.2f}\n"
                f"Ahorro mensual: ${r['ahorro_mensual']:,.2f}\n"
                f"Reduccion de cobertura: "
                f"{r['reduccion_cobertura_pct']}%\n\n"
                "La reduccion de prima implica una "
                "menor proteccion. "
                "¿Deseas explorar esta alternativa "
                "o continuar con la cancelacion?"
            )

        if self.estado == "propuesta":
            return (
                "Esta es una simulacion academica. "
                "Para modificar una poliza real se "
                "requiere validacion de la aseguradora. "
                "Puedes solicitar atencion humana "
                "o continuar con la cancelacion."
            )

        return "Primero debemos iniciar la conversacion."
