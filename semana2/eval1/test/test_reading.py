from datetime import datetime

import pytest

from semana2.eval1.reading import (
    InvalidReadingError,
    ReadingRecorder,
)
from semana2.eval1.registry import (
    SensorNotFoundError,
    SensorRegistry,
    SensorRepository,
    SensorType,
)


def test_registrar_lectura_valida_sensor_existente() -> None:
    # Given: el sensor "TEMP-01" esta registrado
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    recorder = ReadingRecorder(repository)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")
    now = datetime.now()

    # When: registro la lectura para "TEMP-01" con timestamp
    reading = recorder.record_reading(sensor_id="TEMP-01", value=22.5, timestamp=now)

    # Then: la lectura queda almacenada
    # And: los datos son correctos
    assert reading is not None
    assert reading.sensor_id == "TEMP-01"
    assert reading.value == 22.5
    assert reading.timestamp == now


def test_rechazar_lectura_sensor_no_registrado() -> None:
    # Given: ningun sensor con ID "GHOST-99" existe
    repository = SensorRepository()
    recorder = ReadingRecorder(repository)
    now = datetime.now()

    # When: intento registrar lectura para "GHOST-99"
    # Then: se lanza SensorNotFoundError
    with pytest.raises(SensorNotFoundError):
        recorder.record_reading(sensor_id="GHOST-99", value=22.5, timestamp=now)


def test_rechazar_lectura_sin_timestamp() -> None:
    # Given: el sensor "TEMP-01" está registrado
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    recorder = ReadingRecorder(repository)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")

    # When: intento registrar lectura sin timestamp
    # Then: se lanza InvalidReadingError
    with pytest.raises(InvalidReadingError, match="Timestamp requerido"):
        recorder.record_reading(sensor_id="TEMP-01", value=22.5, timestamp=None)


def test_registrar_lecturas_multiples_sensores() -> None:
    # Given: los sensores "TEMP-01" y "TEMP-02" están registrados
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    recorder = ReadingRecorder(repository)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")
    regis.register("TEMP-02", SensorType.TEMPERATURE, "Bodega B")
    now = datetime.now()

    # When: registro lecturas para ambos
    r1 = recorder.record_reading("TEMP-01", 22.5, now)
    r2 = recorder.record_reading("TEMP-02", 19.0, now)

    # Then: ambas lecturas quedan almacenadas
    # And: ambas lecturas tienen sus ID
    readings = recorder.get_readings()
    assert len(readings) == 2
    assert r1.sensor_id == "TEMP-01"
    assert r2.sensor_id == "TEMP-02"
