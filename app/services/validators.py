from app.models.sensors import SensorInfo
from app.schemas.readings import ReadingCreate


class ReadingValidationError(Exception): ...


class SensorInactiveError(ReadingValidationError):
    def __init__(self, sensor_id: int) -> None:
        self.sensor_id = sensor_id
        super().__init__(f"El sensor {sensor_id} está inactivo y no acepta lecturas")


class UnsupportedUnitError(ReadingValidationError):
    def __init__(self, unit: str, sensor_type: str) -> None:
        self.unit = unit
        self.sensor_type = sensor_type
        super().__init__(f"Unidad '{unit}' no soportada para sensores de tipo {sensor_type}")


class ValueOutOfRangeError(ReadingValidationError):
    def __init__(self, value: float, unit: str, min_value: float | None = None) -> None:
        self.value = value
        self.unit = unit
        super().__init__(
            f"Valor {value} {unit} fuera del rango físico permitido (mínimo: {min_value})"
        )


class ReadingValidator:
    """Evalua de forma si una lectura cumple las condiciones para procesarse"""

    @staticmethod
    def validate(sensor: SensorInfo, reading_in: ReadingCreate) -> None:
        if not sensor.active:
            raise SensorInactiveError(sensor.id)

        if sensor.type == "TEMPERATURE" and reading_in.unit not in ("C", "F", "K"):
            raise UnsupportedUnitError(reading_in.unit, sensor.type)

        if sensor.type == "TEMPERATURE" and reading_in.unit == "C" and reading_in.value < -273.15:
            raise ValueOutOfRangeError(reading_in.value, reading_in.unit, min_value=-273.15)
