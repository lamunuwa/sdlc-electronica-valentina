from collections.abc import Generator
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models.alerts import AlertInfo
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
    sensor = SensorInfo(
        name="TEMP-00",
        type="TEMPERATURE",
        unit="C",
        threshold_min=-40.0,
        threshold_max=40.0,
        ubication="Bodega A",
        active=True,
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    db.close()
    return sensor


@pytest.fixture
def temp_sensor_inactive() -> SensorInfo:
    db = sessionlocal()
    sensor = SensorInfo(
        name="TEMP-01",
        type="TEMPERATURE",
        unit="C",
        threshold_min=-40.0,
        threshold_max=40.0,
        ubication="Bodega B",
        active=False,
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    db.close()
    return sensor


@pytest.fixture
def temp_alert(temp_sensor: SensorInfo) -> AlertInfo:
    db = sessionlocal()

    # Creamos una lectura base para la alerta
    reading = ReadingInfo(sensor_id=temp_sensor.id, value=55.0, unit="C", timestamp=datetime.now())
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # Creamos la alerta
    alert = AlertInfo(
        sensor_id=temp_sensor.id,
        reading_id=reading.id,
        type="HIGH_TEMPERATURE",
        value=55.0,
        unit="C",
        state="open",
        timestamp=datetime.now(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    db.close()

    return alert


# Test para SENSORS endpoint --------------------------


# Funcionamiento correcto
def test_create_sensor_ok() -> None:
    payload = {
        "name": "TEMP-02",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"min": -10.0, "max": 50.0},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 201


def test_get_sensor_ok(temp_sensor: SensorInfo) -> None:
    response = client.get(f"/sensors/search?sensor_id={temp_sensor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == temp_sensor.id
    assert data["name"] == temp_sensor.name


def test_update_sensor_ok(temp_sensor: SensorInfo) -> None:
    payload = {"unit": "F"}
    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["unit"] == "F"


def test_delete_sensor_ok(temp_sensor: SensorInfo) -> None:
    response = client.delete(f"/sensors/delete?sensor_id={temp_sensor.id}")
    assert response.status_code == 204


# Funcionamiento incorrecto


# POST: create_sensor
def test_missing_fields_create_sensor() -> None:
    payload = {
        "name": "TEMP-02",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"min": None, "max": None},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 400


def test_name_too_long_create_sensor() -> None:
    name = "A" * 31
    payload = {
        "name": name,
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"min": -10.0, "max": 50.0},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 400


def test_invalid_type_create_sensor() -> None:
    payload = {
        "name": "TEMP-02",
        "type": "INVALID_TYPE",
        "unit": "C",
        "sensor_umbral": {"min": -10.0, "max": 50.0},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 422


def test_invalid_unit_create_sensor() -> None:
    payload = {
        "name": "TEMP-02",
        "type": "TEMPERATURE",
        "unit": "%",
        "sensor_umbral": {"min": -10.0, "max": 50.0},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 422


def test_threshold_min_greater_than_max_create_sensor() -> None:
    payload = {
        "name": "TEMP-02",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"min": 60.0, "max": 50.0},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 400


def test_threshold_out_of_range_create_sensor() -> None:
    payload = {
        "name": "TEMP-02",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"min": -300.0, "max": 50.0},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 400


def test_duplicate_name_create_sensor(temp_sensor: SensorInfo) -> None:
    payload = {
        "name": temp_sensor.name,
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"min": 0.0, "max": 10.0},
        "ubication": "Bodega A",
    }
    response = client.post("/sensors/create", json=payload)
    assert response.status_code == 409


# GET: get_sensor
def test_not_found_get_sensor() -> None:
    response = client.get("/sensors/search?sensor_id=99999")
    assert response.status_code == 404


def test_name_or_id_dont_match_get_sensor(temp_sensor: SensorInfo) -> None:
    response = client.get(f"/sensors/search?sensor_id={temp_sensor.id}&name=ANY")
    assert response.status_code == 400


def test_missing_fields_get_sensor() -> None:
    response = client.get("/sensors/search")
    assert response.status_code == 400


# PUT: update_sensor
def test_not_found_update_sensor() -> None:
    response = client.put("/sensors/update?sensor_id=99999", json={"unit": "F"})
    assert response.status_code == 404


def test_name_or_id_dont_match_update_sensor(temp_sensor: SensorInfo) -> None:
    payload = {"unit": "F"}
    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}&name=ANY", json=payload)
    assert response.status_code == 400


def test_missing_fields_update_sensor() -> None:
    response = client.put("/sensors/update", json={"unit": ""})
    assert response.status_code == 400


def test_nedded_changes_update_sensor(temp_sensor: SensorInfo) -> None:
    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}", json={})
    assert response.status_code == 400


def test_name_too_long_update_sensor(temp_sensor: SensorInfo) -> None:
    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}", json={"name": "B" * 31})
    assert response.status_code == 400


def test_invalid_type_update_sensor(temp_sensor: SensorInfo) -> None:
    response = client.put(
        f"/sensors/update?sensor_id={temp_sensor.id}", json={"type": "INVALID_TYPE"}
    )
    assert response.status_code == 422


def test_invalid_unit_update_sensor(temp_sensor: SensorInfo) -> None:
    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}", json={"unit": "%"})
    assert response.status_code == 422


def test_threshold_min_greater_than_max_update_sensor(temp_sensor: SensorInfo) -> None:
    payload = {"sensor_umbral": {"min": 60.0, "max": 50.0}}
    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}", json=payload)
    assert response.status_code == 400


def test_threshold_out_of_range_update_sensor(temp_sensor: SensorInfo) -> None:
    payload = {"sensor_umbral": {"min": -300.0, "max": 50.0}}
    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}", json=payload)
    assert response.status_code == 400


