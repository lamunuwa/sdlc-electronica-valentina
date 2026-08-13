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
    sensor = SensorInfo(
        name="TEMP-01",
        type="TEMPERATURE",
        unit="C",
        threshold_min=-40.0,
        threshold_max=40.0,
        active=True,
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    db.close()
    return sensor


# Test de US-01: API base -----------------------------
def test_verificar_estado_activo() -> None:
    # Given: SensorHub esta activo
    # When: envio una solicitud GET /health
    response = client.get("/health")
    # Then: recibo una respuesta HTTP con codigo de estado 200
    assert response.status_code == 200
    # And: la respuesta es '{"status": "ok"}'
    assert response.json() == {"status": "ok"}


# -----------------------------------------------------


# Test de US-02: Registro de sensores -----------------
def test_registro_exitoso() -> None:
    # Given: envio datos para un registro
    payload = {
        "name": "TEMP-01",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"max": 35.0, "min": -40.0},
    }
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
    payload = {
        "name": "TEMP-01",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"max": 35.0, "min": -40.0},
    }
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
    payload = {"name": "TEMP-01", "type": "TEMPERATURE"}  # Falta unit y sensor_umbral
    response = client.post("/sensors", json=payload)
    # Then: recibo 422 ""Unprocessable Entity"" con sus detalles
    assert response.status_code == 422
    assert response.json()["detail"]


# -----------------------------------------------------


