# Comparacion entre prompts (basico vs estructurado)

Este documento registra las comparativas entre estrategias de prompting (básico vs. estructurado) aplicadas a tareas reales de diseño de software y requerimientos para la API de SensorHub. El objetivo es analizar cómo el contexto, las restricciones y la especificación del dominio reducen la alucinación y mejoran la precisión del resultado.

**Nota:** Todos los prompts "básicos" los ejecuté en archivos copia de los originales para no generar problemas; cumple con el cometido, pero nunca entró en la API realmente.

---

## Tarea 2

### Prompt basico

> Hazme los tests en pytest para estos escenarios gherkin de anomalias.

### Prompt estructurado

> CONTEXTO: En la tarea anterior definimos los escenarios Gherkin para el sistema de anomalias y alertas (basicas) en docs/BACKLOG.md. Ahora debemos aplicar TDD creando primero la suite de pruebas que valide la implementacion del feature.
>
> TAREA: Escribe la suite de tests TDD en `test/test_api.py` traduciendo los escenarios Gherkin del backlog.
>
> RESTRICCIONES:
>
> - Utiliza exclusivamente las librerias/imports que ya existen en tests/test_api.py (por ejemplo: pytest, datetime, etc.) y las importaciones internas de la propia API (creo que en este feat no se agregan mas modelos que deban ser importados). Solo se permiten imports externos si es tecnicamente imposible realizar la prueba sin el o en caso de que exista un modelo nuevo en la API que deba ser importado.
> - Las funciones de prueba deben cumplir con Ruff y Mypy, puedes correr `mypy app test` y `ruff check app test`.
> - Los tests deben probar ESTRICTAMENTE TODOS los casos escritos en docs/BACKLOG.md.
> - Debes usar la misma estructura de todos los test del archivo `test/test_api.py`, es decir, escribir literalmente el given, when, then, and encima de las lineas de codigo como comentario
>
> ENTREGA: Unicamente el codigo Python para el archivo de tests.

### Análisis Comparativo

| Criterio | Prompt Básico | Prompt Estructurado |
| :--- | :--- | :--- |
| **¿Por qué es malo/bueno?** | Lo mismo que en la tarea anterior, la ambigüedad es un factor de muerte para el prompt, agregando que en ese chat no hay nada de donde guiarse. | Es un prompt que tiene muchos factores positivos; para mí el principal es el historial. Tiene una referencia clara, específica y revisada de qué debe hacer; las restricciones son bastante específicas, entonces no debería equivocarse justamente en los puntos que más mermaron mi tiempo en el curso. Además, usa la terminal para revisar los linters automáticamente. |
| **Resultados obtenidos** | Este prompt pudo ser útil en un contexto donde no tengo una API ya bastante avanzada; los test que genero cumplen con lo puesto en los US, pero no es lo que necesito. | Todos los test parecen tener sentido; no generé aún las modificaciones al código para probarlos, pero todos mantienen una estructura que ya entiendo, son prácticamente iguales a como yo los hago, siguen también la misma estructura de comentarios de Gherkin y, a pesar de no habérselo pedido, los dividió en secciones como yo lo hago. Siguió a la perfección todas las restricciones; solo tuvo un error: al ejecutar mypy y ruff no pudo, ya que no activó el .venv. Esta es una muestra de cómo las restricciones pueden ayudar a no alucinar, pero también no le permiten a la IA salirse de ellas. |

## Tarea 1

### Prompt basico

> Escribeme los escenarios de pruebas en gherkin para la detección de anomalias y alertas en mi API de sensores.

### Prompt estructurado

> CONTEXTO: Para el desarrollo de la API de SensorHub suelo aplicar gherkin para organizar los features. Los escribo como user stories usando la siguiente estructura: prioridad (en MoSCoW) -> dificultad (en story points) -> As, I want to, So that (para el story) -> gherkin
>
> Esta vez necesito desarrollar un sistema que detecte y notifique anomalias, es decir, al recibir una lectura se evalua contra un umbral configurable por sensor, si lo supera registra una alerta consultable en un endpoint. Actualmente tengo un sistema que revisa limites fisicos reales, todos los sensores se limitan por eso, no hay forma de configurar umbrales por sensor.
>
> TAREA: Genera en docs/BACKLOG.md los US usando la estructura que uso.
>
> RESTRICCIONES:
>
> - Escribe las US en la parte de hasta arriba por debajo del titulo y descripcion, como si fuera un changelog.
> - Usa nombres de entidades precisos (por ejemplo: alerta, sensor_umbral), con el fin de usar esos mismos nombres y que sea mas fácil el debug.
> - Divide las US por responsabilidades: no hagas un "US: Todo" y metas 10 escenarios de gherkin, mejor divide (ESTOS SON EJEMPLOS): US-01: Umbrales configurables por sensor, US-02: Deteccion de anomalias, US-03: Gestion de alertas consultables.
> - Toma de ejemplo los demas US que estan en el archivo.
>
> Ademas de eso me gustaria que el umbral se agregue en el registro del sensor, no como un endpoint aparte, es decir en el payload yo agregar los datos que ya existen y aparte el umbral, para poder modificarlo que sea en el apartado de actualizar un sensor, estos umbrales por como me imagino la arquitectura no deberian poderse borrar ni leer, me parece mejor implementacion dentro del modelo del sensor. Por parte de las alertas si que exista un endpoint, este SOLO puede leer, no crear, modificar o eliminar.
>
> ENTREGA: Unicamente el bloque de texto en el documento.

### Análisis Comparativo

| Criterio | Prompt Básico | Prompt Estructurado |
| :--- | :--- | :--- |
| **¿Por qué es malo/bueno?** | Es ambiguo. Al no especificar la metodología ni considerar la arquitectura existente (límites físicos vs. umbrales), perderia perdiendo tiempo refactorizando la respuesta manualmente. | Aquí delimité el contexto, definí ejemplos de los nombres de las entidades que necesito, exigí una metodología clara con su flujo y forcé la modularización en User Stories pequeñas por responsabilidad. |
| **Resultados obtenidos** | La IA hizo un poco lo que quiso: ignoró el proyecto, no revisó el documento base y simplemente entregó algo genérico. Ni siquiera enumeró las User Stories, lo que me confirma que no leyó el archivo. | Empezo de una base mucho más sólida: las User Stories quedaron donde las pedí y los gherkins tienen sentido con la arquitectura actual. Aunque agregó algunas notas extra que tuve que eliminar, fue mucho más preciso. Solo tuve 2 detalles: con los métodos HTTP (usó PATCH en lugar de PUT), lo cual asumo que pasó porque no le permití leer app/routers/ y no genero casos límite. |