<p align="center">
  <img src="docs/images/LogoSensorHub.png" alt="LogoSensorHub" width="500">
</p>

---
<p align="center">
  <a href="https://github.com/lamunuwa/sdlc-electronica-valentina/actions/workflows/ci.yaml"><img src="https://img.shields.io/badge/CI-CHECK-brightgreen?style=flat&logo=githubactions&logoColor=white" alt="CI Status"></a> <a href="https://sensorhub-api-odm7.onrender.com/docs"><img src="https://img.shields.io/badge/Render-DOCS-46E3B7?style=flat&logo=render&logoColor=white" alt="Render Docs"></a> <a href="https://sensorhub-api-odm7.onrender.com/health"><img src="https://img.shields.io/badge/Render-HEALTH-0F5257?style=flat&logo=render&logoColor=white" alt="Render Health"></a> <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white" alt="Python Version"> <img src="https://img.shields.io/badge/FastAPI-v0.139.0-586F7C?style=flat&logo=fastapi&logoColor=white" alt="FastAPI Version">
</p>

**SensorHub** es un sistema de backend robusto para telemetría IoT industrial. Basado en **FastAPI** y diseñado para la ingesta, almacenamiento y análisis de datos provenientes de sensores en entornos críticos.

## Características

- **Sistema integral de sensores:** Realiza operaciones CRUD completas con desactivación lógica (soft delete), consulta por ID o nombre, estadísticas individuales y control del ciclo de vida.
- **Ingesta de lecturas idempotentes:** Registro masivo y unitario protegido por deduplicación hash SHA-256 (sensor + valor + unidad + timestamp), evitando datos duplicados en la red.
- **Validación de dominio robusta:** Validación dinámico de variables por sensor (TEMPERATURE, HUMIDITY, DISTANCE), unidades físicas reales y verificación de umbrales. Extensible a nuevos tipos de sensor.
- **Motor de alertas automatico:** Detección en tiempo real de anomalías (HIGH/LOW) ante lecturas fuera de rango, junto con la gestión de su ciclo de vida (OPEN, ACKNOWLEDGED, RESOLVED).
- **Paginación y filtrado flexible:** Consultas optimizadas con filtros y límite de resultados por paginación.
- **Métricas e inteligencia agregada:** Procesamiento en tiempo real de métricas descriptivas (totales, mínimos, máximos y promedios) agrupadas por sensor.
- **Arquitectura escalable:** Diseño basado en capas (Servicio, Repositorio, Modelo, Validación) alineado con principios SOLID, contenedorización en Docker y pipeline CI/CD automatizado.

## Stack Tecnológico

| Componente | Tecnología |
| :--- | :--- |
| **Lenguaje** | Python 3.12 |
| **Framework** | FastAPI + Uvicorn |
| **Validación & Schemas** | Pydantic |
| **Base de Datos** | PostgreSQL 16 |
| **ORM & Migraciones** | SQLAlchemy 2.0 + Alembic |
| **Contenerización** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |
| **QA & Linter** | Ruff, Mypy, Pytest + Coverage |

## Estructura del Repositorio

```text
├── .github/            # GitHub Actions
├── app/
│   ├── core/           # Configuración general
│   ├── models/         # Modelos de dominio y ORM
│   ├── repositories/   # Acceso a datos
│   ├── routers/        # Endpoints
│   ├── schemas/        # Esquemas y DTOs
│   └── services/       # Lógica de negocio y validaciones
├── archive/            # Archivos de prácticas pasadas
├── docs/               # Documentación de la API
├── migrations/         # Control de versiones de BD (Alembic)
├── test/               # Suite de pruebas
├── Dockerfile          # Imagen para contenedores
├── requirements.txt    # Dependencias del proyecto
├── docker-compose.yml  # Configuración del entorno de orquestación
└── render.yaml         # Infraestructura como Código (Render)
```

## Instalación

