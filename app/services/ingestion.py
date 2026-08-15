import hashlib
import json
from datetime import datetime

from app.models.readings import ReadingInfo
from app.repositories.alerts import AlertRepository
from app.repositories.readings import ReadingRepository
from app.repositories.sensors import SensorRepository
from app.schemas.readings import ReadingCreate
from app.services.validators import (
    DuplicateReadingError,
    InvalidDateRangeError,
    ReadingValidator,
    ValidateSensorParameters,
)


def get_now() -> datetime:
    return datetime.now()


class ReadingService:
    """Todas las sesiones de la inyeccion de lecturas"""

    def __init__(
        self,
        reading_repository: ReadingRepository,
        sensor_repository: SensorRepository,
        alert_repository: AlertRepository | None = None,
    ) -> None:
        self.reading_repository = reading_repository
        self.sensor_repository = sensor_repository
        self.alert_repository = alert_repository

    # funciones de apoyo ---------------------------------------
    @staticmethod
    def compute_hash(sensor_id: int, value: float, unit: str, timestamp: datetime) -> str:
        """Genera un hash unico basado en el contenido de la lectura y su timestamp"""
        payload = json.dumps(
            {
                "sensor_id": sensor_id,
                "value": value,
                "unit": unit,
                "timestamp": timestamp.isoformat(timespec="microseconds"),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # ---------------------------------------------------------

    def register_reading(self, sensor_id: int, reading_in: ReadingCreate) -> ReadingInfo:
        """Registra una lectura en la base de datos"""

        sensor = ValidateSensorParameters.search_sensor(
            self.sensor_repository, sensor_id=sensor_id, name=None
        )
        ReadingValidator.validate(sensor, reading_in)

        timestamp = reading_in.timestamp or datetime.now()
        hash_id = self.compute_hash(
            sensor_id=sensor.id,
            value=reading_in.value,
            unit=reading_in.unit,
            timestamp=timestamp,
        )

        if self.reading_repository.by_hash(sensor.id, hash_id):
            raise DuplicateReadingError(sensor_id)

        reading = self.reading_repository.create(
            sensor_id=sensor.id,
            reading_in=reading_in,
            hash_id=hash_id,
        )

        # 5. Evaluar Umbrales y Generar Alerta si aplica
        if (
            self.alert_repository
            and sensor.threshold_min is not None
            and sensor.threshold_max is not None
        ):
            if not (sensor.threshold_min <= reading.value <= sensor.threshold_max):
                # Determinamos si fue superior o inferior al rango permitido
                if reading.value > sensor.threshold_max:
                    alert_type = f"HIGH_{sensor.type}"
                else:
                    alert_type = f"LOW_{sensor.type}"

                alert_payload = {
                    "sensor_id": sensor.id,
                    "reading_id": reading.id,
                    "type": alert_type,
                    "value": reading.value,
                    "unit": reading.unit,
                    "state": "OPEN",
                    "timestamp": timestamp,
                }
                self.alert_repository.create_alert(alert_payload)

        return reading

    def get_readings(
        self,
        sensor_id: int | None = None,
        name: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ReadingInfo]:
        """Busca el sensor por ID, nombre o ambos (igual que sensors) y obtiene sus lecturas"""

        sensor = ValidateSensorParameters.search_sensor(
            self.sensor_repository, sensor_id=sensor_id, name=name
        )

        if from_date is not None and to_date is not None and from_date > to_date:
            raise InvalidDateRangeError

        return self.reading_repository.get_reading(
            sensor_id=sensor.id,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )
