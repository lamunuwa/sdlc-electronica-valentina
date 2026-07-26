import json

from semana1.uart_driver.recorder import DataRecorder, Log


def test_recorder_write_json(tmp_path):
    temp_file = tmp_path / "test.jsonl"
    recorder = DataRecorder(str(temp_file))

    record_1 = {"address": 1, "function": 3, "crc_valid": True}
    record_2 = {"address": 2, "function": 6, "crc_valid": False}

    recorder.open()
    recorder.record(record_1)
    recorder.record(record_2)
    recorder.close()

    with open(temp_file, encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 2
    assert json.loads(lines[0]) == record_1
    assert json.loads(lines[1]) == record_2


# Se refiere a que pueda soportar caracteres como acentos, emojis y caracteres especiales
def test_recorder_unicode_utf8(tmp_path):
    temp_file = tmp_path / "test_unicode.jsonl"
    recorder = DataRecorder(str(temp_file))

    unicode_data = {
        "talker_id": "GP",
        "sentence_type": "GGA",
        "raw": "$GPGGA,Ejemplo: línea_#$😂",
    }

    recorder.open()
    recorder.record(unicode_data)
    recorder.close()

    with open(temp_file, encoding="utf-8") as f:
        line = f.readline()

    assert json.loads(line) == unicode_data


# Test para Loggind JSON


def test_info(capsys):
    Log.log_json("info", "test_event", {"key": "value"})

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out.strip())

    assert log_entry["level"] == "INFO"
    assert log_entry["event"] == "test_event"
    assert log_entry["metadata"] == {"key": "value"}


def test_warning(capsys):
    Log.log_json("warning", "buffer_full", {"capacity": 10})

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out.strip())

    assert log_entry["level"] == "WARNING"
    assert log_entry["event"] == "buffer_full"
    assert log_entry["metadata"] == {"capacity": 10}


def test_metadata_none(capsys):
    Log.log_json("info", "simple_event", None)

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out.strip())

    assert log_entry["level"] == "INFO"
    assert log_entry["event"] == "simple_event"
    assert log_entry["metadata"] == {}


def test_unicode(capsys):
    unicode_metadata = {"message": "línea_#$😂"}

    Log.log_json("info", "unicode_event", unicode_metadata)

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out.strip())

    assert log_entry["level"] == "INFO"
    assert log_entry["event"] == "unicode_event"
    assert log_entry["metadata"] == unicode_metadata
