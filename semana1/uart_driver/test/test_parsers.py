from semana1.uart_driver.parsers import ModbusFrame, ModBusParser


def test_to_dict_format():
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