```bash
# Clona el repositorio
git clone https://github.com/lamunuwa/sdlc-electronica-valentina.git
cd sdlc-electronica-valentina

# Crea el entorno virtual
python3 -m venv .venv
# En Linux/macOS:
source .venv/bin/activate
# En Windows (PowerShell):
.venv\Scripts\activate

pip install -r requirements.txt

# Levanta contenedores
docker compose up o docker compose up -d
```

## Uso

Una vez levantado el servidor, la API estará disponible en `http://localhost:8000`.

- **Documentación Interactiva (Swagger):** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

También puedes probar la instancia desplegada en la nube sin levantar contenedores: https://sensorhub-api-odm7.onrender.com

## Testing

```bash
# Corre las pruebas y linters
pytest
ruff check app test
mypy app test
```

## Flujo secuencial

<p align="center">Flujo de los endpoint de SENSORS</p>

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as consumidor API
    participant API as FastAPI
    participant Servicio as SensorService
    participant Repo as SensorRepository
    participant DB as Base de datos

    Note over Cliente,DB: Crear un sensor
    Cliente->>API: POST /sensors/create
    API->>Servicio: create_sensor
    Servicio->>Repo: by_name (verificar duplicado)
    Repo->>DB: SELECT sensors WHERE name
    DB-->>Repo: sensor o ausencia
    Repo-->>Servicio: resultado
    Servicio->>Servicio: validar tipo/unidad y umbrales
    alt Nombre duplicado, tipo/unidad inválidos o umbral inconsistente
        Servicio-->>API: excepción de dominio
        API-->>Cliente: 400, 409 o 422
    else Configuración válida
        Servicio->>Repo: create
        Repo->>DB: INSERT sensors + COMMIT
        DB-->>Repo: sensor persistido
        Repo-->>Servicio: SensorInfo
        Servicio-->>API: SensorInfo
        API-->>Cliente: 201 Created
    end

    Note over Cliente,DB: Actualizar un sensor
    Cliente->>API: PUT /sensors/update?sensor_id o name
    API->>Servicio: update_sensor (lógica con PUT, body completo)
    Servicio->>Repo: search_sensor (localizar por id, nombre o ambos)
    Repo->>DB: SELECT sensors
    DB-->>Repo: sensor o ausencia
    Repo-->>Servicio: SensorInfo o SensorNotFoundError
    Servicio->>Repo: by_name (verificar duplicado)
    Repo-->>Servicio: resultado
    Servicio->>Servicio: validar tipo/unidad, umbrales y comparar body vs estado actual
    alt Sensor no encontrado, locator inválido, duplicado o config inválida
        Servicio-->>API: excepción de dominio
        API-->>Cliente: 400, 404 o 409
    else Body idéntico al estado actual
        Servicio-->>API: NeddedChangesToUpdateSensorError
        API-->>Cliente: 400
    else Reemplazo válido con cambios reales
        Servicio->>Repo: update (sobrescribe todos los campos)
        Repo->>DB: UPDATE sensors + COMMIT
        DB-->>Repo: sensor persistido
        Repo-->>Servicio: SensorInfo
        Servicio-->>API: SensorInfo
        API-->>Cliente: 200 OK
    end

    Note over Cliente,DB: Listar, buscar y desactivar un sensor
    Cliente->>API: GET /sensors/list o GET /sensors/search o DELETE /sensors/delete
    API->>Servicio: list_sensors / get_sensor / deactivate_sensor
    opt GET /sensors/search o DELETE /sensors/delete
        Servicio->>Repo: search_sensor (localizar por id, nombre o ambos)
        Repo->>DB: SELECT sensors
        DB-->>Repo: sensor o ausencia
        Repo-->>Servicio: SensorInfo o SensorNotFoundError
    end
    alt Sensor no encontrado, locator inválido, límite excedido o ya inactivo
        Servicio-->>API: excepción de dominio
        API-->>Cliente: 400, 404 o 409
    else Operación válida
        opt DELETE /sensors/delete
            Servicio->>Repo: deactivate
            Repo->>DB: UPDATE sensors SET active=false + COMMIT
            DB-->>Repo: sensor actualizado
        end
        Repo-->>Servicio: SensorInfo(s)
        Servicio-->>API: resultado
        API-->>Cliente: 200 OK o 204 No Content
    end

    Note over Cliente,DB: Estadísticas por sensor
    Cliente->>API: GET /sensors/statistics
    API->>Servicio: get_sensor_statistics
    Servicio->>Repo: search_sensor
    Repo->>DB: SELECT sensors
    DB-->>Repo: sensor o ausencia
    Repo-->>Servicio: SensorInfo o SensorNotFoundError
    Servicio->>Repo: get_statistics (COUNT/MIN/MAX/AVG)
    Repo->>DB: SELECT agregado sobre readings
    DB-->>Repo: total, min, max, avg
    Repo-->>Servicio: tupla de resultados
    alt fechas invertidas
        Servicio-->>API: InvalidDateRangeError
        API-->>Cliente: 400 o 404
    else sin lecturas en el periodo
        Servicio-->>API: SensorNoHaveReadingsError
        API-->>Cliente: 404
    else con lecturas
        Servicio-->>API: SensorStatisticsResponse
        API-->>Cliente: 200 OK
    end
