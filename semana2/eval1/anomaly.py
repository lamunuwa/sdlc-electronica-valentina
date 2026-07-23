from dataclasses import dataclass
from enum import Enum

from semana2.eval1.reading import SensorReading

# Clases de apoyo -------------------------------------


class AnomalyType(Enum):
    """Clase para determinar el tipo de anomalia"""

    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"
    TOO_FAR = "TOO_FAR"
    # HIGH_HUMIDITY = "HIGH_HUMIDITY"
    # TOO_SLOW = "TOO_SLOW"


@dataclass
class ThresholdConfig:
    """Clase para configurar los umbrales"""

    sensor_id: str
    max_value: float
    anomaly_type: AnomalyType | None = None


class AnomalyResult:
    """Clase para almacenar el resultado de la deteccion"""

    def __init__(
        self,
        is_anomaly: bool,
        anomaly_type: AnomalyType | None,
        sensor_id: str,
        value: float,
    ):
        self.is_anomaly = is_anomaly
        self.anomaly_type = anomaly_type
        self.sensor_id = sensor_id
        self.value = value


# -----------------------------------------------------


# Clases de negocio -----------------------------------


class ThresholdConfigManager:
    """Clase para configurar los umbrales"""

    def __init__(self) -> None:
        self.thresholds: dict[str, ThresholdConfig] = {}

    def configure_threshold(
        self, sensor_id: str, max_value: float, anomaly_type: AnomalyType
    ) -> ThresholdConfig:
        raise NotImplementedError


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
