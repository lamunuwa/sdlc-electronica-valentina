# ADR-003: Arquitectira Append-Only para Lecturas y su Monitoreo

- **Estado:** Aceptado
- **Fecha:** 2026-08-15
- **Autores:** Anna Valentina (LaMunuwa)

## Contexto

SensorHub está diseñada como una API para un entorno de monitoreo industrial donde la ingesta de datos genera un flujo masivo y constante de eventos. Cada lectura registrada por un sensor representa una variable física real (temperatura, voltaje, vibración, etc.) capturada en un instante específico de tiempo.

El modelo estándar REST propone usar un CRUD completo (Create, Read, Update, Delete). Sin embargo, en un dominio industrial:

- Un hecho físico como lo son las lecturas de un sensor debe ser persistido. La modificación o eliminación posterior compromete la fiabilidad de las métricas.

También existe un conflicto con la idempotencia por hashing. SensorHub utiliza una huella criptográfica SHA-256 (`hash_id`, definido en el ADR-02). Permitir la edición de lecturas rompería la consistencia del hash de identificación original, provocando posibles duplicaciones evasivas y manipulación de reportes.

## Decisión

Opté por un diseño mixto para SensorHub:

- **Sensores:** Se implementa un CRUD completo (GET, POST, PUT, DELETE).
- **Lecturas:** Se adopta un Modelo Append-Only (creación y consulta únicamente), omitiendo los endpoints de modificación (PUT) y eliminación (DELETE).

## Opciones Consideradas

1. CRUD Convencional en Lecturas (Permitir PUT/PATCH/DELETE):
    - Ventajas: Cumple con el patrón REST.
    - Desventajas: Expone el historial a manipulación, invalida la estrategia de idempotencia basada en el `hash_id` criptográfico y genera "sobrecódigo" para sincronizar hashes editados. Inclusive, según el estándar HTTP, DELETE administra el ciclo de vida de un recurso.
2. Borrado Lógico (Soft Delete mediante `is_deleted`):
    - Ventajas: Permite simular la eliminación REST.
    - Desventajas: Introduce complejidad innecesaria y sigue permitiendo que un cliente descarte evidencia real sin control.

## Consecuencias

**Positivas (Beneficios):**

- La base de datos actúa como una bitácora inalterable, ideal para inspección de fallas.
- Complementa a SHA-256, asegurando la consistencia entre el identificador y el contenido del registro.
- Reducimos complejidad y mantenimiento. Al acotar las operaciones permitidas sobre lecturas a POST y GET, se elimina la necesidad de manejar lógica de sincronización, bloqueos por concurrencia durante actualizaciones o estados fragmentados.

**Negativas (Riesgos / Deuda técnica asumida):**

- Si un dispositivo defectuoso emite mediciones erróneas con un `timestamp` válido, la lectura quedará registrada sin posibilidad de rectificación, requiriendo intervención a nivel de base de datos o herramientas especializadas de limpieza de datos si el caso lo amerita.
- No cumple con el 100% de los requisitos del curso. Sin embargo, dicho por la propia guía "recortar con criterio también es ingeniería", esta es una decisión bien justificada que genera más avance que retroceso.
