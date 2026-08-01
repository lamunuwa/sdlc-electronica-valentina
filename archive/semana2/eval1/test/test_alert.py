from pathlib import Path

from _pytest.capture import CaptureFixture
from semana2.eval1.alert import AlertManager, ConsoleAlert, FileAlert
from semana2.eval1.anomaly import AnomalyResult, AnomalyType


def test_mostrar_anomalia_consola(capsys: CaptureFixture) -> None:
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


def test_registrar_anomalia_archivo(tmp_path: Path) -> None:
    tmp_file = tmp_path / "alerts.log"
    # Given: un FileAlert configurado a "alerts.log"
    file_alert = FileAlert(str(tmp_file))

    # And: se ha detectado una anomalia HIGH_TEMPERATURE para sensor "TEMP-01" con valor 38.0
    anomaly = AnomalyResult(
        is_anomaly=True,
        anomaly_type=AnomalyType.HIGH_TEMPERATURE,
        sensor_id="TEMP-01",
        value=38.0,
    )
    # When: el FileAlert procesa la anomalia
    file_alert.process_anomaly(anomaly)
    # Then: el archivo "alerts.log" contiene el mensaje
    with open(tmp_file) as f:
        lines = f.readlines()
    assert any(
        "TEMP-01" in line and "HIGH_TEMPERATURE" in line and "38.0" in line for line in lines
    )


def test_archivo_acumula_entradas(tmp_path: Path) -> None:
    tmp_file = tmp_path / "alerts.log"
    # Given: el archivo "alerts.log" ya contiene 5 lineas
    with open(tmp_file, "w") as f:
        for i in range(5):
            f.write(f"ALERTA: Sensor TEMP-0{i}, HIGH_TEMPERATURE, {38.0 + i}\n")
    # And: un FileAlert configurado a "alerts.log"
    file_alert = FileAlert(str(tmp_file))
    # When: se registra una nueva anomalia
    anomaly = AnomalyResult(
        is_anomaly=True,
        anomaly_type=AnomalyType.HIGH_TEMPERATURE,
        sensor_id="TEMP-05",
        value=43.0,
    )
    file_alert.process_anomaly(anomaly)
    # Then: el archivo contiene 6 lineas
    with open(tmp_file) as f:
        lines = f.readlines()
    assert len(lines) == 6


def test_enviar_anomalia_todos_canales(capsys: CaptureFixture, tmp_path: Path) -> None:
    tmp_file = tmp_path / "alerts.log"
    # Given: AlertManager configurado con ConsoleAlert y FileAlert
    alert_manager = AlertManager()
    alert_manager.add_handler(ConsoleAlert())
    alert_manager.add_handler(FileAlert(str(tmp_file)))
    # And: anomalia HIGH_TEMPERATURE para sensor "TEMP-01" con valor 38.0
    anomaly = AnomalyResult(
        is_anomaly=True,
        anomaly_type=AnomalyType.HIGH_TEMPERATURE,
        sensor_id="TEMP-01",
        value=38.0,
    )
    # When: AlertManager procesa la anomalia
    alert_manager.process_anomaly(anomaly)
    captured = capsys.readouterr()
    # Then: ConsoleAlert recibe la anomalia
    assert "ALERTA: Sensor TEMP-01, HIGH_TEMPERATURE, 38.0" in captured.out
    # And: FileAlert recibe la anomalia
    with open(tmp_file) as f:
        lines = f.readlines()
    assert any(
        "TEMP-01" in line and "HIGH_TEMPERATURE" in line and "38.0" in line for line in lines
    )


def test_alert_manager_sin_canales() -> None:
    # Given: AlertManager sin canales configurados
    alert_manager = AlertManager()
    # And: anomalia HIGH_TEMPERATURE para sensor "TEMP-01" con valor 38.0
    anomaly = AnomalyResult(
        is_anomaly=True,
        anomaly_type=AnomalyType.HIGH_TEMPERATURE,
        sensor_id="TEMP-01",
        value=38.0,
    )
    # When: AlertManager procesa la anomalia
    alert_manager.process_anomaly(anomaly)
    # Then: no se produce ningun error
    # And: la anomalia se ignora silenciosamente
