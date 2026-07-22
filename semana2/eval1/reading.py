from dataclasses import dataclass
from datetime import datetime

from semana2.eval1.registry import (
    SensorLister,
    SensorRepository,
)


# Clases de apoyo -------------------------------------
@dataclass
class SensorReading:
    """Clase para determinar los datos de lectura"""

    sensor_id: str
    value: float
    timestamp: datetime


# -----------------------------------------------------


# Clases de error -------------------------------------
class InvalidReadingError(Exception): ...


# -----------------------------------------------------


# Clases de negocio -----------------------------------
class ReadingRecorder:
    """Clase para registrar lecturas de sensores"""

    def __init__(self, repository: SensorRepository) -> None:
        self.sensor_lister = SensorLister(repository)
        self.readings: list[SensorReading] = []

    def record_reading(
        self, sensor_id: str, value: float, timestamp: datetime | None
    ) -> SensorReading:
        self.sensor_lister.find_by_id(sensor_id)

        if timestamp is None:
            raise InvalidReadingError("Timestamp requerido")

        reading = SensorReading(sensor_id=sensor_id, value=value, timestamp=timestamp)
        self.readings.append(reading)
        return reading

    def get_readings(self) -> list[SensorReading]:
        return list(self.readings)


# -----------------------------------------------------
