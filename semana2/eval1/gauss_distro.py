from typing import Any


class InvalidCycleCountError(Exception): ...


class SensorSimulator:
    """Clase que genera las lecturas simuladas"""

    def __init__(self, num_sensores: int, media: float, desviacion: float):
        self.num_sensores = num_sensores
        self.media = media
        self.desviacion = desviacion

    def ejecutar_simulacion(self, ciclos: int, intervalo: int) -> list[dict[str, Any]]:
        raise NotImplementedError
