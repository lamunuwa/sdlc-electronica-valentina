import hashlib
import json
from datetime import datetime

from app.models.readings import ReadingInfo
from app.repositories.readings import RepositoryProtocolReading
from app.repositories.sensors import RepositoryProtocol
from app.schemas.readings import ReadingCreate
from app.services.catalog import SensorNotFoundError
from app.services.validators import ReadingValidator


class DuplicateReadingError(Exception):
    def __init__(self, sensor_id: int) -> None:
        self.sensor_id = sensor_id
        super().__init__(f"Lectura duplicada detectada para el sensor {sensor_id}")


def get_now() -> datetime:
    return datetime.now()


class IngestionService:
    def __init__(
        self,
        reading_repo: RepositoryProtocolReading,
        sensor_repo: RepositoryProtocol,
        validator: ReadingValidator = ReadingValidator(),  # noqa: B008
    ) -> None:
        self.reading_repo = reading_repo
        self.sensor_repo = sensor_repo
        self.validator = validator

    def _compute_hash(self, sensor_id: int, value: float, unit: str) -> str:
        payload = json.dumps(
            {
                "sensor_id": sensor_id,
                "value": value,
                "unit": unit,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def register_reading(self, sensor_id: int, reading_in: ReadingCreate) -> ReadingInfo:
        sensor = self.sensor_repo.by_id(sensor_id)
        if not sensor:
            raise SensorNotFoundError(sensor_id)

        self.validator.validate(sensor, reading_in)

        now = get_now()
        hash_id = self._compute_hash(
            sensor_id=sensor_id,
            value=reading_in.value,
            unit=reading_in.unit,
        )

        if self.reading_repo.exists_by_hash(sensor_id, hash_id):
            raise DuplicateReadingError(sensor_id)

        # 5. Guardar en Base de Datos
        return self.reading_repo.create(
            sensor_id=sensor_id,
            reading_in=reading_in,
            hash_id=hash_id,
            timestamp=now,
        )