def test_duplicate_name_update_sensor(temp_sensor: SensorInfo) -> None:
    client.post(
        "/sensors/create",
        json={
            "name": "TEMP-02",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"min": -10.0, "max": 50.0},
            "ubication": "Bodega A",
        },
    )

    response = client.put(f"/sensors/update?sensor_id={temp_sensor.id}", json={"name": "TEMP-02"})
    assert response.status_code == 409


# DELETE: delete_sensor
def test_not_found_delete_sensor() -> None:
    response = client.delete("/sensors/delete?sensor_id=99999")
    assert response.status_code == 404


def test_name_or_id_dont_match_delete_sensor(temp_sensor: SensorInfo) -> None:
    response = client.delete(f"/sensors/delete?sensor_id={temp_sensor.id}&name=ANY")
    assert response.status_code == 400


def test_missing_fields_delete_sensor() -> None:
    response = client.delete("/sensors/delete")
    assert response.status_code == 400


def test_already_inactive_delete_sensor(temp_sensor: SensorInfo) -> None:
    client.delete(f"/sensors/delete?sensor_id={temp_sensor.id}")

    response = client.delete(f"/sensors/delete?sensor_id={temp_sensor.id}")
    assert response.status_code == 409


# -----------------------------------------------------


# Test para READINGS endpoint -------------------------

# Funcionamiento correcto


def test_create_reading_ok(temp_sensor: SensorInfo) -> None:
    payload = {"value": 20.5, "unit": "C", "timestamp": datetime.now().isoformat()}

    response = client.post(f"/readings/{temp_sensor.id}", json=payload)
    assert response.status_code == 201


def test_get_readings_ok(temp_sensor: SensorInfo) -> None:
    time = datetime.now() - timedelta(hours=1)

    for i in range(3):
        client.post(
            f"/readings/{temp_sensor.id}",
            json={
                "value": 10.0,
                "unit": "C",
                "timestamp": (time + timedelta(minutes=i)).isoformat(),
            },
        )

    response = client.get(f"/readings/search?sensor_id={temp_sensor.id}")
    assert response.status_code == 200
    assert len(response.json()) == 3


# Funcionamiento incorrecto


# POST: create_reading
def test_not_found_create_reading() -> None:
    payload = {"value": 25.0, "unit": "C"}
    response = client.post("/readings/99999", json=payload)
    assert response.status_code == 404


def test_sensor_inactive_create_reading(temp_sensor_inactive: SensorInfo) -> None:
    payload = {"value": 20.0, "unit": "C"}
    response = client.post(f"/readings/{temp_sensor_inactive.id}", json=payload)
    assert response.status_code == 400


def test_value_too_long_create_reading(temp_sensor: SensorInfo) -> None:
    payload = {"value": 123.456789123456789, "unit": "C"}
    response = client.post(f"/readings/{temp_sensor.id}", json=payload)
    assert response.status_code == 400


def test_duplicate_reading_create_reading(temp_sensor: SensorInfo) -> None:
    time = datetime.now().isoformat()
    payload = {"value": 25.0, "unit": "C", "timestamp": time}
    res_no_dup = client.post(f"/readings/{temp_sensor.id}", json=payload)
    assert res_no_dup.status_code == 201

    res_dup = client.post(f"/readings/{temp_sensor.id}", json=payload)
    assert res_dup.status_code == 409


