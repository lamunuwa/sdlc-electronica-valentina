from abc import ABC, abstractmethod

from semana2.eval1.anomaly import AnomalyResult


class Alert(ABC):
    @abstractmethod
    def process_anomaly(self, anomaly: AnomalyResult) -> None: ...


class ConsoleAlert:
    """Clase para mostrar alertas en consola"""

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        if anomaly.is_anomaly and anomaly.anomaly_type is not None:
            anomaly_type = anomaly.anomaly_type.value
            print(f"ALERTA: Sensor {anomaly.sensor_id}, {anomaly_type}, {anomaly.value}")


class FileAlert:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        raise NotImplementedError


class AlertManager:
    def __init__(self) -> None:
        self.handlers: list[Alert] = []

    def add_handler(self, handler: Alert) -> None:
        raise NotImplementedError

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        raise NotImplementedError
