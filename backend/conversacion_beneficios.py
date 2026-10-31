
from backend.beneficios import consultar_beneficios


class ConversacionBeneficios:

    def __init__(self):
        self.estado = "inicio"
        self.id_poliza = None
        self.beneficios = []

    def iniciar(self):
        self.estado = "esperando_poliza"

        return (
            "Entiendo que no encuentras suficiente utilidad "
            "en tu seguro. Podemos revisar los beneficios "
            "asociados a tu poliza. "
            "¿Cual es el identificador de tu poliza? "
            "Puedes utilizar VIDA-001, VIDA-002 o VIDA-003. "
            "Tambien puedes solicitar un asesor o cancelar."
        )

    def procesar(self, mensaje):

        texto = mensaje.strip()
        opcion = texto.lower()

        if self.estado in ["cancelacion", "asesor"]:
            return "Esta conversacion ha finalizado."

        # Cancelacion disponible durante toda la conversacion
        if opcion in [
            "cancelar",
            "quiero cancelar",
            "continuar cancelacion",
            "continuar con la cancelacion"
        ]:
            self.estado = "cancelacion"
            return (
                "Puedes continuar con la cancelacion. "
                "Este prototipo no realiza cancelaciones reales."
            )

        # Solicitud de atencion humana
        if opcion in [
            "asesor",
            "hablar con un asesor",
            "atencion humana"
        ]:
            self.estado = "asesor"
            return (
                "Has solicitado atencion humana. "
                "En este prototipo no se conecta "
                "con un asesor real."
            )

        if self.estado == "esperando_poliza":

            resultado = consultar_beneficios(texto)

            if not resultado["encontrada"]:
                return (
                    "No encontramos esa poliza. "
                    "Puedes utilizar VIDA-001, VIDA-002 "
                    "o VIDA-003, solicitar un asesor "
                    "o continuar con la cancelacion."
                )

            self.id_poliza = resultado["id_poliza"]
            self.beneficios = resultado["beneficios"]
            self.estado = "beneficios_presentados"

            respuesta = (
                f"La poliza {self.id_poliza} tiene "
                "los siguientes beneficios vigentes "
                "en nuestro catalogo academico:\n\n"
            )

            if not self.beneficios:
                respuesta += (
                    "No se encontraron beneficios vigentes."
                )
            else:
                for numero, beneficio in enumerate(
                    self.beneficios, start=1
                ):
                    respuesta += (
                        f"{numero}. {beneficio['nombre']}: "
                        f"{beneficio['descripcion']}\n"
                    )

            respuesta += (
                "\nEstos beneficios son ficticios. "
                "¿Deseas mas informacion, hablar con "
                "un asesor o continuar con la cancelacion?"
            )

            return respuesta

        if self.estado == "beneficios_presentados":

            if opcion in [
                "mas informacion",
                "informacion",
                "beneficios"
            ]:
                return (
                    "La informacion disponible corresponde "
                    "al catalogo academico. "
                    "Puedes solicitar un asesor para "
                    "obtener informacion adicional."
                )

            return (
                "Puedes solicitar mas informacion, "
                "hablar con un asesor o cancelar."
            )

        return "Primero debemos iniciar la conversacion."
