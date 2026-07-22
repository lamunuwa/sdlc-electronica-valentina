from dataclasses import dataclass
from enum import Enum


# Clases de apoyo -------------------------------------
class SensorType(Enum):
    """Clase para determinar el tipo de sensor"""

    TEMPERATURE = "TEMPERATURE"
    # HUMIDITY = "HUMIDITY"
    # PRESSURE = "PRESSURE"
    # DISTANCE = "DISTANCE"


@dataclass
class SensorData:
    """Clase para determinar los datos de un sensor"""

    id: str
    type: SensorType
    location: str


# -----------------------------------------------------


# Clases de error -------------------------------------
class InvalidSensorDataError(Exception): ...


class SensorAlreadyExistsError(Exception): ...


# ------------------------------------------------------


# Clases de negocio -----------------------------------
class SensorRepository:
    """Clase para mantener los sensores registrados en memoria"""

    def __init__(self) -> None:
        self.sensors: dict[str, SensorData] = {}


class SensorLister:
    """Clase para consultar informacion de los sensores"""

    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    def get_by_id(self, sensor_id: str) -> SensorData | None:
        return self.repository.sensors.get(sensor_id)

    def list_all(self) -> list[SensorData]:
        return list(self.repository.sensors.values())


class SensorRegistry:
    """Clase para registrar sensores validando las situaciones de negocio establecidas"""

    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    def register(self, sensor_id: str, sensor_type: SensorType, location: str) -> SensorData:
        if not sensor_id or not sensor_id.strip():
            raise InvalidSensorDataError("ID no puede estar vacío")

        if sensor_id in self.repository.sensors:
            raise SensorAlreadyExistsError("ID existente")

        sensor = SensorData(id=sensor_id, type=sensor_type, location=location)
        self.repository.sensors[sensor_id] = sensor
        return sensor


class SensorDeleter:
    """Clase para eliminar sensores"""

    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    def unregister(self, sensor_id: str) -> None:
        if sensor_id in self.repository.sensors:
            del self.repository.sensors[sensor_id]


# ------------------------------------------------------
