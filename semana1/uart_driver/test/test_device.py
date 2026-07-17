import pytest

from semana1.uart_driver.config import Parity, StopBits, UartConfig
from semana1.uart_driver.device import UartDevice
from semana1.uart_driver.parsers import ModbusFrame, ModBusParser


@pytest.fixture
def uart_config():
    """Fixture para crear una configuración estándar de UART."""
    return UartConfig(baudrate=9600, parity=Parity.N, stop_bits=StopBits.One, timeout=1.0)


@pytest.fixture
def modbus_parser():
    """Fixture para inyectar un parser válido."""
    return ModBusParser()


def test_device_initial(uart_config, modbus_parser):
    device = UartDevice(config=uart_config, parser=modbus_parser)
    assert device.connection is False
    assert len(device.buffer) == 0


def test_simulate_data_error(uart_config, modbus_parser):
    device = UartDevice(config=uart_config, parser=modbus_parser)
    with pytest.raises(ConnectionError, match="Puerto UART está cerrado"):
        device.simulate_data(b"data")


def test_process_error(uart_config, modbus_parser):
    device = UartDevice(config=uart_config, parser=modbus_parser)
    with pytest.raises(RuntimeError, match="El dispositivo está desconectado"):
        device.uart_proccess()


def test_process_empty_buffer(uart_config, modbus_parser):
    device = UartDevice(config=uart_config, parser=modbus_parser)
    device.connect()
    assert device.uart_proccess() is None


def test_process_complete(uart_config, modbus_parser):
    device = UartDevice(config=uart_config, parser=modbus_parser)
    device.connect()

    valid_frame = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A])
    device.simulate_data(valid_frame)
    assert len(device.buffer) == 1

    result = device.uart_proccess()
    assert isinstance(result, ModbusFrame)
    assert result.valid is True
    assert len(device.buffer) == 0
