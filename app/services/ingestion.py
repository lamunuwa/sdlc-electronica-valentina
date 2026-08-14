import hashlib
import json
from datetime import datetime

from app.models.readings import ReadingInfo
from app.repositories.alerts import AlertRepository
from app.repositories.readings import ReadingRepository
from app.repositories.sensors import SensorRepository
from app.schemas.readings import ReadingCreate
from app.services.anomalies import AlertService
from app.services.catalog import SensorService
from app.services.validators import (
    DuplicateReadingError,
    InvalidDateRangeError,
    ReadingValidator,
    SensorNotFoundError,
)


def get_now() -> datetime:
    return datetime.now()


class ReadingService:
    """Coordina las sesiones: buscar sensor, validar, evitar duplicados y guardar"""

    def __init__(
        self,
        reading_repository: ReadingRepository,
        sensor_repository: SensorRepository,
        validator: ReadingValidator | None = None,
        alert_repository: AlertRepository | None = None,
    ) -> None:
        self.reading_repository = reading_repository
        self.sensor_repository = sensor_repository
        self.validator = validator or ReadingValidator()
        self.alert_repository = alert_repository

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

    def register_reading(self, sensor_id: int, reading_in: ReadingCreate) -> ReadingInfo:
        """
        1. Confirma existencia del sensor (el sensor_id siempre viene del path)
        2. Ejecuta validacion con ReadingValidator
        3. Verifica no duplicidad mediante el hash
        4. Inserta el registro en la base de datos
        """
        sensor = self.sensor_repository.by_id(sensor_id)
        if sensor is None:
            raise SensorNotFoundError

        self.validator.validate(sensor, reading_in)

        timestamp = reading_in.timestamp or get_now()
        hash_id = self.compute_hash(sensor_id, reading_in.value, reading_in.unit, timestamp)
        if self.reading_repository.by_hash(sensor_id, hash_id):
            raise DuplicateReadingError(sensor_id)

        reading = self.reading_repository.create(sensor_id, reading_in, hash_id, timestamp)
        if self.alert_repository is not None:
            AlertService(self.alert_repository).process_reading(sensor, reading)
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

        sensor_service = SensorService(self.sensor_repository)
        sensor = sensor_service.get_sensor(sensor_id=sensor_id, name=name)

        if from_date is not None and to_date is not None and from_date > to_date:
            raise InvalidDateRangeError

        return self.reading_repository.get_reading(
            sensor_id=sensor.id,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )
