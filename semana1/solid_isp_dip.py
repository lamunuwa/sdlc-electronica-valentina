from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SensorReading:
    sensor_id: str
    value: float


# S - Interface Segregation Principle: No se debe forzar a depender de interfaces sin uso, es mejor
# muchas interfaces especificas a una interfaz general con usos indeseados.

# Supongamos que tenemos un sensor calibrado y listo, que no neceesita escribir, calibrarse ni
# resetearse solo poder leer. En ese contexto el siguiente ejemplo es incorrecto, tenemos una
# interfaz enorme sin uso implementada en el sensor.


class BadSensorInterface(ABC):
    @abstractmethod
    def read(self) -> SensorReading:
        pass

    @abstractmethod
    def write(self, value: float) -> None:
        pass

    @abstractmethod
    def calibrate(self) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


class BadSensorUse(BadSensorInterface):
    def __init__(self, sensor_id: str) -> None:
        self.sensor_id = sensor_id
        self.value = 32.0

    def read(self) -> SensorReading:
        return SensorReading(self.sensor_id, self.value)

    def write(self, value: float) -> None:
        raise NotImplementedError("Este sensor no tiene escritura")

    def calibrate(self) -> None:
        raise NotImplementedError("Este sensor no tiene calibracion")

    def reset(self) -> None:
        raise NotImplementedError("Este sensor no tiene boton de reset")


# El siguiente codigo representa un buen uso del principio, Para no ser tan simple, ahora
# supongamos que el sensor necesita leer y escribir, solo tendra las interfaces necesarias para su
# correcto funcionamiento


class Readable(Protocol):
    def read(self) -> SensorReading:
        pass


class Writable(Protocol):
    def write(self, value: float) -> None:
        pass


# Las demas interfaces solicitadas (Calibratable y Resetable no las voy a agregar ya que son
# innecesarias para fines practicos de mi ejemplo y romperian con ISP. Pero se programan igual.


class GoodSensorUse:
    def __init__(self, sensor_id: str) -> None:
        self.sensor_id = sensor_id
        self.value = 32.0

    def read(self) -> SensorReading:
        return SensorReading(self.sensor_id, self.value)

    def write(self, value: float) -> None:
        self.value = value
