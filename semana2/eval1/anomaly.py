from dataclasses import dataclass

from semana2.eval1.reading import SensorReading


@dataclass
class AnomalyType:
    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"


class AnomalyResult:
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


class AnomalyDetector:
    def evaluate(self, reading: SensorReading) -> AnomalyResult:
        raise NotImplementedError
