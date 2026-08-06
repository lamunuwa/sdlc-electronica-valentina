from collections.abc import Generator
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models.readings import ReadingInfo
from app.models.sensors import SensorInfo

db_url = "sqlite:///:memory:"

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def override_get_db() -> Generator[Session]:
    try:
        db = sessionlocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def set_db() -> Generator[None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def temp_sensor() -> SensorInfo:
    db = sessionlocal()
    sensor = SensorInfo(name="TEMP-01", type="TEMPERATURE", unit="C", active=True)
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    db.close()
    return sensor


# Test de US-01 ---------------------------------------
def test_verificar_estado_activo() -> None:
    # Given: SensorHub esta activo
    # When: envio una solicitud GET /health
    response = client.get("/health")
    # Then: recibo una respuesta HTTP con codigo de estado 200
    assert response.status_code == 200
    # And: la respuesta es '{"status": "ok"}'
    assert response.json() == {"status": "ok"}


# -----------------------------------------------------


# Test de US-02 ---------------------------------------
def test_registro_exitoso() -> None:
    # Given: envio datos para un registro
    payload = {"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"}
    # When: hago POST /sensors
    response = client.post("/sensors/", json=payload)
    # Then: recibo 201 "Created"
    assert response.status_code == 201
    data = response.json()
    # And: el sensor creado con toda su informacion
    assert data["name"] == "TEMP-01"
    assert data["type"] == "TEMPERATURE"
    assert data["unit"] == "C"
    assert "id" in data
    assert data["active"] is True


def test_nombre_duplicado() -> None:
    payload = {"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"}
    first_response = client.post("/sensors", json=payload)
    assert first_response.status_code == 201
    # Given: ya existe un sensor con el mismo nombre (reenvio el anterior)
    # When: envio POST /sensors
    response = client.post("/sensors", json=payload)
    # Then: recibo 409 ""Conflict" con sus detalles
    assert response.status_code == 409
    assert response.json()["detail"]


def test_payload_invalido() -> None:
    # When: envio datos incorrectos
    payload = {"name": "TEMP-01", "type": "TEMPERATURE"}  # Falta unit
    response = client.post("/sensors", json=payload)
    # Then: recibo 422 ""Unprocessable Entity"" con sus detalles
    assert response.status_code == 422
    assert response.json()["detail"]


# -----------------------------------------------------


# Test de US-03A --------------------------------------
def test_listar_sensores() -> None:
    client.post("/sensors", json={"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"})
    client.post("/sensors", json={"name": "PRESS-01", "type": "PRESSURE", "unit": "BAR"})
    # Given: existen sensores registrados
    # When: envio GET /sensors
    response = client.get("/sensors")
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    # And: la lista completa
    assert len(response.json()) >= 2


def test_actualizacion_sensor() -> None:
    sensor = client.post(
        "/sensors", json={"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"}
    ).json()["id"]
    # Given: un sensor existente
    # When: hago PATCH /sensors/{id} con {"unit": "F"}
    response = client.put(f"/sensors/{sensor}", json={"unit": "F"})
    # Then recibo 200 "OK"
    assert response.status_code == 200
    assert response.json()["name"] == "TEMP-01"  # Verificacion
    # And: los datos actualizados
    assert response.json()["unit"] == "F"


def test_desactivar_sensor() -> None:
    sensor = client.post(
        "/sensors", json={"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"}
    ).json()
    sensor_id = sensor["id"]
    # Given: un sensor existente
    # When: hago DELETE /sensors/{id}
    response = client.delete(f"/sensors/{sensor_id}")
    # Then: recibo 204 "No Content"
    assert response.status_code == 204
    for_response = client.get(f"/sensors/{sensor_id}")
    assert for_response.status_code == 200
    # And el sensor tiene active=false (eliminacion parcial)
    assert for_response.json()["active"] is False


# -----------------------------------------------------
