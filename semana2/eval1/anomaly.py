from dataclasses import dataclass

from semana2.eval1.reading import SensorReading


# Clases de apoyo -------------------------------------
@dataclass
class AnomalyType:
    """Clase para determinar el tipo de anomalia"""

    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"


class AnomalyResult:
    """Clase para almacenar el resultado de la deteccion"""

    def __init__(
        self,
        is_anomaly: bool,
        anomaly_type: str | None,
        sensor_id: str,
        value: float,
    ):
        self.is_anomaly = is_anomaly
        self.anomaly_type = anomaly_type
        self.sensor_id = sensor_id
        self.value = value


# -----------------------------------------------------


# Clases de negocio -----------------------------------
class AnomalyDetector:
    """Clase para detectar anomalias en las lecturas"""

    def evaluate(self, reading: SensorReading) -> AnomalyResult:
        if reading.value > 35.0:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_type=AnomalyType.HIGH_TEMPERATURE,
                sensor_id=reading.sensor_id,
                value=reading.value,
            )
        else:
            return AnomalyResult(
                is_anomaly=False,
                anomaly_type=None,
                sensor_id=reading.sensor_id,
                value=reading.value,
            )


# -----------------------------------------------------