def test_cant_processed_unit_create_reading(temp_sensor: SensorInfo) -> None:
    payload = {
        "value": 25.0,
        "unit": "V",
    }
    response = client.post(f"/readings/{temp_sensor.id}", json=payload)
    assert response.status_code == 400


def test_invalid_timestamp_create_reading(temp_sensor: SensorInfo) -> None:
    payload = {
        "value": 25.0,
        "unit": "C",
        "timestamp": "8/13/2026 a las 6:00pm",
    }
    response = client.post(f"/readings/{temp_sensor.id}", json=payload)
    assert response.status_code == 422


def test_timestiamp_future_create_reading(temp_sensor: SensorInfo) -> None:
    future_time = datetime.now() + timedelta(days=1)
    payload = {
        "value": 25.0,
        "unit": "C",
        "timestamp": future_time.isoformat(),
    }
    response = client.post(f"/readings/{temp_sensor.id}", json=payload)
    assert response.status_code == 400


# GET: get_readings
def test_missing_fields_get_readings() -> None:
    response = client.get("/readings/search")
    assert response.status_code == 400


def test_invalid_date_get_readings(temp_sensor: SensorInfo) -> None:
    response = client.get(f"/readings/search?sensor_id={temp_sensor.id}&from_date=YESTERDAY")
    assert response.status_code == 422


def test_not_found_get_readings() -> None:
    response = client.get("/readings/search?sensor_id=99999")
    assert response.status_code == 404


def test_name_or_id_dont_match_get_readings(temp_sensor: SensorInfo) -> None:
    response = client.get(f"/readings/search?sensor_id={temp_sensor.id}&name=INVALID_NAME")
    assert response.status_code == 400


# Test para ALERTS endpoint ---------------------------

# Funcionamiento correcto


def test_list_alerts_ok(temp_alert: AlertInfo) -> None:
    response = client.get("/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_alert_id_ok(temp_alert: AlertInfo) -> None:
    response = client.get(f"/alerts/{temp_alert.id}")
    assert response.status_code == 200
    assert response.json()["id"] == temp_alert.id


def test_get_alert_by_sensor_ok(temp_alert: AlertInfo, temp_sensor: SensorInfo) -> None:
    response = client.get(f"/alerts/sensor?sensor_id={temp_sensor.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_state_alert_ok(temp_alert: AlertInfo) -> None:
    payload = {"state": "acknowledged"}
    response = client.put(f"/alerts/{temp_alert.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["state"] == "acknowledged"


# Funcionamiento incorrecto


# GET: get_alert_by_sensor
def test_missing_fields_get_alert_by_sensor() -> None:
    response = client.get("/alerts/sensor")
    assert response.status_code == 400


def test_not_found_get_alert_by_sensor() -> None:
    response = client.get("/alerts/sensor?sensor_id=99999")
    assert response.status_code == 404


def test_name_or_id_dont_match_get_alert_by_sensor(temp_sensor: SensorInfo) -> None:
    response = client.get(f"/alerts/sensor?sensor_id={temp_sensor.id}&name=ANY")
    assert response.status_code == 400


def test_invalid_date_range_get_alert_by_sensor(temp_sensor: SensorInfo) -> None:
    response = client.get(
        f"/alerts/sensor?sensor_id={temp_sensor.id}&from_date=2026-12-31T00:00:00&to_date=2026-01-01T00:00:00"
    )
    assert response.status_code == 400


# GET: get_alert_id
def test_not_found_get_alert_id() -> None:
    response = client.get("/alerts/99999")
    assert response.status_code == 404


# GET: list_alerts
def test_invalid_date_range_list_alerts() -> None:
    response = client.get("/alerts?from_date=2026-12-31T00:00:00&to_date=2026-01-01T00:00:00")
    assert response.status_code == 400


# PUT: update_state_alert
def test_not_found_update_state_alert() -> None:
    payload = {"state": "acknowledged"}
    response = client.put("/alerts/99999", json=payload)
    assert response.status_code == 404


def test_missing_alert_status_update_state_alert(temp_alert: AlertInfo) -> None:
    response = client.put(f"/alerts/{temp_alert.id}", json={})
    assert response.status_code == 400


def test_invalid_alert_status_update_state_alert(temp_alert: AlertInfo) -> None:
    payload = {"state": "estado_invalido"}
    response = client.put(f"/alerts/{temp_alert.id}", json=payload)
    assert response.status_code == 400


def test_needed_changes_update_state_alert(temp_alert: AlertInfo) -> None:
    payload = {"state": "open"}
    response = client.put(f"/alerts/{temp_alert.id}", json=payload)
    assert response.status_code == 400


# -----------------------------------------------------
