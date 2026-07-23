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


class ReadingHistory:
    """Clase para obtener el historial de lecturas de sensores"""

    def __init__(self, sensor_repository: SensorRepository, recorder: ReadingRecorder) -> None:
        self.sensor_lister = SensorLister(sensor_repository)
        self.recorder = recorder

    def get_sensor_history(
        self, sensor_id: str, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> list[SensorReading]:
        self.sensor_lister.find_by_id(sensor_id)

        sensor_readings = [
            reading for reading in self.recorder.readings if reading.sensor_id == sensor_id
        ]

        # Filtro de fechas ------------------------------
        if start_date is not None:
            sensor_readings = [
                reading for reading in sensor_readings if reading.timestamp >= start_date
            ]

        if end_date is not None:
            sensor_readings = [
                reading for reading in sensor_readings if reading.timestamp <= end_date
            ]
        # -----------------------------------------------

        sensor_readings.sort(key=lambda reading: reading.timestamp)
        return sensor_readings

    def get_readings(self) -> list[SensorReading]:
        return list(self.recorder.readings)


# -----------------------------------------------------
