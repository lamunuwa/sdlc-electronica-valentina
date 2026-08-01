from abc import ABC, abstractmethod

from semana2.eval1.anomaly import AnomalyResult


# Clases de apoyo -------------------------------------
class Alert(ABC):
    """Clase abstracta para todos los manejos de alertas"""

    @abstractmethod
    def process_anomaly(self, anomaly: AnomalyResult) -> None: ...


# -----------------------------------------------------


# Clases de negocio -----------------------------------
class ConsoleAlert(Alert):
    """Clase para mostrar alertas en consola"""

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        if anomaly.is_anomaly and anomaly.anomaly_type is not None:
            anomaly_type = anomaly.anomaly_type.value
            print(f"ALERTA: Sensor {anomaly.sensor_id}, {anomaly_type}, {anomaly.value}")


class FileAlert(Alert):
    """Clase para registrar alertas en un archivo"""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        if anomaly.is_anomaly and anomaly.anomaly_type is not None:
            anomaly_type = anomaly.anomaly_type.value
            with open(self.file_path, "a") as f:
                f.write(f"ALERTA: Sensor {anomaly.sensor_id}, {anomaly_type}, {anomaly.value}\n")


class AlertManager:
    """Clase que gestiona y coordina todos los manejadores de alertas"""

    def __init__(self) -> None:
        self.handlers: list[Alert] = []

    def add_handler(self, handler: Alert) -> None:
        self.handlers.append(handler)

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        for handler in self.handlers:
            handler.process_anomaly(anomaly)


# -----------------------------------------------------
