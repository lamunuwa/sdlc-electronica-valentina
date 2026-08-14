from datetime import datetime

from app.models.sensors import SensorInfo
from app.schemas.readings import ReadingCreate


# Errores compartidos ---------------------------------
class MissingRequiredFieldsError(Exception):
    def __init__(self) -> None:
        super().__init__("Campos obligatorios faltantes")


class SensorNameOrIDDontMatchError(Exception):
    def __init__(self) -> None:
        super().__init__("El nombre y el ID del sensor no coinciden")


class SensorNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("Sensor no encontrado")


# -----------------------------------------------------


# Errores de sensores ---------------------------------
class SensorNameDuplicateError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"El sensor con el nombre '{name}' ya existe")


class SensorNameTooLongError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"El nombre '{name}' excede el limite de caracteres permitido")


class InvalidSensorTypeError(Exception):
    def __init__(self, sensor_type: str) -> None:
        self.sensor_type = sensor_type
        super().__init__(f"Tipo de sensor '{sensor_type}' no soportado")


class InvalidSensorUnitError(Exception):
    def __init__(self, sensor_type: str, unit: str) -> None:
        self.sensor_type = sensor_type
        self.unit = unit
        super().__init__(f"Unidad '{unit}' no soportada para sensores de tipo {sensor_type}")


class LowThreshGreaterThanHighThreshError(Exception):
    def __init__(self) -> None:
        super().__init__("Umbral minimo no puede ser mayor que el umbral maximo")


class SensorThresholdOutOfRangeError(Exception):
    def __init__(self, unit: str) -> None:
        self.unit = unit
        super().__init__(f"Umbral minimo y/o umbral maximo fuera del rango fisico de {unit}")


class NeddedChangesToUpdateSensorError(Exception):
    def __init__(self) -> None:
        super().__init__("No se proporcionaron cambios para actualizar el sensor")


class SensorAlreadyInactiveError(Exception):
    def __init__(self) -> None:
        super().__init__("El sensor ya se encuentra inactivo")


# -----------------------------------------------------


# Errores de lecturas ---------------------------------


class UnsupportedSensorTypeError(Exception):
    def __init__(self, sensor_type: str) -> None:
        self.sensor_type = sensor_type
        super().__init__(f"No existen reglas definidas para {sensor_type}")


class UnsupportedUnitError(Exception):
    def __init__(self, unit: str, sensor_type: str) -> None:
        self.unit = unit
        self.sensor_type = sensor_type
        super().__init__(f"Unidad '{unit}' no soportada para sensores de tipo {sensor_type}")


class ValueOutOfRangeError(Exception):
    def __init__(self, value: float, unit: str, min_value: float | None = None) -> None:
        self.value = value
        self.unit = unit
        super().__init__(
            f"Valor {value} {unit} fuera del rango fisico permitido (minimo: {min_value})"
        )


class SensorCantProcessUnitError(Exception):
    def __init__(self, reading_unit: str, sensor_unit: str) -> None:
        self.reading_unit = reading_unit
        self.sensor_unit = sensor_unit
        super().__init__(
            f"El sensor no puede procesar la unidad '{reading_unit}', requiere '{sensor_unit}'"
        )


class ReadingValueTooLongError(Exception):
    def __init__(self, value: float) -> None:
        self.value = value
        super().__init__(f"El valor de la lectura {value} excede el rango permitido por el sensor")


class InvalidTimestampError(Exception):
    def __init__(self) -> None:
        super().__init__("El formato de timestamp no es valido, usa 'yyyy-mm-dd hh:mm:ss'")


class TimestampInFutureError(Exception):
    def __init__(self) -> None:
        super().__init__("La fecha de la lectura no puede estar en el futuro")


class SensorInactiveError(Exception):
    def __init__(self, sensor_id: int) -> None:
        self.sensor_id = sensor_id
        super().__init__(f"El sensor {sensor_id} esta inactivo y no acepta lecturas")


class DuplicateReadingError(Exception):
    def __init__(self, sensor_id: int) -> None:
        self.sensor_id = sensor_id
        super().__init__(f"Lectura duplicada detectada para el sensor {sensor_id}")


class InvalidDateRangeError(Exception):
    def __init__(self) -> None:
        super().__init__("La fecha de inicio no puede ser mayor que la fecha final")


class ReadingValidator:
    """Evalua si una lectura cumple las condiciones para procesarse contra un sensor especifico"""

    @staticmethod
    def validate(sensor: SensorInfo, reading_in: ReadingCreate) -> None:
        # 1. Verificar si el sensor esta activo
        if not sensor.active:
            raise SensorInactiveError(sensor.id)

        # 2. Validar compatibilidad de unidad entre la lectura y el sensor
        if reading_in.unit != sensor.unit:
            raise SensorCantProcessUnitError(
                reading_unit=reading_in.unit,
                sensor_unit=sensor.unit,
            )

        # 3. Validar timestamp en el futuro
        if reading_in.timestamp is not None:
            tz = reading_in.timestamp.tzinfo
            now = datetime.now(tz=tz)
            if reading_in.timestamp > now:
                raise TimestampInFutureError

        # 4. Validar el valor dentro de los umbrales configurados en el sensor
        if sensor.threshold_min is not None and sensor.threshold_max is not None:
            if not (sensor.threshold_min <= reading_in.value <= sensor.threshold_max):
                raise ReadingValueTooLongError(value=reading_in.value)


# -----------------------------------------------------


# Errores de alertas ----------------------------------


class AlertNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("Alerta no encontrada")


class MissingAlertStatusError(Exception):
    def __init__(self) -> None:
        super().__init__("Debe proporcionar el campo 'state' para actualizar la alerta")


class InvalidAlertStatusError(Exception):
    def __init__(self) -> None:
        super().__init__("El estado de la alerta debe ser 'open', 'acknowledged' o 'resolved'")


class NeededChangesToUpdateAlertError(Exception):
    def __init__(self) -> None:
        super().__init__("La alerta ya se encuentra en el estado solicitado")


# -----------------------------------------------------
