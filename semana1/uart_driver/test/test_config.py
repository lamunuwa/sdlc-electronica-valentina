import pytest

from semana1.uart_driver.config import Parity, StopBits, UartConfig


def test_config_datos_validos():
    config = UartConfig(baudrate=9600, parity=Parity.N, stop_bits=StopBits.One, timeout=1.0)
    assert config.baudrate == 9600
    assert config.parity == Parity.N
    assert config.stop_bits == StopBits.One
    assert config.timeout == 1.0


def test_config_es_inmutable():
    config = UartConfig(baudrate=9600, parity=Parity.N, stop_bits=StopBits.One, timeout=1.0)
    with pytest.raises(Exception):
        config.baudrate = 115200  # type: ignore


def test_config_timeout_negativo():
    with pytest.raises(ValueError, match="Timeout no puede ser negativo"):
        UartConfig(baudrate=9600, parity=Parity.E, stop_bits=StopBits.Two, timeout=-0.5)
