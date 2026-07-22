from dataclasses import dataclass
from datetime import datetime

from semana2.eval1.registry import SensorRepository


class InvalidReadingError(Exception): ...


@dataclass
class SensorReading:
    sensor_id: str
    value: float
    timestamp: datetime


class ReadingRecorder:
    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    def record_reading(
        self, sensor_id: str, value: float, timestamp: datetime | None
    ) -> SensorReading:
        raise NotImplementedError

    def get_readings(self) -> list[SensorReading]:
        raise NotImplementedError
