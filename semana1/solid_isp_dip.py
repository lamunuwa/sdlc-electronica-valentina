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


# S - Dependency Inversion Principle: Los módulos de alto nivel no deben depender de módulos de bajo
#  nivel. Ambos deben depender de abstracciones.

# El siguiente codigo representa un mal uso de DIP, dado que el modulo de alto nivel
# "BadDataProcessor" depende el codigo que guarda la informacion, un modulo de mas bajo nivel.


class BadDatabase:
    def __init__(self, filename: str = "database.txt") -> None:
        self.filename = filename

    def save(self, reading: SensorReading) -> None:
        with open(self.filename, "a") as f:
            f.write(f"{reading.sensor_id}: {reading.value}\n")


class BadDataProcessor:
    def __init__(self, filename: str = "database.txt") -> None:
        self.logger = BadDatabase(filename)

    def process(self, reading: SensorReading) -> None:
        self.logger.save(reading)


# Para solucionarlo y aplicar DIP se crea un "contrato" de por medio, una clase que sirve para
# establecer lectura y escritura pero que como tal no guarda ni lee. Iniciamos tomando de
# referencia el codigo de la guia de estudios


class DataRepository(Protocol):
    def save(self, reading: SensorReading) -> None: ...
    def get_latest(self, sensor_id: str) -> SensorReading | None: ...


# El documento explicitamente solicita usar unicamente InMemoryRepository para el test, dejo
# esta seccion del codigo como comentario para evitar errores con el coverage

""" class PostgreSQLRepositoy:
        def save(self, reading: SensorReading) -> None:
            print(f"[PostgreSQL] Guardando: {reading.sensor_id} = {reading.value}")
    
        def get_latest(self, sensor_id: str) -> SensorReading:
            return SensorReading(sensor_id, 32.0) """


class InMemoryRepository:
    def __init__(self) -> None:
        self.data: dict[str, SensorReading] = {}

    def save(self, reading: SensorReading) -> None:
        self.data[reading.sensor_id] = reading

    def get_latest(self, sensor_id: str) -> SensorReading | None:
        return self.data.get(sensor_id)


class DataProcessor:
    """Depende de la abstraccion, no de una implementacion concreta."""

    def __init__(self, repository: DataRepository) -> None:
        self.repo = repository  # inyeccion de dependencias

    def process_reading(self, sensor_id: str, value: float) -> None:
        reading = SensorReading(sensor_id, value)
        self.repo.save(reading)

    def get_sensor_reading(self, sensor_id: str) -> SensorReading | None:
        return self.repo.get_latest(sensor_id)