```

---

<p align="center">Flujo de los endpoint de READINGS</p>

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as consumidor API
    participant API as FastAPI
    participant Servicio as ReadingService / AlertService
    participant Repo as SensorRepository / ReadingRepository / AlertRepository
    participant DB as Base de datos

    Note over Cliente,DB: Ingesta de lecturas y detección de anomalías
    Cliente->>API: POST /readings/{sensor_id}
    API->>Servicio: register_reading(sensor_id, datos)
    Servicio->>Repo: search_sensor (por sensor_id)
    Repo->>DB: SELECT sensors
    DB-->>Repo: sensor o ausencia
    Repo-->>Servicio: SensorInfo o SensorNotFoundError
    Servicio->>Servicio: ReadingValidator (activo, unidad soportada, timestamp no futuro)
    alt Sensor inexistente, inactivo, unidad inválida o fecha futura
        Servicio-->>API: excepción de dominio
        API-->>Cliente: 404 o 400
    else Lectura válida
        Servicio->>Servicio: compute_hash (SHA-256 de sensor, valor, unidad, timestamp)
        Servicio->>Repo: by_hash
        Repo->>DB: SELECT readings WHERE sensor_id, hash_id
        DB-->>Repo: existe o no existe
        Repo-->>Servicio: resultado
        alt Lectura duplicada
            Servicio-->>API: DuplicateReadingError
            API-->>Cliente: 409 Conflict
        else Lectura nueva
            Servicio->>Repo: create
            Repo->>DB: INSERT readings + COMMIT
            DB-->>Repo: ReadingInfo persistida
            Repo-->>Servicio: ReadingInfo
            Servicio-->>API: ReadingInfo
            API->>Servicio: AlertService.process_reading(lectura)
            Servicio->>Repo: by_id (sensor de la lectura)
            Repo->>DB: SELECT sensors
            DB-->>Repo: sensor con threshold_min/threshold_max
            Repo-->>Servicio: SensorInfo
            alt Valor fuera de threshold_min/threshold_max
                Servicio->>Repo: create_alert (state=OPEN, tipo HIGH_*/LOW_*)
                Repo->>DB: INSERT alerts + COMMIT
                DB-->>Repo: alerta persistida
            else Valor dentro de los umbrales
                Note over Servicio,DB: No se crea alerta
            end
            API-->>Cliente: 201 Created con la lectura
        end
    end

    Note over Cliente,DB: Consulta de lecturas
    Cliente->>API: GET /readings/search
    API->>Servicio: get_readings(sensor_id?, name?, fechas?, limit?, offset)
    Servicio->>Servicio: validar limit ≤ 100 y rango de fechas
    alt sensor_id y name ausentes
        alt limit no especificado
            Servicio-->>API: MissingRequiredFieldsError
            API-->>Cliente: 400
        else limit especificado
            Servicio->>Repo: get_reading (sin filtro de sensor)
            Repo->>DB: SELECT readings
            DB-->>Repo: lecturas
            Repo-->>Servicio: lista de ReadingInfo
            Servicio-->>API: lecturas
            API-->>Cliente: 200 OK
        end
    else sensor_id o name presentes
        Servicio->>Repo: search_sensor
        Repo->>DB: SELECT sensors
        DB-->>Repo: sensor o ausencia
        Repo-->>Servicio: SensorInfo o SensorNotFoundError
        alt sensor no encontrado o locator inválido
            Servicio-->>API: excepción de dominio
            API-->>Cliente: 400 o 404
        else sensor localizado
            Servicio->>Repo: get_reading (filtrado por sensor)
            Repo->>DB: SELECT readings
            DB-->>Repo: lecturas
            Repo-->>Servicio: lista de ReadingInfo
            Servicio-->>API: lecturas
            API-->>Cliente: 200 OK
        end
    end
```

