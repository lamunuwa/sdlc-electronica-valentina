from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

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


def test_registro_exitoso() -> None:
    # Given: envio datos para un registro
    payload = {"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"}
    # When: hago POST /sensors
    response = client.post("/sensors/", json=payload)
    # Then: recibo 201 "Created" y verificamos
    assert response.status_code == 201
    data = response.json()
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
