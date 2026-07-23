from _pytest.capture import CaptureFixture

from semana2.eval1.alert import ConsoleAlert
from semana2.eval1.anomaly import AnomalyResult, AnomalyType


def test_console_alert_prints_message(capsys: CaptureFixture) -> None:
    # Given: un ConsoleAlert configurado
    console_alert = ConsoleAlert()
    # And anomalia HIGH_TEMPERATURE para sensor "TEMP-01" con valor 38.0
    # When: el ConsoleAlert procesa la anomalia
    console_alert.process_anomaly(
        AnomalyResult(
            is_anomaly=True,
            anomaly_type=AnomalyType.HIGH_TEMPERATURE,
            sensor_id="TEMP-01",
            value=38.0,
        )
    )
    captured = capsys.readouterr()
    # Then: imprime en consola un mensaje de alerta con el formato esperado
    assert captured.out.strip() == "ALERTA: Sensor TEMP-01, HIGH_TEMPERATURE, 38.0"
