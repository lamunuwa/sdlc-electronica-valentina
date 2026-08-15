from datetime import datetime

from app.models.alerts import AlertInfo
from app.models.readings import ReadingInfo
from app.models.sensors import SensorInfo
from app.repositories.alerts import AlertRepository
from app.repositories.sensors import SensorRepository
from app.services.validators import (
    AlertNotFoundError,
    InvalidAlertStatusError,
    InvalidDateRangeError,
    MissingAlertStatusError,
    MissingRequiredFieldsError,
    NeededChangesToUpdateAlertError,
    ValidateSensorParameters,
)


class AlertService:
    """Todas las sesiones de procesamiento de alertas"""

    def __init__(
        self, alert_repo: AlertRepository, sensor_repo: SensorRepository | None = None
    ) -> None:
        self.alert_repo = alert_repo
        self.sensor_repo = sensor_repo

    def process_reading(self, sensor: SensorInfo, reading: ReadingInfo) -> None:
        """Procesa una lectura"""

        alert_type: str | None = None
        if reading.value > sensor.threshold_max:
            alert_type = f"HIGH_{sensor.type}"
        elif reading.value < sensor.threshold_min:
            alert_type = f"LOW_{sensor.type}"

        if alert_type is not None:
            self.alert_repo.create_alert(
                {
                    "sensor_id": sensor.id,
                    "reading_id": reading.id,
                    "type": alert_type,
                    "value": reading.value,
                    "unit": reading.unit,
                    "state": "open",
                    "timestamp": reading.timestamp,
                }
            )

    def validate_dates(self, from_date: datetime | None, to_date: datetime | None) -> None:
        """Valida los rangos de fechas"""

        if from_date and to_date and from_date > to_date:
            raise InvalidDateRangeError

    def get_all_alerts(
        self, from_date: datetime | None, to_date: datetime | None, limit: int, offset: int
    ) -> list[AlertInfo]:
        """Lista todas las alertas"""
        self.validate_dates(from_date, to_date)
        return self.alert_repo.get_all_alerts(from_date, to_date, limit, offset)

    def get_alerts_by_sensor(
        self,
        sensor_id: int | None,
        name: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AlertInfo]:
        """Busca el sensor por ID, nombre o ambos"""

        if self.sensor_repo is None:
            raise MissingRequiredFieldsError

        sensor = ValidateSensorParameters.search_sensor(
            self.sensor_repo, sensor_id=sensor_id, name=name
        )

        self.validate_dates(from_date, to_date)

        return self.alert_repo.get_alerts_by_sensor(sensor.id, from_date, to_date, limit, offset)

    def get_alert(self, alert_id: int) -> AlertInfo:
        """Busca el alert por ID"""

        alert = self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFoundError
        return alert

    def update_alert_state(self, alert_id: int, state: str | None) -> AlertInfo:
        """Verifica las actualizaciones de las alertas"""

        if state is None:
            raise MissingAlertStatusError

        valid_states = ["OPEN", "ACKNOWLEDGED", "RESOLVED"]
        if state not in valid_states:
            raise InvalidAlertStatusError

        alert = self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFoundError

        if alert.state == state:
            raise NeededChangesToUpdateAlertError

        alert.state = state
        return self.alert_repo.update_alert(alert)