---

<p align="center">Flujo de los endpoint de ALERTS</p>

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as consumidor API
    participant API as FastAPI
    participant Servicio as AlertService
    participant Repo as SensorRepository / AlertRepository
    participant DB as Base de datos

    Note over Cliente,DB: Consulta de alertas
    Cliente->>API: GET /alerts/list o GET /alerts/search o GET /alerts/{alert_id}
    API->>Servicio: get_all_alerts / get_alerts_by_sensor / get_alert
    opt GET /alerts/search
        Servicio->>Repo: search_sensor
        Repo->>DB: SELECT sensors
        DB-->>Repo: sensor o ausencia
        Repo-->>Servicio: SensorInfo o SensorNotFoundError
    end
    opt GET /alerts/{alert_id}
        Servicio->>Repo: get_by_id
        Repo->>DB: SELECT alerts WHERE id
        DB-->>Repo: alerta o ausencia
        Repo-->>Servicio: AlertInfo o AlertNotFoundError
    end
    opt GET /alerts/list o GET /alerts/search
        Servicio->>Servicio: validar fechas y límite ≤ 50
        Servicio->>Repo: get_all_alerts o get_alerts_by_sensor
        Repo->>DB: SELECT alerts
        DB-->>Repo: alertas
        Repo-->>Servicio: lista de AlertInfo
    end
    alt sensor/alerta no encontrada, locator inválido, fechas inválidas o límite excedido
        Servicio-->>API: excepción de dominio
        API-->>Cliente: 400 o 404
    else consulta válida
        Servicio-->>API: alerta(s)
        API-->>Cliente: 200 OK
    end

    Note over Cliente,DB: Actualizar estado de una alerta
    Cliente->>API: PUT /alerts/{alert_id}
    API->>Servicio: update_alert_state(alert_id, state)
    Servicio->>Servicio: validar state presente y en {OPEN, ACKNOWLEDGED, RESOLVED}
    Servicio->>Repo: get_by_id
    Repo->>DB: SELECT alerts WHERE id
    DB-->>Repo: alerta o ausencia
    Repo-->>Servicio: AlertInfo o AlertNotFoundError
    alt estado ausente, inválido o alerta no encontrada
        Servicio-->>API: excepción de dominio
        API-->>Cliente: 400 o 404
    else state igual al actual
        Servicio-->>API: NeededChangesToUpdateAlertError
        API-->>Cliente: 400
    else cambio válido
        Servicio->>Repo: update_alert
        Repo->>DB: UPDATE alerts + COMMIT
        DB-->>Repo: alerta persistida
        Repo-->>Servicio: AlertInfo
        Servicio-->>API: AlertResponse
        API-->>Cliente: 200 OK
    end
```

## Demo de SensorHub

<p align="center">
  <img src="docs/images/VideoMiniDemo.gif" alt="Demo de SensorHub API" width="700">
</p>

Para ver una explicación detallada del proyecto y su funcionamiento, puedes consultar el video de demostración completo aquí:
