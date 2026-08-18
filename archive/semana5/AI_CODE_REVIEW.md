# AI CODE REVIEW

| Archivo a revisar | IA que reviso |
| :--- | :--- |
| `app/services/catalog.py` | Gemini 3.6 Flash *(Razonamiento Extendido)* |

---

## Evaluación

### 1. Inyección de Dependencias (Violación de SOLID - DIP)

- Línea 19: def __init__(self, repository: SensorRepository) -> None:

- Problema: Dependes directamente de una clase concreta (SensorRepository) en lugar de un protocolo o interfaz abstracta (AbstractSensorRepository o Protocol). Esto dificulta el unit testing y restringe el principio de Inversión de Dependencias (DIP).

```python
# Sugerencia de la IA
from typing import Protocol

class ISensorRepository(Protocol):
    def by_name(self, name: str) -> SensorInfo | None: ...
    def create(self, sensor_in: SensorCreate) -> SensorInfo: ...
    def list_sensor(self, limit: int, offset: int, show_inactive: bool) -> list[SensorInfo]: ...
    def update(self, sensor: SensorInfo, sensor_in: SensorUpdate) -> SensorInfo: ...
    def deactivate(self, sensor: SensorInfo) -> SensorInfo: ...

class SensorService:
    def __init__(self, repository: ISensorRepository) -> None:
        self.repository = repository
```

### STATUS: RECHAZADO

La clase `SensorService` ya respeta el Principio de Inversión de Dependencias (DIP).

- SensorRepository ya es un Protocol (una abstracción) y no una implementación concreta vinculada a SQLAlchemy.

- Análisis de arquitectura:

    - La dependencia heredada `ValidateSensorParameters.search_sensor` y la importación directa desde `app.core.limits` podrían considerarse acoplamientos teóricos, pero abstraerlos añadiría complejidad innecesaria sin aportar valor real.

    - Funciones de `app.core.limits`: Cumplen SRP, son puras y carecen de efectos secundarios.

    - `ValidateSensorParameters`: Inyecta self.repository, preservando la testeabilidad.

### 2. Validación de Dominio en Capa de Servicio vs Schema (SOLID - SRP)

- Líneas 43, 89: if len(sensor_in.name) > 30:

- Problema: La validación de la longitud máxima del string (len > 30) le pertenece a la capa de esquemas/DTOs (Pydantic con Field(max_length=30)). Mezclar validaciones de formato simple en el servicio ensucia la lógica de negocio.

```Python
# Sugerencia de la IA
name: str = Field(..., max_length=30)
```

### STATUS: RECHAZADO

La IA no verificó la capa de esquemas. El límite máximo de 30 caracteres ya está configurado en el esquema Pydantic correspondiente.

### 3. Falta de Paginación Límite Superior / Denial of Service (Riesgo de Seguridad & Rendimiento)

- Líneas 55-59: def list_sensors(self, limit: int = 50, offset: int = 0, ...)

- Problema: No hay acotación máxima sobre limit ni validación contra limit < 0 / offset < 0. Un cliente podría enviar limit=1000000 consumiendo memoria masiva en base de datos o API (DoS).

```Python
# Sugerencia de la IA
def list_sensors(
    self, limit: int = 50, offset: int = 0, show_inactive: bool = False
) -> list[SensorInfo]:
    limit = max(1, min(limit, 100)) # Clampear límite entre 1 y 100
    offset = max(0, offset)
    return self.repository.list_sensor(limit=limit, offset=offset, show_inactive=show_inactive)
```

### STATUS: ACEPTADO

Vulnerabilidad de rendimiento confirmada.

- Resolución: En lugar de silenciar o clampear el valor, se lanzará explícitamente la excepción `LimitExceededError` si limit > 100/50 dependiendo.

### 4. Condición de Carrera Time-of-Check to Time-of-Use / TOCTOU (Riesgo de Seguridad / Concurrencia)

- Líneas 50-51 & 91-92: if self.repository.by_name(sensor_in.name): raise SensorNameDuplicateError...
- Problema: Verificar la existencia antes de insertar en dos pasos no atómicos genera condiciones de carrera (dos peticiones simultáneas pueden pasar la condición de by_name e intentar insertar a la vez).

```Python
# Sugerencia de la IA
try:
    return self.repository.create(sensor_in)
except IntegrityError: # Capturar error de BD
    raise SensorNameDuplicateError(sensor_in.name)
```

### STATUS: ACEPTADO

Riesgo de concurrencia válido.

- Resolución: Delegar unicidad a la restricción UNIQUE de la base de datos y capturar `IntegrityError` de SQLAlchemy para mapearlo a `SensorNameDuplicateError`.

### 5. Inconsistencia en la Invalidez de Umbrales al Actualizar (Caso Borde)

- Líneas 95-106: Actualización parcial de tipo, unidad y umbrales.

- Problema: Si la petición SensorUpdate cambia el type o la unit de un sensor pero NO envía sensor_umbral, la llamada validate_sensor_configuration(sensor_type, sensor_unit) valida la nueva unidad, pero nunca re-valida si los umbrales antiguos de la base de datos (sensor.threshold_min, sensor.threshold_max) son válidos para la nueva unidad/tipo.

```Python
# Sugerencia de la IA
if sensor_in.type is not None or sensor_in.unit is not None or sensor_in.sensor_umbral is not None:
    min_val = threshold.min if (sensor_in.sensor_umbral and threshold.min is not None) else sensor.threshold_min
    max_val = threshold.max if (sensor_in.sensor_umbral and threshold.max is not None) else sensor.threshold_max
    self.validate_sensor_threshold(sensor_type, sensor_unit, min_val, max_val)
```

### STATUS: RECHAZADO

La lógica del servicio ya evalúa la compatibilidad entre la nueva unidad y los umbrales existentes, lanzando un error si se detectan incongruencias (ej. `min_val = -20` al migrar de `C` a `K`).

---

Los 5 casos de prueba de esta revisión quedarán ubicados en la sección superior de la suite de pruebas: [test_api.py](test/test_api.py)