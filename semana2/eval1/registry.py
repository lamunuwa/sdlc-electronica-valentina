from dataclasses import dataclass
from enum import Enum


class SensorType(Enum):
    TEMPERATURE = "TEMPERATURE"


@dataclass
class SensorData:
    id: str
    type: SensorType
    location: str


class InvalidSensorDataError(Exception): ...


class SensorAlreadyExistsError(Exception): ...


class SensorRepository:
    def __init__(self) -> None:
        self.sensors: dict[str, SensorData] = {}


class SensorLister:
    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    def get_by_id(self, sensor_id: str) -> SensorData | None:
        raise NotImplementedError

    def list_all(self) -> list[SensorData]:
        raise NotImplementedError


class SensorRegistry:
    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    def register(self, sensor_id: str, sensor_type: SensorType, location: str) -> SensorData:
        raise NotImplementedError


class SensorDeleter:
    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    def unregister(self, sensor_id: str) -> None:
        raise NotImplementedError
