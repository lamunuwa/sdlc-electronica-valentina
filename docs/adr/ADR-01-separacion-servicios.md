# ADR-001: Separación de Servicios en Módulos Especializados

- **Estado:** Aceptado
- **Fecha:** 2026-07-30
- **Autores:** Anna Valentina (LaMunuwa)

## Contexto

Inicialmente, la lógica de negocio, las reglas de validación física y la gestión de excepciones para los sensores y lecturas se encontraban acopladas en un archivo único o agrupadas de forma monolítica. A medida que la API creció, esta estructura resultaba poco escalable, difícil de mantener y complicada de depurar.

Dado que la capa de servicios (`services/`) alberga el núcleo de la lógica de la aplicación, se requería una mejor arquitectura que facilitara la mantenibilidad y la evolución del código a largo plazo.

## Decisión

Se decidió dividir la capa de servicios en tres módulos especializados aplicando el **Principio de Responsabilidad Única (SRP)**:

1. **`catalog.py`:** Administra exclusivamente el CRUD y ciclo de vida de los sensores.
2. **`validator.py`:** Se encarga de aislar la lógica de validaciones del dominio (unidades compatibles y rangos físicos aceptables), gestionando las excepciones propias de validación.
3. **`ingestion.py`:** Actúa como el orquestador principal del proceso de ingesta, coordinando la verificación del sensor, la validación, la generación del hash de deduplicación y la persistencia en la base de datos.

## Opciones Consideradas

**Mantener un archivo único por entidad (`sensors.py` y `readings.py`):** Descartado porque mezclaba la orquestación del flujo de base de datos con las reglas de validación física y la definición de excepciones, saturando la responsabilidad del servicio.

## Consecuencias

**Positivas (Beneficios):**

- Se pueden realizar tests unitarios sobre `validator.py` en milisegundos sin necesidad de mockear repositorios ni conectar una base de datos.
- Si falla una regla física, se corrige en `validator.py`; si falla el ciclo de vida del sensor, en `catalog.py`.
- Facilita la adición de nuevas reglas de ingesta o nuevos tipos de sensores sin alterar el orquestador.

**Negativas (Riesgos / Deuda técnica asumida):**

- Incremento menor en la cantidad de archivos y en la cantidad de imports necesarios en el router.
