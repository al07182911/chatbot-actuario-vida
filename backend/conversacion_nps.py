
from backend.clasificador_nps import clasificar_insatisfaccion
from backend.registro_nps import (
    DatosCasoNPS,
    registrar_caso_nps
)
from backend.limite_ia import CuotaIAAgotada


class ConversacionNPS:

    def __init__(self, clasificador=None):
        self.estado = "inicio"
        self.folio = None
        self.caso = None
        self.clasificador = (
            clasificador or clasificar_insatisfaccion
        )

    def iniciar(self):
        self.estado = "esperando_descripcion"

        return (
            "Lamento que hayas tenido una experiencia "
            "insatisfactoria. Para comprender lo ocurrido, "
            "¿podrias contarme que problema tuviste? "
            "No incluyas nombres, telefonos ni datos personales. "
            "Tambien puedes solicitar un asesor o cancelar."
        )

    def procesar(self, mensaje):

        if self.estado in ["cancelacion", "asesor"]:
            return "Esta conversacion ha finalizado."

        if not isinstance(mensaje, str):
            return "Por favor, escribe tu mensaje."

        texto = mensaje.strip()
        opcion = texto.lower()

        # Cancelacion disponible durante la conversacion
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
                "En esta demostracion no se conecta "
                "con un asesor real."
            )

        if self.estado == "esperando_descripcion":

            if len(texto) < 10 or len(texto) > 2000:
                return (
                    "Por favor, describe el problema "
                    "en un texto de 10 a 2000 caracteres."
                )

            try:
                resultado = self.clasificador(texto)

                if not resultado["categorias"]:
                    return (
                        "No pude identificar una causa concreta "
                        "de insatisfaccion. ¿Podrias explicar "
                        "con mas detalle lo ocurrido? "
                        "Tambien puedes solicitar un asesor "
                        "o continuar con la cancelacion."
                    )

                datos = DatosCasoNPS(
                    descripcion=texto,
                    categorias=resultado["categorias"],
                    areas_relacionadas=(
                        resultado["areas_relacionadas"]
                        or ["Por determinar"]
                    ),
                    resumen=resultado["resumen"]
                )

                self.caso = registrar_caso_nps(datos)
                self.folio = self.caso["folio"]
                self.estado = "caso_registrado"

                categorias = ", ".join(
                    self.caso["categorias"]
                ).replace("_", " ")

                areas = ", ".join(
                    self.caso["areas_relacionadas"]
                )

                return (
                    "Gracias por compartir lo ocurrido.\n\n"
                    f"Folio academico: {self.folio}\n"
                    f"Causas identificadas: {categorias}\n"
                    f"Areas sugeridas: {areas}\n"
                    f"Resumen: {self.caso['resumen']}\n"
                    "Estado: pendiente de revision simulada.\n\n"
                    "Este registro es exclusivamente academico "
                    "y no se ha enviado a una aseguradora.\n"
                    "¿Deseas solicitar un asesor o continuar "
                    "con la cancelacion?"
                )

            except CuotaIAAgotada:
                raise

            except Exception:
                return (
                    "No fue posible analizar o registrar "
                    "el caso en este momento. "
                    "Puedes intentarlo nuevamente, "
                    "solicitar un asesor o cancelar."
                )

        if self.estado == "caso_registrado":
            return (
                f"Tu folio academico es {self.folio}. "
                "El caso permanece pendiente de revision "
                "simulada. Puedes solicitar un asesor "
                "o continuar con la cancelacion."
            )

        return "Primero debemos iniciar la conversacion."
