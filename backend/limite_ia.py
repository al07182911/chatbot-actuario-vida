
import os
import time
from collections import deque
from threading import Lock


class LimiteIA:
    def __init__(self, max_solicitudes=10, ventana=3600):
        if max_solicitudes <= 0 or ventana <= 0:
            raise ValueError("Limites invalidos.")

        self.max_solicitudes = max_solicitudes
        self.ventana = ventana
        self.solicitudes = deque()
        self.lock = Lock()

    def consumir(self):
        ahora = time.monotonic()

        with self.lock:
            while (
                self.solicitudes
                and ahora - self.solicitudes[0] >= self.ventana
            ):
                self.solicitudes.popleft()

            if len(self.solicitudes) >= self.max_solicitudes:
                restante = max(
                    1,
                    int(
                        self.ventana
                        - (ahora - self.solicitudes[0])
                    ) + 1
                )

                return False, restante

            self.solicitudes.append(ahora)
            return True, 0


limite_ia = LimiteIA(
    max_solicitudes=int(
        os.getenv("MAX_SOLICITUDES_IA", "10")
    ),
    ventana=int(
        os.getenv("VENTANA_IA_SEGUNDOS", "3600")
    )
)
