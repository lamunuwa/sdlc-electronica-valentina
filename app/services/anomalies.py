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
    SensorNameOrIDDontMatchError,
    SensorNotFoundError,
)


class AlertService:
    def __init__(
        self, alert_repo: AlertRepository, sensor_repo: SensorRepository | None = None
    ) -> None:
        self.alert_repo = alert_repo
        self.sensor_repo = sensor_repo

    def process_reading(self, sensor: SensorInfo, reading: ReadingInfo) -> None:
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
                    "state": "open",
                    "timestamp": reading.timestamp,
                }
            )

    def _validate_dates(self, from_date: datetime | None, to_date: datetime | None) -> None:
        if from_date and to_date and from_date > to_date:
            raise InvalidDateRangeError()

    def get_all_alerts(
        self, from_date: datetime | None, to_date: datetime | None, limit: int, offset: int
    ) -> list[AlertInfo]:
        self._validate_dates(from_date, to_date)
        return self.alert_repo.get_all_alerts(from_date, to_date, limit, offset)

    def get_alerts(
        self,
        sensor_id: int,
        from_date: datetime | None,
        to_date: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AlertInfo]:
        self._validate_dates(from_date, to_date)
        return self.alert_repo.get_alerts_by_sensor(sensor_id, from_date, to_date, limit, offset)

    def get_alerts_by_sensor(
        self,
        sensor_id: int | None,
        name: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AlertInfo]:
        if not sensor_id and not name:
            raise MissingRequiredFieldsError()

        self._validate_dates(from_date, to_date)

        if self.sensor_repo is None:
            raise MissingRequiredFieldsError

        target_sensor_id: int | None = sensor_id
        if name:
            # Usando el método by_name() definido en SensorRepository
            sensor = self.sensor_repo.by_name(name)
            if not sensor:
                # Si name no existe pero hay sensor_id, significa mismatch
                if sensor_id:
                    raise SensorNameOrIDDontMatchError()
                # Si solo hay name y no existe, lanzar SensorNotFoundError
                raise SensorNotFoundError()
            # Si sensor existe por name y hay sensor_id, verificar que coincidan
            if sensor_id and sensor.id != sensor_id:
                raise SensorNameOrIDDontMatchError()
            target_sensor_id = sensor.id
        else:
            # Solo hay sensor_id, búscar por id
            sensor = self.sensor_repo.by_id(sensor_id or 0)
            if not sensor:
                raise SensorNotFoundError()
            target_sensor_id = sensor_id

        assert target_sensor_id is not None
        return self.alert_repo.get_alerts_by_sensor(
            target_sensor_id, from_date, to_date, limit, offset
        )

    def get_alert(self, alert_id: int) -> AlertInfo:
        alert = self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFoundError()
        return alert

    def update_alert_state(self, alert_id: int, state: str | None) -> AlertInfo:
        if state is None:
            raise MissingAlertStatusError()

        valid_states = ["open", "acknowledged", "resolved"]
        if state not in valid_states:
            raise InvalidAlertStatusError()

        alert = self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFoundError()

        if alert.state == state:
            raise NeededChangesToUpdateAlertError()

        alert.state = state
        return self.alert_repo.update(alert)
