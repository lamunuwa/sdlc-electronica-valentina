from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorReading:
    sensor_id: str
    value: float


# S - Single Responsibility Principle: Una clase solo debe tener una razón para cambiar.

# La siguiente clase no sigue el principio de responsabilidad unica, ya que tiene 2
# responsabilidades: lee el sensor y luego escribe un log con la informacion impresa.


class BadSensorReader:
    def __init__(self, sensor_id: str, filename: str = "log.txt") -> None:
        self.sensor_id = sensor_id
        self.filename = filename

    def read_sensor(self) -> SensorReading:
        return SensorReading(sensor_id=self.sensor_id, value=32.0)

    def save_to_database(self, reading: SensorReading) -> None:
        with open(self.filename, "a") as f:
            f.write(f"{reading.sensor_id}: {reading.value}\n")


# La siguiente clase sigue el principio de responsabilidad unica, ya que creamos una clase
# para leer el sensor y otra clase para escribir un log con la informacion impresa.


class GoodSensorReader:
    def __init__(self, sensor_id: str) -> None:
        self.sensor_id = sensor_id

    def read_sensor(self) -> SensorReading:
        return SensorReading(sensor_id=self.sensor_id, value=32.0)


class DatabaseLogger:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def save(self, reading: SensorReading) -> None:
        with open(self.filename, "a") as f:
            f.write(f"{reading.sensor_id}: {reading.value}\n")


# O - Open/Closed Principle: El código debe estar abierto a la extensión pero cerrado a la
# modificación.

# El siguiente ejemplo no sigue el principio de abierto/cerrado, ya que debemos asegurar que
# las clases BadAnomalyDetector y GoodAnomalyDetector no se modifiquen al agregar metodos de alerta.


class BadAnomalyDetector:
    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    def check(self, reading: SensorReading, alert: str) -> None:
        if reading.value > self.threshold:
            if alert == "console":
                print(f"Alerta: Anomalia en {reading.sensor_id} con valor {reading.value}")
            elif alert == "file":
                with open("alert.txt", "a") as f:
                    f.write(f"Alerta: Anomalia en {reading.sensor_id} con valor {reading.value}\n")


# El siguiente ejemplo sigue el principio de abierto/cerrado, ya que aseguramos dividir las clases
# para evitar modificar BadAnomalyDetector al agregar nuevos metodos de alerta.


class AlertStrategy(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass


class ConsoleAlert(AlertStrategy):
    def send(self, message: str) -> None:
        print(message)


class FileAlert(AlertStrategy):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def send(self, message: str) -> None:
        with open(self.filename, "a") as f:
            f.write(f"{message}\n")


class GoodAnomalyDetector:
    def __init__(self, alert: AlertStrategy, threshold: float) -> None:
        self.alert = alert
        self.threshold = threshold

    def check(self, reading: SensorReading) -> None:
        if reading.value > self.threshold:
            self.alert.send(f"Alerta: Anomalia en {reading.sensor_id} con valor {reading.value}")


# L - Liskov Substitution Principle: Las subclases deben poder sustituir a sus clases base sin
# romper el comportamiento del programa.

# Este código rompe el principio porque la subclase BadHumiditySensor altera por completo el
# comportamiento esperado de la clase base. Cambia el tipo de retorno de SensorReading a un simple
# entero


class BadBaseSensor:
    def get_reading(self) -> SensorReading:
        return SensorReading("id", 0.0)


class BadTemperatureSensor(BadBaseSensor):
    def get_reading(self) -> SensorReading:
        return SensorReading("temperature", 32.0)


class BadHumiditySensor(BadBaseSensor):
    def get_humidity_percentage(self) -> int:
        return 65

    def get_reading(self) -> SensorReading:
        # Forzamos el error para demostrar que no puede sustituir a la base
        raise AttributeError("BadHumiditySensor no implementa get_reading")


def bad_process_sensor(sensor: BadBaseSensor) -> SensorReading:
    return sensor.get_reading()


# Este codigo sigue el principio ya que mantenemos el comportamiento de la clase base y no alteramos
# el tipo de retorno de la clase base.


class GoodBaseSensor(ABC):
    @abstractmethod
    def get_reading(self) -> SensorReading:
        pass


class GoodTemperatureSensor(GoodBaseSensor):
    def get_reading(self) -> SensorReading:
        return SensorReading("temperature", 32.0)


class GoodHumiditySensor(GoodBaseSensor):
    def get_reading(self) -> SensorReading:
        return SensorReading("humidity", 65.0)


def process_sensor(sensor: GoodBaseSensor) -> SensorReading:
    return sensor.get_reading()
