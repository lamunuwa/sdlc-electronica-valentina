from datetime import datetime

from app.models.alerts import AlertInfo
from app.models.readings import ReadingInfo
from app.models.sensors import SensorInfo
from app.repositories.alerts import AlertRepository


class AlertService:
    """Detecta y registra anomalías de una lectura persistida"""

    def __init__(
        self,
        alert_repo: AlertRepository,
    ) -> None:
        """Guarda el repositorio de alertas"""
        self.alert_repo = alert_repo

    def process_reading(self, sensor: SensorInfo, reading: ReadingInfo) -> None:
        """Crea una alerta si la lectura supera un umbral"""
        alert_type: str | None = None
        if reading.value > sensor.threshold_max:
            alert_type = f"HIGH_{sensor.type}"
        elif reading.value < sensor.threshold_min:
            alert_type = f"LOW_{sensor.type}"

        if alert_type is not None:
            self.alert_repo.create(
                {
                    "sensor_id": sensor.id,
                    "reading_id": reading.id,
                    "type": alert_type,
                    "value": reading.value,
                    "unit": reading.unit,
                    "timestamp": reading.timestamp,
                }
            )

    def get_alerts(
        self,
        sensor_id: int,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AlertInfo]:
        """Obtiene alertas de un sensor"""
        return self.alert_repo.get_alerts(sensor_id, from_date, to_date, limit, offset)

    def get_alert(self, alert_id: int) -> AlertInfo | None:
        """Obtiene una alerta por su id"""
        return self.alert_repo.get_by_id(alert_id)
