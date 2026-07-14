from semana1.solid_srp_ocp_lsp import BadSensorReading, DatabaseLogger, GoodSensorReading


def test_srp_bad(tmp_path) -> None:
    tmp_file = tmp_path / "log.txt"
    bad_sensor = BadSensorReading(sensor_id="sensor_1", filename=str(tmp_file))
    reading = bad_sensor.read_sensor()

    assert reading.sensor_id == "sensor_1"
    assert reading.value == 32.0

    bad_sensor.save_to_database(reading)

    assert tmp_file.exists()
    assert tmp_file.read_text() == "sensor_1: 32.0\n"


def test_srp_good(tmp_path) -> None:
    tmp_file = tmp_path / "log_bueno.txt"
    good_sensor = GoodSensorReading(sensor_id="sensor_2")
    reading = good_sensor.read_sensor()

    assert reading.sensor_id == "sensor_2"
    assert reading.value == 32.0

    logger = DatabaseLogger(filename=str(tmp_file))
    logger.save(reading)

    assert tmp_file.exists()
    assert tmp_file.read_text() == "sensor_2: 32.0\n"
