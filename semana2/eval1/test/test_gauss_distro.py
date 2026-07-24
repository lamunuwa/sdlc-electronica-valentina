import datetime

import pytest

from semana2.eval1.gauss_distro import InvalidCycleCountError, SensorSimulator


def test_generar_lecturas_periodicas() -> None:
    # Given: un SensorSimulator configurado con 10 sensores
    # And: cada sensor cuenta con una media y desviación estandar
    simulador = SensorSimulator(num_sensores=10, media=25.0, desviacion=2.0)

    # When: 60 ciclos  con intervalo de 30s se ejecutan
    lecturas = simulador.ejecutar_simulacion(ciclos=60, intervalo=30)

    # Then: el simulador genera exactamente 600 lecturas
    assert len(lecturas) == 600

    for lectura in lecturas:
        # And: cada lectura contiene un ID asociado a un sensor del conjunto
        assert "sensor_id" in lectura

        # And: cada lectura contiene un valor de temperatura
        assert "temperatura" in lectura

        # And: cada lectura incluye un timestamp
        assert "timestamp" in lectura
        assert isinstance(lectura["timestamp"], datetime.datetime)


def test_rechazar_ciclos_negativos() -> None:
    # Given: un SensorSimulator configurado con 5 sensores
    simulador = SensorSimulator(num_sensores=5, media=25.0, desviacion=2.0)

    # When: intento ejecutar -5 ciclos
    # Then: el sistema lanza manda InvaidCycleCountError
    with pytest.raises(InvalidCycleCountError):
        simulador.ejecutar_simulacion(ciclos=-5, intervalo=30)
