
from backend.conversacion_economia import ConversacionEconomia
from backend.conversacion_beneficios import ConversacionBeneficios
from backend.conversacion_nps import ConversacionNPS


RUTAS = {
    "economia_personal": ConversacionEconomia,
    "falta_utilidad": ConversacionBeneficios,
    "mala_experiencia": ConversacionNPS
}

NOMBRES_RUTAS = {
    "economia_personal": "Economia personal",
    "falta_utilidad": "Beneficios del seguro",
    "mala_experiencia": "Mala experiencia de servicio"
}


class CoordinadorChatbot:

    def __init__(self):
        self.estado = "inicio"
        self.motivos = []
        self.ruta_activa = None
        self.conversacion = None

    def iniciar_ruta(self, motivo):

        if motivo not in RUTAS:
            raise ValueError("Ruta no reconocida.")

        self.ruta_activa = motivo
        self.conversacion = RUTAS[motivo]()
        self.estado = "ruta_activa"

        return self.conversacion.iniciar()

    def recibir_clasificacion(self, motivos):

        if self.estado != "inicio":
            raise ValueError(
                "La conversacion ya fue clasificada."
            )

        if not isinstance(motivos, list):
            raise ValueError("Clasificacion invalida.")

        if (
            any(m not in RUTAS for m in motivos)
            or len(motivos) != len(set(motivos))
        ):
            raise ValueError("Motivos no validos.")

        self.motivos = motivos.copy()

        if len(motivos) == 0:
            self.estado = "sin_motivo"

            return (
                "Entiendo que deseas cancelar tu seguro. "
                "¿El motivo esta relacionado con tu "
                "economia personal, los beneficios "
                "del seguro o una mala experiencia? "
                "Tambien puedes continuar con la cancelacion."
            )

        if len(motivos) == 1:
            return self.iniciar_ruta(motivos[0])

        self.estado = "seleccion_ruta"

        opciones = "\n".join(
            f"{numero}. {NOMBRES_RUTAS[motivo]}"
            for numero, motivo in enumerate(
                motivos, start=1
            )
        )

        return (
            "Identifique varios motivos de cancelacion. "
            "¿Cual deseas atender primero?\n"
            f"{opciones}\n"
            "Escribe el numero de la opcion. "
            "Tambien puedes solicitar un asesor o cancelar."
        )

    def procesar(self, mensaje):

        texto = mensaje.strip()
        opcion = texto.lower()

        if self.estado == "finalizada":
            return "Esta conversacion ha finalizado."

        # Controles globales de salida
        if opcion in [
            "cancelar",
            "quiero cancelar",
            "continuar cancelacion",
            "continuar con la cancelacion"
        ]:
            self.estado = "finalizada"
            return (
                "Puedes continuar con la cancelacion. "
                "Este prototipo academico no realiza "
                "cancelaciones reales."
            )

        if opcion in [
            "asesor",
            "hablar con un asesor",
            "atencion humana"
        ]:
            self.estado = "finalizada"
            return (
                "Has solicitado atencion humana. "
                "Este prototipo no conecta con asesores reales."
            )

        if self.estado == "seleccion_ruta":

            if not texto.isdigit():
                return (
                    "Selecciona una de las opciones "
                    "indicando su numero."
                )

            numero = int(texto)

            if numero < 1 or numero > len(self.motivos):
                return "La opcion seleccionada no es valida."

            motivo = self.motivos[numero - 1]

            return self.iniciar_ruta(motivo)

        if self.estado == "sin_motivo":
            return (
                "Por favor, indica si el motivo esta "
                "relacionado con economia personal, "
                "beneficios o mala experiencia. "
                "Tambien puedes solicitar un asesor "
                "o continuar con la cancelacion."
            )

        if self.estado == "ruta_activa":

            respuesta = self.conversacion.procesar(texto)

            if self.conversacion.estado in [
                "cancelacion", "asesor"
            ]:
                self.estado = "finalizada"

            return respuesta

        return "Primero debemos identificar el motivo."
