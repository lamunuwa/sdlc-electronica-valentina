import hashlib
import json
from datetime import datetime

from app.models.readings import ReadingInfo
from app.repositories.readings import ReadingRepository
from app.repositories.sensors import SensorRepository
from app.schemas.readings import ReadingCreate
from app.services.validators import (
    DuplicateReadingError,
    InvalidDateRangeError,
    LimitExceededError,
    MissingRequiredFieldsError,
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
    ) -> None:
        self.reading_repository = reading_repository
        self.sensor_repository = sensor_repository

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

        return reading

    def get_readings(
        self,
        sensor_id: int | None = None,
        name: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ReadingInfo]:
        """Busca el sensor por ID, nombre o ambos y obtiene sus lecturas"""
        effective_limit = 100 if limit is None else limit
        if effective_limit > 100:
            raise LimitExceededError

        if from_date is not None and to_date is not None and from_date > to_date:
            raise InvalidDateRangeError

        if sensor_id is None and name is None:
            if limit is None:
                raise MissingRequiredFieldsError
            return self.reading_repository.get_reading(
                sensor_id=None,
                from_date=from_date,
                to_date=to_date,
                limit=effective_limit,
                offset=offset,
            )

        sensor = ValidateSensorParameters.search_sensor(
            self.sensor_repository, sensor_id=sensor_id, name=name
        )

        return self.reading_repository.get_reading(
            sensor_id=sensor.id,
            from_date=from_date,
            to_date=to_date,
            limit=effective_limit,
            offset=offset,
        )
