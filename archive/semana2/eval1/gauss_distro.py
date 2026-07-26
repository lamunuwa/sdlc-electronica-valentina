import datetime
import random
from typing import Any


# Clases de error -------------------------------------
class InvalidCycleCountError(Exception): ...


# -----------------------------------------------------


# Clases de negocio -----------------------------------
class SensorSimulator:
    """Clase que simula la generacion de lecturas"""

    def __init__(self, num_sensores: int, media: float, desviacion: float):
        self.num_sensores = num_sensores
        self.media = media
        self.desviacion = desviacion

    def ejecutar_simulacion(self, ciclos: int, intervalo: int) -> list[dict[str, Any]]:
        if ciclos <= 0:
            raise InvalidCycleCountError

        lecturas = []
        tiempo_base = datetime.datetime.now()

        for ciclo in range(ciclos):
            for sensor_id in range(self.num_sensores):
                lectura = {
                    "sensor_id": sensor_id,
                    "temperatura": random.gauss(self.media, self.desviacion),
                    "timestamp": tiempo_base + datetime.timedelta(seconds=ciclo * intervalo),
                }
                lecturas.append(lectura)

        return lecturas


# -----------------------------------------------------
