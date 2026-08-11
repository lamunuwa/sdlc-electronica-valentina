# Comparacion entre prompts (basico vs estructurado)

Este documento registra las comparativas entre estrategias de prompting (básico vs. estructurado) aplicadas a tareas reales de diseño de software y requerimientos para la API de SensorHub. El objetivo es analizar cómo el contexto, las restricciones y la especificación del dominio reducen la alucinación y mejoran la precisión del resultado.

---

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