# Test de US-03A: Consulta de sensores ----------------
def test_listar_sensores() -> None:
    client.post(
        "/sensors",
        json={
            "name": "TEMP-01",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    )
    client.post(
        "/sensors",
        json={
            "name": "TEMP-02",
            "type": "TEMPERATURE",
            "unit": "K",
            "sensor_umbral": {"max": 100.0, "min": 0.0},
        },
    )
    # Given: existen sensores registrados
    # When: envio GET /sensors
    response = client.get("/sensors")
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    # And: la lista completa
    assert len(response.json()) >= 2


def test_actualizacion_sensor() -> None:
    sensor = client.post(
        "/sensors",
        json={
            "name": "TEMP-01",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
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
        "/sensors",
        json={
            "name": "TEMP-01",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
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


# Test de US-03B: Gestion de errores ------------------
def test_obtener_ID_inexistente() -> None:
    # When: GET /sensors/9999
    response = client.get("/sensors/9999")
    # Then: recibo 404 "Not Found"
    assert response.status_code == 404
    assert response.json()["detail"]


def test_actualizar_ID_inexistente() -> None:
    # When: PATCH /sensors/9999 con {"unit": "F"}
    response = client.put("/sensors/9999", json={"unit": "F"})
    # Then: recibo 404 "Not Found"
    assert response.status_code == 404
    # And: un mensaje de error
    assert response.json()["detail"] == "El sensor con id '9999' no encontrado"


def test_actualizacion_nombre_duplicado() -> None:
    sensor1 = client.post(
        "/sensors",
        json={
            "name": "TEMP-01",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    client.post(
        "/sensors",
        json={
            "name": "TEMP-02",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    # Given: existen sensores "TEMP-01" y "TEMP-02"
    # When hago PATCH /sensors/{""} con {"name": "TEMP-02"}
    response = client.put(f"/sensors/{sensor1}", json={"name": "TEMP-02"})
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


# Test de US-04: Registro de lecturas -----------------
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


def test_lectura_duplicada_mismo_contenido(temp_sensor: SensorInfo) -> None:
    time = datetime(2026, 7, 30, 12, 0, 0)
    payload = {"value": 24.5, "unit": "C", "timestamp": time.isoformat()}
    response1 = client.post(f"/sensors/{temp_sensor.id}/readings", json=payload)
    assert response1.status_code == 201
    # Given: una lectura ya procesada con el mismo contenido y, por tanto, el mismo hash
    # When: reenvio la misma lectura
    response2 = client.post(f"/sensors/{temp_sensor.id}/readings", json=payload)
    # Then recibo 409 "Conflict"
    assert response2.status_code == 409
    assert "duplicada" in response2.json()["detail"].lower()


# -----------------------------------------------------


# Test de US-05: Paginación y filtro por fechas -------
def test_paginacion_y_filtro_fechas(temp_sensor: SensorInfo) -> None:
    db = sessionlocal()
    base_date = datetime(2026, 7, 1, 0, 0, 0)
    readings = []
    for i in range(100):
        # Generamos lecturas separadas por 4 horas
        reading_time = base_date + timedelta(hours=i * 4)
        reading = ReadingInfo(
            sensor_id=temp_sensor.id,
            value=20.0 + (i % 5),
            unit="C",
            timestamp=reading_time,
            hash_id=f"hash_sample_{i}",
        )
        readings.append(reading)
    # Given: 100 lecturas para el sensor distribuidas en julio 2026
    db.add_all(readings)
    db.commit()
    db.close()
    """
    When: hago GET /sensors/{id}/readings
    from=2026-07-01T00:00:00
    to=2026-07-27T00:00:00
    limit=10
    offset=0
    """
    filter_params = {
        "from": "2026-07-01T00:00:00",
        "to": "2026-07-27T00:00:00",
        "limit": 10,
        "offset": 0,
    }
    response = client.get(f"/sensors/{temp_sensor.id}/readings", params=filter_params)
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    data = response.json()
    # And: exactamente las primeras 10 lecturas dentro del rango
    assert len(data) == 10
    first_timestamp = data[0]["timestamp"]
    assert "2026-07-01" in first_timestamp  # las lecturas deben estar dentro del rango especificado


def test_indices_justificados() -> None:
    # Given: la tabla "readings" tiene un indice compuesto (sensor_id, timestamp/created_at)
    inspector = inspect(engine)
    indexes = inspector.get_indexes("readings")

    # When: buscamos un indice que incluya "sensor_id" y "timestamp/created_at"
    index_found = False
    for idx in indexes:
        column_names = idx.get("column_names", [])
        if "sensor_id" in column_names and (
            "timestamp" in column_names or "created_at" in column_names
        ):
            index_found = True
            break

    # Then: se usa dicho indice
    assert index_found, "Indice compuesto en 'readings' con 'sensor_id, timestamp/created_at'"


def test_sensor_no_encontrado_lecturas() -> None:
    # When: consulto lecturas de un sensor inexistente
    response = client.get("/sensors/9999/readings")

    # Then: recibo 404 "Not Found"
    assert response.status_code == 404
    assert response.json()["detail"]


def test_validacion_parametros_consulta(temp_sensor: SensorInfo) -> None:
    # When: mando limit con un valor no numérico
    response = client.get(f"/sensors/{temp_sensor.id}/readings?limit=invalid_value")

    # Then: recibo 422 "Unprocessable Entity"
    assert response.status_code == 422
    assert response.json()["detail"]


# -----------------------------------------------------


# FIX-02: Tipos o unidades no soportadas --------------
def test_registro_con_tipo_no_soportado() -> None:
    payload = {
        "name": "TEMP-01",
        "type": "INVALID_TYPE",
        "unit": "C",
        "sensor_umbral": {"max": 35.0, "min": -40.0},
    }
    response = client.post("/sensors", json=payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "INVALID_TYPE" in detail


def test_registro_con_unidad_no_soportada() -> None:
    payload = {
        "name": "TEMP-01",
        "type": "TEMPERATURE",
        "unit": "PSI",
        "sensor_umbral": {"max": 35.0, "min": -40.0},
    }
    response = client.post("/sensors", json=payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "PSI" in detail
    assert "TEMPERATURE" in detail


def test_actualizacion_con_tipo_no_soportado() -> None:
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-01",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    response = client.put(f"/sensors/{sensor_id}", json={"type": "INVALID_TYPE"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "INVALID_TYPE" in detail


def test_actualizacion_con_unidad_no_soportada() -> None:
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-01",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    response = client.put(f"/sensors/{sensor_id}", json={"unit": "PSI"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "PSI" in detail
    assert "TEMPERATURE" in detail


# -----------------------------------------------------


# Test de US-01: Umbrales configurables ---------------
def test_registrar_sensor_con_umbral() -> None:
    # Given: envío un payload con un sensor_umbral configurado
    payload = {
        "name": "TEMP-01",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"max": 35.0, "min": -40.0},
    }
    # When: hago POST /sensors
    response = client.post("/sensors", json=payload)
    # Then: recibo 201 "Created"
    assert response.status_code == 201
    data = response.json()
    # And: el sensor creado contiene el umbral configurado
    assert data["sensor_umbral"]["max"] == 35.0
    assert data["sensor_umbral"]["min"] == -40.0


def test_actualizar_umbral_mediante_put() -> None:
    # Given: un sensor existente con umbral
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-02",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    # When: hago PUT /sensors/{id} con {"sensor_umbral": {"max": 30.0}}
    response = client.put(f"/sensors/{sensor_id}", json={"sensor_umbral": {"max": 30.0}})
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    data = response.json()
    # And: el sensor actualizado conserva el nuevo umbral
    assert data["sensor_umbral"]["max"] == 30.0


def test_registrar_sensor_sin_umbral() -> None:
    # Given: envío un payload con un sensor_umbral vacío
    payload = {
        "name": "TEMP-03",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"max": "", "min": ""},
    }
    # When: hago POST /sensors
    response = client.post("/sensors", json=payload)
    # Then: recibo 400 "Bad Request"
    assert response.status_code == 400


def test_validacion_umbral_invalido_en_registro() -> None:
    # Given: intento registrar un sensor con un umbral inválido
    payload = {
        "name": "TEMP-04",
        "type": "TEMPERATURE",
        "unit": "C",
        "sensor_umbral": {"max": "alto"},
    }
    # When: hago POST /sensors
    response = client.post("/sensors", json=payload)
    # Then: recibo 422 "Unprocessable Entity"
    assert response.status_code == 422
    # And: el mensaje indica que se requiere un valor numérico
    assert response.json()["detail"]


def test_validacion_umbral_invalido_en_actualizacion() -> None:
    # Given: existe un sensor válido
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-05",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    # When: intento actualizar un sensor con un umbral no numérico
    response = client.put(f"/sensors/{sensor_id}", json={"sensor_umbral": {"max": "alto"}})
    # Then: recibo 422 "Unprocessable Entity"
    assert response.status_code == 422
    # And: el mensaje indica que se requiere un valor numérico
    assert response.json()["detail"]


def test_registrar_sensor_con_umbral_minimo_mayor() -> None:
    # Given intento registrar un sensor con {"sensor_umbral":{"max": 20.0, "min": 30.0}}
    response = client.post(
        "/sensors",
        json={
            "name": "TEMP-06",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 20.0, "min": 30.0},
        },
    )
    # When hago POST /sensors
    # Then recibo 400 "Bad Request"
    assert response.status_code == 400
    # And el detalle indica "Umbral minimo no puede ser mayor que el umbral maximo"
    assert response.json()["detail"] == "Umbral minimo no puede ser mayor que el umbral maximo"


def test_registrar_sensor_con_umbral_fuera_de_rango_fisico() -> None:
    # Given intento registrar un sensor con {"sensor_umbral": {"max": 35.0, "min": -274.0}}
    response = client.post(
        "/sensors",
        json={
            "name": "TEMP-07",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -274.0},
        },
    )
    # When hago POST /sensors
    # Then recibo 400 "Bad Request"
    assert response.status_code == 400
    # And el detalle indica "Umbral minimo y/o umbral maximo fuera del rango fisico de C"
    assert response.json()["detail"] == (
        "Umbral minimo y/o umbral maximo fuera del rango fisico de C"
    )


# -----------------------------------------------------


# Test de US-02: Detección de anomalías ---------------
def test_lectura_que_supera_umbral_genera_alerta() -> None:
    # Given: un sensor con sensor_umbral.max = 35.0
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-08",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    # When: envío POST /sensors/{id}/readings con {"value": 36.5, "unit": "C"}
    response = client.post(f"/sensors/{sensor_id}/readings", json={"value": 36.5, "unit": "C"})
    # Then: recibo 201 "Created"
    assert response.status_code == 201
    alerts = client.get(f"/alerts?sensor_id={sensor_id}").json()
    # And: se persiste una alerta asociada al sensor con tipo HIGH_TEMPERATURE y value 36.5
    assert len(alerts) >= 1
    assert alerts[0]["sensor_id"] == sensor_id
    assert alerts[0]["type"] == "HIGH_TEMPERATURE"
    assert alerts[0]["value"] == 36.5


def test_lectura_dentro_de_umbral_no_genera_alerta() -> None:
    # Given: un sensor con sensor_umbral.max = 35.0
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-09",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    # When: envío POST /sensors/{id}/readings con {"value": 22.0, "unit": "C"}
    response = client.post(f"/sensors/{sensor_id}/readings", json={"value": 22.0, "unit": "C"})
    # Then: recibo 201 "Created"
    assert response.status_code == 201
    alerts = client.get(f"/alerts?sensor_id={sensor_id}").json()
    # And: no se crea ninguna alerta
    assert alerts == []


def test_alerta_incluye_metadatos_para_auditoria() -> None:
    # Given: se genera una alerta por lectura
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-10",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    client.post(f"/sensors/{sensor_id}/readings", json={"value": 36.5, "unit": "C"})
    # When: consulto las alertas del sensor
    response = client.get(f"/alerts?sensor_id={sensor_id}")
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    data = response.json()[0]
    # And: la alerta contiene id, sensor_id, type, value, unit, timestamp, reading_id
    for field in ["id", "sensor_id", "type", "value", "unit", "timestamp", "reading_id"]:
        assert field in data


# -----------------------------------------------------


# Test de US-03: Gestión de alertas -------------------
def test_listar_alertas_de_un_sensor() -> None:
    # Given: existen varias alertas asociadas a un sensor
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-11",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    client.post(f"/sensors/{sensor_id}/readings", json={"value": 36.5, "unit": "C"})
    client.post(f"/sensors/{sensor_id}/readings", json={"value": 37.0, "unit": "C"})
    # When: hago GET /alerts?sensor_id={id}&limit=10&offset=0
    response = client.get(f"/alerts?sensor_id={sensor_id}&limit=10&offset=0")
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    data = response.json()
    # And: la respuesta contiene una lista de alertas ordenadas por timestamp descendente
    assert len(data) >= 2
    assert all(item["sensor_id"] == sensor_id for item in data)
    assert data[0]["timestamp"] >= data[-1]["timestamp"]


def test_obtener_alerta_por_id() -> None:
    # Given: existe una alerta con id 1
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-12",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    client.post(f"/sensors/{sensor_id}/readings", json={"value": 36.5, "unit": "C"})
    alert_id = client.get(f"/alerts?sensor_id={sensor_id}").json()[0]["id"]
    # When: hago GET /alerts/{id}
    response = client.get(f"/alerts/{alert_id}")
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    data = response.json()
    # And: el cuerpo contiene los campos id, sensor_id, type, value, unit, timestamp, reading_id
    for field in ["id", "sensor_id", "type", "value", "unit", "timestamp", "reading_id"]:
        assert field in data


def test_filtrado_por_rango_de_fechas() -> None:
    # Given: existen alertas en un sensor en diferentes fechas
    sensor_id = client.post(
        "/sensors",
        json={
            "name": "TEMP-13",
            "type": "TEMPERATURE",
            "unit": "C",
            "sensor_umbral": {"max": 35.0, "min": -40.0},
        },
    ).json()["id"]
    first_timestamp = datetime(2026, 7, 10, 12, 0, 0)
    second_timestamp = datetime(2026, 7, 20, 12, 0, 0)
    payload_1 = {"value": 36.0, "unit": "C", "timestamp": first_timestamp.isoformat()}
    payload_2 = {"value": 38.0, "unit": "C", "timestamp": second_timestamp.isoformat()}
    client.post(f"/sensors/{sensor_id}/readings", json=payload_1)
    client.post(f"/sensors/{sensor_id}/readings", json=payload_2)
    # When: hago GET /alerts?from=2026-07-01T00:00:00&to=2026-07-31T23:59:59
    response = client.get(
        "/alerts",
        params={
            "sensor_id": sensor_id,
            "from": "2026-07-01T00:00:00",
            "to": "2026-07-31T23:59:59",
        },
    )
    # Then: recibo 200 "OK"
    assert response.status_code == 200
    data = response.json()
    # And: solo las alertas dentro del rango
    assert len(data) >= 2
    for item in data:
        assert item["sensor_id"] == sensor_id
