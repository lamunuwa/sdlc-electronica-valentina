import json

from semana1.uart_driver.recorder import DataRecorder


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
