from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
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
    response = client.patch(f"/sensors/{sensor}", json={"unit": "F"})
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


# Test de US-03B --------------------------------------
def test_obtener_ID_inexistente() -> None:
    # When: GET /sensors/9999
    response = client.get("/sensors/9999")
    # Then: recibo 404 "Not Found"
    assert response.status_code == 404
    assert response.json()["detail"]


def test_actualizar_ID_inexistente() -> None:
    # When: PATCH /sensors/9999 con {"unit": "F"}
    response = client.patch("/sensors/9999", json={"unit": "F"})
    # Then: recibo 404 "Not Found"
    assert response.status_code == 404
    # And: un mensaje de error
    assert response.json()["detail"] == "El sensor con id '9999' no encontrado"


def test_actualizacion_nombre_duplicado() -> None:
    sensor1 = client.post(
        "/sensors", json={"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"}
    ).json()["id"]
    client.post("/sensors", json={"name": "TEMP-02", "type": "TEMPERATURE", "unit": "C"}).json()[
        "id"
    ]
    # Given: existen sensores "TEMP-01" y "TEMP-02"
    # When hago PATCH /sensors/{""} con {"name": "TEMP-02"}
    response = client.patch(f"/sensors/{sensor1}", json={"name": "TEMP-02"})
    # Then: recibo 409 "Conflict"
    assert response.status_code == 409
    # And: un mensaje de error
    assert response.json()["detail"] == "El sensor con el nombre 'TEMP-02' ya existe"


def test_desactivar_sensor_no_encontrado() -> None:
    # When: hago DELETE /sensors/9999
    response = client.delete("/sensors/9999")
    # Then: recibo 404 "Not Found"
    assert response.status_code == 404
    assert response.json()["detail"]


# -----------------------------------------------------


# Test de US-04 ---------------------------------------
def test_lectura_valida(temp_sensor: SensorInfo) -> None:
    # Given: un sensor de tipo "TEMPERATURE"
    # When: {"value": 24.5, "unit": "C"} a /sensors/{id}/readings
    payload = {"value": 24.5, "unit": "C"}
    response = client.post(f"/sensors/{temp_sensor.id}/readings", json=payload)
    # Then: recibo 201 "Created"
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "timestamp" in data
    # And: el id de la lectura y timestamp
    assert data["sensor_id"] == temp_sensor.id
    assert data["value"] == 24.5
    assert data["unit"] == "C"
    assert "hash_id" in data


def test_sensor_no_encontrado() -> None:
    payload = {"value": 20.0, "unit": "C"}
    # When: mando lectura a /sensors/9999/readings
    response = client.post("/sensors/9999/readings", json=payload)
    # Then: recibo 404 "Not Found"
    assert response.status_code == 404
    assert response.json()["detail"] == "Sensor con id 9999 no encontrado"


def test_unidad_no_soportada(temp_sensor: SensorInfo) -> None:
    # Given: un sensor de temperatura
    payload = {"value": 20.0, "unit": "PSI"}
    # When: envio {"value": 20, "unit": "PSI"}
    response = client.post(f"/sensors/{temp_sensor.id}/readings", json=payload)
    # Then: recibo 422 "Unprocessable Entity"
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "PSI" in detail
    assert "TEMPERATURE" in detail


def test_valor_fuera_rango_fisico(temp_sensor: SensorInfo) -> None:
    # Given: un sensor de temperatura
    payload = {"value": -345.67, "unit": "C"}
    # When: {"value": -345.67, "unit": "C"}
    response = client.post(f"/sensors/{temp_sensor.id}/readings", json=payload)
    # Then: recibo 400 "Bad Request"
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "-273.15" in detail
    assert "-345.67" in detail


def test_lectura_duplicada_mismo_timestamp(temp_sensor: SensorInfo) -> None:
    payload = {
        "value": 24.5,
        "unit": "C",
    }
    datetime.now()
    response1 = client.post(f"/sensors/{temp_sensor.id}/readings", json=payload)
    assert response1.status_code == 201  # debe ser exitosa
    # Given: una lectura ya procesada con el mismo hash/timestamp
    # When: reenvio la misma lectura
    response2 = client.post(f"/sensors/{temp_sensor.id}/readings", json=payload)
    # Then recibo 409 "Conflict"
    assert response2.status_code == 409  # debe ser rechazada
    assert "duplicada" in response2.json()["detail"].lower()


# -----------------------------------------------------
