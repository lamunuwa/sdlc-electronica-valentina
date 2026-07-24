import datetime

import pytest

from semana2.eval1.gauss_distro import InvalidCycleCountError, SensorSimulator


def test_generar_lecturas_periodicas() -> None:
    num_sensores = 10
    ciclos = 60
    intervalo = 30
    # Given: un SensorSimulator configurado con 10 sensores
    # And: cada sensor cuenta con una media y desviacion estandar
    simulador = SensorSimulator(num_sensores=num_sensores, media=25.0, desviacion=2.0)

    # When: 60 ciclos  con intervalo de 30s se ejecutan
    lecturas = simulador.ejecutar_simulacion(ciclos=ciclos, intervalo=intervalo)

    # Then: el simulador genera exactamente 600 lecturas
    assert len(lecturas) == num_sensores * ciclos

    # Refactor: validamos que los ID esten dentro del rango
    ids_esperados = set(range(num_sensores))
    ids_obtenidos = set()

    for i, lectura in enumerate(lecturas):
        # And: cada lectura contiene un ID asociado a un sensor del conjunto
        assert "sensor_id" in lectura
        sensor_id = lectura["sensor_id"]
        assert sensor_id in ids_esperados, f"Lectura {i}: ID {sensor_id} no valido"
        ids_obtenidos.add(sensor_id)

        # And: cada lectura contiene un valor de temperatura
        assert "temperatura" in lectura

        # And: cada lectura incluye un timestamp
        assert "timestamp" in lectura
        assert isinstance(lectura["timestamp"], datetime.datetime)

    # Refactor: validamos que se hay lecturas para todos los sensores
    assert ids_obtenidos == ids_esperados, "No todos los sensores generaron lecturas"


def test_rechazar_ciclos_negativos() -> None:
    # Given: un SensorSimulator configurado con 5 sensores
    simulador = SensorSimulator(num_sensores=5, media=25.0, desviacion=2.0)

    # When: intento ejecutar -5 ciclos
    # Then: el sistema lanza manda InvaidCycleCountError
    with pytest.raises(InvalidCycleCountError):
        simulador.ejecutar_simulacion(ciclos=-5, intervalo=30)
