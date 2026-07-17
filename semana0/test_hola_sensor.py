from semana0.hola_sensor import Sensor


def test_sensor():
    sensor = Sensor()
    assert sensor.read() == 23.5
