from datetime import datetime, timedelta

import pytest

from semana2.eval1.reading import (
    InvalidReadingError,
    ReadingHistory,
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
    history = ReadingHistory(repository, recorder)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")
    regis.register("TEMP-02", SensorType.TEMPERATURE, "Bodega B")
    now = datetime.now()

    # When: registro lecturas para ambos
    r1 = recorder.record_reading("TEMP-01", 22.5, now)
    r2 = recorder.record_reading("TEMP-02", 19.0, now)

    # Then: ambas lecturas quedan almacenadas
    # And: ambas lecturas tienen sus ID
    readings = history.get_readings()
    assert len(readings) == 2
    assert r1.sensor_id == "TEMP-01"
    assert r2.sensor_id == "TEMP-02"


def test_consultar_historial_lecturas_sensor() -> None:
    # Given: el sensor "TEMP-01" tiene 3 lecturas registradas
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    recorder = ReadingRecorder(repository)
    history = ReadingHistory(repository, recorder)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")

    now = datetime.now()
    timestamp1 = now - timedelta(hours=2)
    timestamp2 = now - timedelta(hours=1)
    timestamp3 = now - timedelta(minutes=30)

    recorder.record_reading(sensor_id="TEMP-01", value=22.5, timestamp=timestamp1)
    recorder.record_reading(sensor_id="TEMP-01", value=23.0, timestamp=timestamp2)
    recorder.record_reading(sensor_id="TEMP-01", value=21.5, timestamp=timestamp3)

    # When: consulto el historial del sensor "TEMP-01"
    sensor_history = history.get_sensor_history(sensor_id="TEMP-01")

    # Then: el sistema devuelve las lecturas
    assert len(sensor_history) == 3

    # And: las lecturas están ordenadas por timestamp ascendente
    assert sensor_history[0].timestamp == timestamp1
    assert sensor_history[1].timestamp == timestamp2
    assert sensor_history[2].timestamp == timestamp3

    # And: cada lectura contiene ID, temperatura y timestamp
    for reading in sensor_history:
        assert reading.sensor_id == "TEMP-01"
        assert isinstance(reading.value, float)
        assert isinstance(reading.timestamp, datetime)


def test_consultar_historial_con_filtro_fechas() -> None:
    # Given: el sensor "TEMP-01" tiene lecturas en diferentes dias
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    recorder = ReadingRecorder(repository)
    history = ReadingHistory(repository, recorder)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")

    day_19 = datetime(2026, 7, 19, 10, 0, 0)
    day_20_morning = datetime(2026, 7, 20, 9, 0, 0)
    day_20_noon = datetime(2026, 7, 20, 12, 0, 0)
    day_20_evening = datetime(2026, 7, 20, 18, 0, 0)
    day_21 = datetime(2026, 7, 21, 10, 0, 0)

    recorder.record_reading(sensor_id="TEMP-01", value=20.0, timestamp=day_19)
    recorder.record_reading(sensor_id="TEMP-01", value=22.0, timestamp=day_20_morning)
    recorder.record_reading(sensor_id="TEMP-01", value=23.0, timestamp=day_20_noon)
    recorder.record_reading(sensor_id="TEMP-01", value=21.0, timestamp=day_20_evening)
    recorder.record_reading(sensor_id="TEMP-01", value=19.0, timestamp=day_21)

    # When: consulto el historial del sensor "TEMP-01" entre las fechas
    start_date = datetime(2026, 7, 20, 0, 0, 0)
    end_date = datetime(2026, 7, 20, 23, 59, 59)
    sensor_history = history.get_sensor_history(
        sensor_id="TEMP-01", start_date=start_date, end_date=end_date
    )

    # Then: el sistema devuelve solo las lecturas del dia 2026-07-20
    assert len(sensor_history) == 3
    for reading in sensor_history:
        assert reading.timestamp.date() == datetime(2026, 7, 20).date()


def test_consultar_historial_sensor_sin_lecturas() -> None:
    # Given: el sensor "TEMP-01" esta registrado pero no tiene lecturas
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    recorder = ReadingRecorder(repository)
    history = ReadingHistory(repository, recorder)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")

    # When: consulto el historial del sensor "TEMP-01"
    sensor_history = history.get_sensor_history(sensor_id="TEMP-01")

    # Then: el sistema devuelve una lista vacía
    assert sensor_history == []
    assert len(sensor_history) == 0


def test_consultar_historial_sensor_inexistente() -> None:
    # Given: no existe el sensor "GHOST-99"
    repository = SensorRepository()
    recorder = ReadingRecorder(repository)
    history = ReadingHistory(repository, recorder)

    # When: consulto el historial del sensor "GHOST-99"
    # Then: el sistema lanza la excepción SensorNotFoundError
    with pytest.raises(SensorNotFoundError):
        history.get_sensor_history(sensor_id="GHOST-99")
