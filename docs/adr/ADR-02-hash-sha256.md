# ADR-002: Estrategia de Deduplicación Mediante Hasheo Criptográfico SHA-256

- **Estado:** Aceptado
- **Fecha:** 2026-07-30
- **Autores:** Anna Valentina (LaMunuwa)

## Contexto

En sistemas de ingesta IoT masiva, los sensores pueden reenviar la misma lectura múltiples veces debido a fallas de red o reintentos automáticos. Para mantener la integridad de las métricas, es crítico prevenir el registro de lecturas duplicadas en el sistema.

## Decisión

Se implementó un mecanismo de deduplicación basado en un **Hash SHA-256**:

1. Antes de la persistencia, se genera una huella digital (hash) calculada a partir de la tupla: `(sensor_id + value + unit)`.
2. Se verifica la existencia del hash en el repositorio de lecturas mediante la función `by_hash`.
3. A nivel de base de datos, la columna `hash_id` se declaró con una restricción de unicidad (`UniqueConstraint`), sirviendo como una segunda barrera defensiva que evita la inserción en caso de condiciones de carrera.

## Opciones Consideradas

**Búsqueda por múltiples columnas (Composite WHERE / Composite UNIQUE):** En proyectos de pequeña escala, buscar por `sensor_id`, `value`, `unit` y `timestamp` es más simple y ahorra espacio (~40 bytes vs 64 bytes del hash). Sin embargo, se descartó como solución principal pensando en escenarios de producción real con millones de eventos en paralelo, donde se requiere un identificador único inmutable, apto para auditoría criptográfica y trazabilidad rápida.

## Consecuencias

**Positivas (Beneficios):**

- Proporciona una huella digital única estilo firma criptográfica para cada lectura ingesta.
- Consultar una sola columna indexada por valor de cadena exacta es computacionalmente eficiente para la base de datos.
- Garantiza cero duplicados tanto en la capa de aplicación (vía código) como en la de infraestructura (vía `UniqueConstraint`).

**Negativas (Riesgos / Deuda técnica asumida):**

- Cada registro almacena los 64 caracteres del hash SHA-256 en disco.
- Un string hexadecimal (ej. `5d10f6...`) no es legible a simple vista por un humano, requiriendo conocer la función generadora en el código para depurar el origen de los datos.
