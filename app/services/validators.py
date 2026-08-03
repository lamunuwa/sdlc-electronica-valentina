from app.core.limits import limits
from app.models.sensors import SensorInfo
from app.schemas.readings import ReadingCreate


class ReadingValidationError(Exception): ...


class SensorInactiveError(ReadingValidationError):
    def __init__(self, sensor_id: int) -> None:
        self.sensor_id = sensor_id
        super().__init__(f"El sensor {sensor_id} está inactivo y no acepta lecturas")


class UnsupportedSensorTypeError(ReadingValidationError):
    def __init__(self, sensor_type: str) -> None:
        self.sensor_type = sensor_type
        super().__init__(f"No existen reglas definidas para {sensor_type}")


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
            f"Valor {value} {unit} fuera del rango físico permitido (minimo: {min_value})"
        )


class ReadingValidator:
    """Evalua de forma si una lectura cumple las condiciones para procesarse"""

    @staticmethod
    def validate(sensor: SensorInfo, reading_in: ReadingCreate) -> None:
        if not sensor.active:
            raise SensorInactiveError(sensor.id)

        # 1. Validar si el tipo existe en los límites del sistema
        if sensor.type not in limits:
            raise UnsupportedSensorTypeError(sensor.type)

        units_for_type = limits[sensor.type]

        # 2. Validar si la unidad es soportada
        if reading_in.unit not in units_for_type:
            raise UnsupportedUnitError(reading_in.unit, sensor.type)

        # 3. Validar el rango de valor
        limits_for_unit = units_for_type[reading_in.unit]
        if reading_in.value < limits_for_unit.min_value:
            raise ValueOutOfRangeError(
                value=reading_in.value, unit=reading_in.unit, min_value=limits_for_unit.min_value
            )
