# alert.py
from semana2.eval1.anomaly import AnomalyResult


class ConsoleAlert:
    """Clase para mostrar alertas en consola"""

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        if anomaly.is_anomaly and anomaly.anomaly_type is not None:
            anomaly_type = anomaly.anomaly_type.value
            print(f"ALERTA: Sensor {anomaly.sensor_id}, {anomaly_type}, {anomaly.value}")
