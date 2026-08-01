import pytest
from semana2.eval1.registry import (
    InvalidSensorDataError,
    SensorAlreadyExistsError,
    SensorDeleter,
    SensorLister,
    SensorNotFoundError,
    SensorRegistry,
    SensorRepository,
    SensorType,
)


def test_registrar_sensor_nuevo() -> None:
    # Given: El repositorio esta vacio e instanciamos los servicios
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    lister = SensorLister(repository)

    assert len(lister.list_all()) == 0

    # When: registro un sensor con ID "TEMP-01", tipo TEMPERATURE y ubicacion "Bodega A"
    regis.register(
        sensor_id="TEMP-01",
        sensor_type=SensorType.TEMPERATURE,
        location="Bodega A",
    )

    # Then: el sensor "TEMP-01" queda almacenado y se verifica mediante SensorLister
    retrieved_sensor = lister.get_by_id("TEMP-01")
    assert retrieved_sensor is not None

    # And: el sensor conserva las propiedades especificadas
    assert retrieved_sensor.id == "TEMP-01"
    assert retrieved_sensor.type == SensorType.TEMPERATURE
    assert retrieved_sensor.location == "Bodega A"


def test_rechazar_registro_sensor_id_vacio() -> None:
    # Given: El repositorio esta vacio e instanciamos los servicios
    repository = SensorRepository()
    regis = SensorRegistry(repository)

    # When: intento registrar un sensor sin ID
    # Then: se lanza InvalidSensorDataError
    with pytest.raises(InvalidSensorDataError) as exc_info:
        regis.register(
            sensor_id="",
            sensor_type=SensorType.TEMPERATURE,
            location="Bodega A",
        )

    # And: el mensaje indica "ID no puede estar vacio"
    assert "ID no puede estar vacío" in str(exc_info.value)


def test_rechazar_registro_sensor_id_duplicado() -> None:
    # Given: el sensor con ID "TEMP-01" ya esta registrado en el repositorio
    repository = SensorRepository()
    regis = SensorRegistry(repository)

    regis.register(
        sensor_id="TEMP-01",
        sensor_type=SensorType.TEMPERATURE,
        location="Bodega A",
    )

    # When: intento registrar otro sensor con el mismo ID "TEMP-01"
    # Then: se lanza SensorAlreadyExistsError
    with pytest.raises(SensorAlreadyExistsError) as exc_info:
        regis.register(
            sensor_id="TEMP-01",
            sensor_type=SensorType.TEMPERATURE,
            location="Bodega B",
        )

    # And: el mensaje indica "ID existente"
    assert "ID existente" in str(exc_info.value)


def test_dar_baja_sensor_existente() -> None:
    # Given: el sensor con ID "TEMP-01" esta registrado
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    lister = SensorLister(repository)
    deleter = SensorDeleter(repository)

    regis.register(
        sensor_id="TEMP-01",
        sensor_type=SensorType.TEMPERATURE,
        location="Bodega A",
    )

    # When: doy de baja el sensor "TEMP-01" usando SensorDeleter
    deleter.unregister("TEMP-01")

    # Then: el sensor "TEMP-01" deja de existir al ser consultado con SensorLister
    assert lister.get_by_id("TEMP-01") is None


def test_consultar_sensor_existente() -> None:
    # Given: el sensor con ID "TEMP-01" esta registrado
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    lister = SensorLister(repository)

    regis.register(
        sensor_id="TEMP-01",
        sensor_type=SensorType.TEMPERATURE,
        location="Bodega A",
    )

    # When: solicito el sensor con ID "TEMP-01"
    sensor = lister.get_by_id("TEMP-01")

    # Then: el sistema devuelve el sensor correcto
    # And: el sensor tiene las propiedades correctas
    assert sensor is not None
    assert sensor.id == "TEMP-01"
    assert sensor.type == SensorType.TEMPERATURE
    assert sensor.location == "Bodega A"


def test_consultar_sensor_inexistente() -> None:
    # Given: no existe un sensor con ID "GHOST-99"
    repository = SensorRepository()
    lister = SensorLister(repository)

    # When: solicito el sensor con ID "GHOST-99"
    # Then: se lanza SensorNotFoundError
    with pytest.raises(SensorNotFoundError):
        lister.find_by_id("GHOST-99")


def test_listar_todos_los_sensores_registrados() -> None:
    # Given: los sensores "TEMP-01" y "TEMP-02" están registrados
    repository = SensorRepository()
    regis = SensorRegistry(repository)
    lister = SensorLister(repository)

    regis.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")
    regis.register("TEMP-02", SensorType.TEMPERATURE, "Bodega B")

    # When: solicito la lista de todos los sensores
    sensors = lister.list_all()

    # Then: el sistema devuelve una lista con 2 sensores específicos
    # And: los sensores son "TEMP-01" y "TEMP-02"
    assert len(sensors) == 2
    sensor_ids = [s.id for s in sensors]
    assert "TEMP-01" in sensor_ids
    assert "TEMP-02" in sensor_ids


def test_listar_cuando_no_hay_sensores_registrados() -> None:
    # Given: el SensorRegistry está vacio
    repository = SensorRepository()
    lister = SensorLister(repository)

    # When: solicito la lista de todos los sensores
    sensors = lister.list_all()

    # Then: el sistema devuelve una lista vacia
    assert len(sensors) == 0
    assert sensors == []
