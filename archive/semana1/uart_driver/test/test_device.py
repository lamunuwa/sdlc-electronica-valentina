import pytest

from semana1.uart_driver.config import Parity, StopBits, UartConfig
from semana1.uart_driver.device import ThreadSafe, UartDevice
from semana1.uart_driver.parsers import CanFrame, CanParser


@pytest.fixture
def uart_config():
    """Fixture para crear una configuración estándar de UART."""
    return UartConfig(baudrate=9600, parity=Parity.N, stop_bits=StopBits.One, timeout=1.0)


@pytest.fixture
def can_parser():
    return CanParser()


def test_initialization():
    buffer = ThreadSafe(capacity=2)
    assert buffer.capacity == 2
    assert len(buffer.buffer) == 0


def test_enqueue_success():
    buffer = ThreadSafe(capacity=2)

    assert buffer.enqueue(b"data1") is True
    assert buffer.enqueue(b"data2") is True
    assert len(buffer.buffer) == 2
    assert buffer.buffer == [b"data1", b"data2"]


def test_enqueue_full():
    buffer = ThreadSafe(capacity=2)

    assert buffer.enqueue(b"data1") is True
    assert buffer.enqueue(b"data2") is True
    assert len(buffer.buffer) == 2


def test_dequeue_success():
    buffer = ThreadSafe(capacity=2)
    buffer.enqueue(b"first")
    buffer.enqueue(b"second")

    assert buffer.dequeue() == b"first"
    assert buffer.dequeue() == b"second"
    assert len(buffer.buffer) == 0


def test_dequeue_empty():
    buffer = ThreadSafe(capacity=2)
    assert buffer.dequeue() is None


def test_device_initial(uart_config, can_parser):
    device = UartDevice(config=uart_config, parser=can_parser, buffer_capacity=2)
    assert device.connection is False
    assert len(device.buffer.buffer) == 0


def test_simulate_data_error(uart_config, can_parser):
    device = UartDevice(config=uart_config, parser=can_parser, buffer_capacity=2)
    with pytest.raises(ConnectionError, match="Puerto UART esta cerrado"):
        device.simulate_data(b"data")


def test_process_error(uart_config, can_parser):
    device = UartDevice(config=uart_config, parser=can_parser, buffer_capacity=2)
    with pytest.raises(RuntimeError, match="El dispositivo esta desconectado"):
        device.uart_proccess()


def test_process_empty_buffer(uart_config, can_parser):
    device = UartDevice(config=uart_config, parser=can_parser, buffer_capacity=2)
    device.connect()
    assert device.uart_proccess() is None


def test_process_complete_canbus(uart_config, can_parser):
    device = UartDevice(config=uart_config, parser=can_parser, buffer_capacity=2)
    device.connect()

    can_frame = bytes([0x5A, 0x01, 0x23, 0x04, 0xAA, 0xBB, 0xCC, 0xDD, 0x00, 0x00, 0x00, 0x00])

    device.simulate_data(can_frame)
    assert len(device.buffer.buffer) == 1

    result = device.uart_proccess()
    assert isinstance(result, CanFrame)
    assert result.id == 0x0123
    assert result.dlc == 4
    assert result.valid is True
    assert len(device.buffer.buffer) == 0
