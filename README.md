<p align="center">
  <img src="docs/images/LogoSensorHub.png" alt="LogoSensorHub" width="500">
</p>

---
<br>
<p align="center">
  <a href="https://github.com/lamunuwa/sdlc-electronica-valentina/actions/workflows/ci.yaml">
    <img src="https://img.shields.io/badge/CI-CHECK-brightgreen?style=flat&logo=githubactions&logoColor=white" alt="CI Status">
  </a>
  <a href="https://sensorhub-api-odm7.onrender.com/docs">
    <img src="https://img.shields.io/badge/Render-DOCS-46E3B7?style=flat&logo=render&logoColor=white" alt="Render Docs">
  </a>
  <a href="https://sensorhub-api-odm7.onrender.com/health">
    <img src="https://img.shields.io/badge/Render-HEALTH-0F5257?style=flat&logo=render&logoColor=white" alt="Render Health">
  </a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-v0.139.0-586F7C?style=flat&logo=fastapi&logoColor=white" alt="FastAPI Version">
</p>

**SensorHub** es un sistema de backend robusto para telemetría IoT industrial. Basado en **FastAPI** y diseñado para la ingesta, almacenamiento y análisis de datos provenientes de sensores en entornos críticos.

## Características

- **Gestión de sensores:** Registro, actualización, desactivación y consulta de datos de sensores.
- **Ingesta de lecturas:** Procesamiento de lecturas en tiempo real asociadas a cada dispositivo.
- **Validación estricta de dominios:** Control automático de tipos de variables (`TEMPERATURE`, `HUMIDITY`, `PRESSURE`, etc.), sus unidades físicas válidas (`°C`, `%`, `Pa`, etc.) y sus valores reales.
- **Arquitectura lista para escalar:** Separación en capas de servicio, repositorios, validaciones y modelos, diseñado con base en principios SOLID, listo para despliegue en contenedores y CI/CD automático.

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
├── docker-compose.yml  # Configuración del entorno de orquestación
├── requirements.txt    # Dependencias del proyecto
└── render.yaml         # Infraestructura como Código (Render)