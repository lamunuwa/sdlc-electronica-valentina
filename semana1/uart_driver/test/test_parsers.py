from semana1.uart_driver.parsers import (
    CanFrame,
    CanParser,
    ModbusFrame,
    ModBusParser,
    NMEAParser,
    NMEASentence,
)


def test_to_dict_format():  # ModBusFrame cuenta dentro de los test para ModBusParser
    frame = ModbusFrame(
        address=1,
        function=3,
        data=bytes([0xAA]),
        raw_data=bytes([1, 3, 0xAA, 0, 0]),
        crc=1234,
        crc_valid=True,
    )

    dic = frame.to_dict()
    assert dic["address"] == 1
    assert dic["function"] == 3
    assert dic["data"] == bytes([0xAA])
    assert dic["crc"] == 1234
    assert dic["crc_valid"]


def test_to_dict_cframe():
    frame = CanFrame(id=0x123, dlc=4, data=bytes([0x0A, 0x0B, 0x0C, 0x0D]), valid=True)

    dic = frame.to_dict()
    assert dic["id"] == 0x123
    assert dic["dlc"] == 4
    assert dic["data"] == "abcd"
    assert dic["valid"] is True


def test_nmea_to_dict():  # NMEASentence cuenta dentro de los test de NMEAParser
    sentence = NMEASentence(
        talker_id="GP",
        sentence_type="GGA",
        fields=["120000", "40.0", "N"],
        checksum_valid=True,
        raw_sentence="$GPGGA,...",
    )

    dic = sentence.to_dict()
    assert dic["talker_id"] == "GP"
    assert dic["sentence_type"] == "GGA"
    assert dic["fields"] == ["120000", "40.0", "N"]
    assert dic["checksum_valid"]


# Los siguientes 5 test son practicamentes todos iguales, son para validar que las restricciones
# funcionen correctamente, cuento los 5 como 1 dentro de los requerimientos del programa.


def test_can_parse_valid_standard_frame():  # 1
    parser = ModBusParser()
    valid_data = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A])
    assert parser.can_parse(valid_data) is True


def test_can_parse_valid_exception_frame():  # 2
    parser = ModBusParser()
    exception_data = bytes([0x01, 0x83, 0x02, 0x01, 0x31, 0xF0])
    assert parser.can_parse(exception_data) is True


def test_can_parse_invalid_length():  # 3
    parser = ModBusParser()
    short_data = bytes([0x01, 0x03, 0x55])  # Menos de 4 bytes
    assert parser.can_parse(short_data) is False


def test_can_parse_invalid_address():  # 4
    parser = ModBusParser()
    invalid_addr_1 = bytes([0x00, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A])
    invalid_addr_2 = bytes([0xF8, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A])  # 248 en hex
    assert parser.can_parse(invalid_addr_1) is False
    assert parser.can_parse(invalid_addr_2) is False


def test_can_parse_invalid_function():  # 5
    parser = ModBusParser()
    invalid_func = bytes([0x01, 0x20, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A])  # ox20 es invalido
    assert parser.can_parse(invalid_func) is False


def test_parse_successful_frame():
    parser = ModBusParser()
    data = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A])

    frame = parser.parse(data)

    assert frame is not None
    assert isinstance(frame, ModbusFrame)
    assert frame.address == 1
    assert frame.function == 3
    assert frame.data == bytes([0x00, 0x00, 0x00, 0x01])
    assert frame.raw_data == data
    assert frame.crc_valid is True
    assert frame.valid is True


def test_can_valid_frame():
    parser = CanParser()
    valid_data = bytes([0x5A, 0x01, 0x23, 0x04, 0x11, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00])
    assert parser.can_parse(valid_data) is True


def test_can_parse_success():
    parser = CanParser()
    bin_data = bytes([0x5A, 0x01, 0x23, 0x04, 0x0A, 0x0B, 0x0C, 0x0D, 0x00, 0x00, 0x00, 0x00])
    # Orden: SOF, ID, ID, DLC, Data... (ABCD)

    frame = parser.parse(bin_data)

    assert frame is not None
    assert isinstance(frame, CanFrame)
    assert frame.id == 0x0123
    assert frame.dlc == 4
    assert frame.data == bytes([0x0A, 0x0B, 0x0C, 0x0D])
    assert frame.valid is True


# Los siguientes 3 test son practicamentes todos iguales, son como los 5 de Parsers, cuento los 3
# como 1 dentro de los requerimientos del programa.


def test_nmea_can_parse_valid_gga():
    parser = NMEAParser()
    # Sentencia GGA típica de GPS (empieza con $, contiene GGA y termina con * y checksum)
    trama_valida = b"$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"
    assert parser.can_parse(trama_valida) is True


def test_nmea_can_parse_invalid_sentence_type():
    parser = NMEAParser()
    # Es una trama NMEA pero es RMC, no GGA (tu parser exige 'GGA' en el can_parse)
    trama_rmc = b"$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A\r\n"
    assert parser.can_parse(trama_rmc) is False


def test_nmea_can_parse_missing_elements():
    parser = NMEAParser()
    assert parser.can_parse(b"SOLO TEXTO") is False
    assert parser.can_parse(b"$GPGGA,sin_asterisco") is False


def test_nmea_parse_success():
    parser = NMEAParser()
    trama_real = b"$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"

    sentence = parser.parse(trama_real)

    assert sentence is not None
    assert isinstance(sentence, NMEASentence)
    assert sentence.talker_id == "GP"
    assert sentence.sentence_type == "GGA"
    assert sentence.checksum_valid is True
    assert sentence.valid is True
    # Verificamos que los campos se hayan separado correctamente por comas
    assert sentence.fields[0] == "123519"  # Hora UTC
    assert sentence.fields[1] == "4807.038"  # Latitud
