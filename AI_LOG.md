# Registro de Uso de IA (AI Log)

Este documento registra las interacciones con Inteligencia Artificial generativa utilizadas como asistencia para el desarrollo de las actividades durante el curso.

**Nota:** En casi todas las entradas (generación de codigo) la IA comete errores menores que no explico, por ejemplo poner Dict en vez de dict.

---

## Semana 3

## Entrada 3

### Objetivo

Terminar los ultimos 3 archivos para feat commit de US-04.

### Prompt

> Generando la estructura para las lecturas y lo solicitado en docs/BACKLOG.md en la seccion de US-04, entre en completo burnout. Tener 8 archivos abiertos para escribir + BACKLOG + archivos de sensors para guiarme, es muy dificil, estoy confundiendome todo el rato de archivos, de nombres de funciones o clases y es poco eficaz esto que estoy haciendo.
>
> En los archivos services/ingestion.py y validators.py asi como routers/readings.py escribe el codigo faltante. En validators debes crear los errores de dominio, por ejemplos hacer la excepcion si el sensor no existe, si el sensor esta inactivo, si no soporta la unidad, valores fuera del rango permitido. En ingestion debes gestionar servicios de lectura de sensores:
>
> 1. Verifica que el sensor existe
> 2, Verifica que el sensor este activo
> 3. Valida la unidad de medida soportada
> 4. Valida el rango fisico, si esta dentro
> 5. Calcula el hash (clase para calcular el hash)
> 6. Verifica duplicados
> 7. Guarda la lectura
>
> Por ultimo en routers debes de agregar las rutas que apareceran en la API, en este caso creo que deberia ser un unico POST pero valida junto con BACKLOG.md

### Resultados

Impecables, salvo los típicos errores de IA, como poner Optional en vez de "| None" o pass en vez de "..." que tuve que arreglar manualmente, ya que no pasan los linters; al ejecutar pytest pasa con +99% de cobertura, sin errores de compilación o de lógica. Todavía no lo probé en el Swagger, solo validé los test; primero haré una refactorización del código completo, poniendo comentarios, mejorando legibilidad y, en general, dejar un código de US-04 completo; sin embargo, en este punto ya funciona.

## Entrada 2

### Objetivo

Probar Antigravity, ya que el anterior prompt era para texto y Gemini lo consideró un excelente modelo para platicar; lo hice en web. Esto, como es dentro de mi VSCode, no sé qué tan amigable sea la web para adjuntar todo un repositorio; entonces descargué y agregué la extensión de Antigravity a VSCode (la cual ya no funciona y tuve que descargar el IDE).

Debía buscar entre el repositorio las direcciones proporcionadas, entender el código, la lógica de negocio de cada archivo y darme una conclusión en base a mi análisis de qué va en cada carpeta y lo que encontró y si era correcto.

### Prompt

> Actua como un ingeniero en software o similares, experto en Python orientado a objetos y plataformas de servidores API y contenedores. En base a las US de docs/agile/BACKLOG.md al final de la semana debo tener una API con los entregables solicitados. En este momento genere todo lo de US-02, lo dividi ya en las capas que se mencionan pero no se si lo hice correctamente, revisa cada archivo de entre app/models/sensors.py, app/repositories/sensors.py, app/routers/sensors.py, app/schemas/sensors.py y app/services/catalog.py. La logica del sistema, la estructura, pero NO toques otros archivos que no sean los dichos, NO entres con la terminal, todo pasa en 100% de covertura por pytest. Solo necesito verificar que todo va donde debe ir
>
> Aqui te dejo un breve analisis/resumen de que deberia ir en cada carpeta, corrigeme en caso de ser necesario
>
> 1. app/models/: Define la estructura de las tablas en la base de datos. Son clases que mapean directamente tablas SQL mediante el ORM (SQLAlchemy).
> 2. app/schemas/: Valida datos que entran y salen de la API, el mas sencillo
> 3. app/services/: Tiene la logica de negocio, las operaciones, aplica reglas, valida restricciones, etc.
> 4. app/repositories/: Mete todas las operaciones de base de datos (CRUD). Es la unica que tiene "acceso" al interior de mi sensorhub.db
> 5. app/routers/: Recibe peticiones HTTP, es lo que en la pagina vemos como los rectangulos expandibles con informacion. Es la unica que tiene acceso a los servicios.

### Resultados

Como todos los prompts que uso cuando salto entre IAs que no tienen mucho contexto sobre mí (soy de ChatGPT, pero sin Codex no sirve para este proyecto), siempre suelo hacer cosas simples que sé que puedo corregir si lo hacen mal; en este caso solo debía validar que todo era correcto y mis explicaciones. Lo hizo sorprendentemente bien; un modelo de copiloto como Raptor Mini hubiera empezado a meterse a la terminal y escribir código y hacer quién sabe cuántas cosas para probar esto, y Antigravity solo entró, revisó y fue tachando en una checklist que me dio antes de empezar. Me gustó mucho su forma de trabajar.

## Entrada 1

### Objetivo

Probar Gemini, me dieron una prueba de 1 mes PRO. Tenía que tomar el rol de un SCRUM master y revisar qué tan bien redactadas están mis US; no le especifiqué bien qué metodologías usar (SP, Gherkin, MoSCoW) para ver qué tan inteligente era el modelo y ver si lo deducía por sí mismo.

### Prompt

> Actua como un SCRUM master. En este punto estoy por cursar la introduccion a FastAPI y SQLAlchemy en mi curso, es la semana 3, en la semana pasada aprendi a hacer User Stories y metolodologias agiles. Genere unos US, estos deben cumplir con los siguientes requisitos:
>
> • API completa de SensorHub en app/ (estructura oficial del repositorio): CRUD de sensores y lecturas siguiendo las convenciones REST.
> • Arquitectura en 4 capas limpiamente separadas: routers → services → repositories → models.
> • Validación Pydantic con física real: rechaza unidades desconocidas y valores fuera de rango por tipo de sensor.
> • Consulta con paginación y filtro por rango de fechas.
> • Swagger funcional en /docs.
> • Manejo de errores exhaustivo 400/404/409/422, decisiones de índices justificadas.
>
> Mis US son los siguientes, responde si cumplen con los requisitos de entrega, en caso de haber discrepancias o fallos arreglalos y explicame por que
>
> `[Aqui inserte el texto del .md de mis US]`

### Resultados

Tuve errores en 3 de los 6 US; me habló de detalles técnicos, de escritura, entendió la rúbrica (cabe recalcar que también le adjunté las 12 páginas del pdf) y también mencionó cosas que no se cumplían al 100%, ejemplo:

```text
1. Detalle Técnico en US-02: Error de escritura (typo) en la unidad
2. Ajuste Faltante para Alto Potencial en US-03
3. Ajuste Faltante para Alto Potencial en US-04
```

También entendió las metodologías usadas; como le pedí que arreglara el texto, generó los 6 US de nuevo, pero corregidos, y todos siguiendo SP, Gherkin, MoSCoW sin falla.

---

## Semana 2

## Entrada 4

### Objetivo

Recibir una explicación acerca de qué es un diagrama C4 nivel 2, específicamente, ¿por qué se llama así? ¿existen niveles mas altos? ¿mas bajos? ¿dónde se usa? ¿cómo se hace? Y generar un diagrama C4 nivel 2 para mi módulo madre device.py en base a una explicación, no al código.

### Prompt

> La ultima actividad que se me solicita en el curso es hacer un diagrama C4 nivel 2, la situacion es que no se que es JAJA.
>
> Explica que es, a que se debe su nombre, que otros tipos de diagramas (de la misma familia) existen, por que lo usaria como ingeniera y como hago uno (y en donde). Al final genera un ejemplo de diagrama C4 nivel 2 en base a este contexto:
>
> Mis modulos conforman un sistema de monitoreo IoT en una bodega. Su proposito es organizar todo el flujo de los datos recolectados por sensores, desde su simulacion hasta el printeo de alertas.
>
> Se divide en 6 modulos:
>
> 1. Modulo registry: Administra el catalogo de sensores en el sistema, SensorData y SensorType definen las propiedades del sensor (ID, ubicacion y tipo como TEMPERATURE o HUMIDITY), SensorRepository actua como almacenamiento central, SensorRegistry valida reglas de negocio para el alta de sensores (impide IDs vacios o duplicados), SensorLister permiten consultar info de los sensores, SensorDeleter da de baja sensores registrados.
> 2. Modulo reading: Almacena y gestiona el historial de lecturas del sistema, SensorReading define la estructura de la lectura (sensor_id, valor y timestamp), ReadingRecorder valida la existencia previa del sensor antes de guardar la lectura y ReadingHistory permite consultar el historial (total o filtrado por fechas).
> 3. Modulo anomaly: Evalua las lecturas para detectar valores fuera del limite, AnomalyType y ThresholdConfig definen los tipos de anomalia y límites maximos, ThresholdConfigManager administra la configuracion de umbrales por sensor (ID) y AnomalyDetector analiza la lectura frente a su configuración para emitir un AnomalyResult.
> 4. Modulo alert: Notifica las anomalias detectadas a diferentes formatos, Alert define una base abstracta, ConsoleAlert muestra los mensajes en terminal, FileAlert registra las alertas en un archivo (alerts.log) y AlertManager coordina todos los formatos para mandar las alertas al mismo tiempo.
> 5. Modulo gauss_distro: Genera lecturas simuladas para forzar el comportamiento de sensores, SensorSimulator utiliza una distribucion normal o gaussiana (basada en media y desviacion estandar) para simular datos.
> 6. Modulo device: Actúa como "modulo madre", PipelineModule acopla todos los modulos mediante inyeccion de dependencias, ejecutando todo: obtención de lecturas, almacenamiento, evaluacion de anomalias y emision de alertas.

### Resultados

Entendí que este diagrama nos ayuda a intentar mostrar todo el sistema en un solo mapa, un diagrama basado en 4 niveles de abstracción; el importante ahora es el nivel 2, una forma de demostrar a alto nivel todo el flujo técnico del sistema. Se genera en código (Mermaid y diferentes softwares) o se puede hacer en bloques, sabiendo acomodarlos. Después de la explicación creo un diagrama con los 6 módulos interconectados entre sí; a simple vista comunica lo que hace mi sistema; supongo que ese es el punto, entenderse fácilmente.

## Entrada 3

### Objetivo

Cómo ingresar la hora y fecha actual para timestamp.

### Prompt

> Necesito la hora actual para timestamp en el formato "YYYY-MM-DD HH:MM, como lo puedo agregar?

### Resultados

Me explicó la librería datetime, varios imports de ella y cómo funcionan; solo lo apliqué.

## Entrada 2

### Objetivo

Volver a valorar mis US, esta vez corregidos con las mismas preguntas y agregando revisar responsabilidades de cada US.

### Prompt

> Hice de nuevo los US (User Stories) eliminando los que no eran funcionalidades del sistema, participando en las sesiones con el ingeniero comente uno de mis US y me menciono que estaba juntando 2 modelos de negocio en un solo US, que estaba bien pero que podia mejorar si los dividia en versiones mas reducidas y precisas. Lo corregi, ahora revisa el texto buscando mas discrepancias de responsabilidad unica y de nuevo ¿es verificable? ¿es ambiguo? ¿qué caso borde falta?. Ademas al final, agrega un US mas (US-12) en el que el punto sea hacer un modulo madre para todos los modulos de los US, prioridad Wont have.
>
> `[Aqui pegue el texto de mi .md]`

### Resultados

Mucho mejor que la vez pasada; esta vez los cambios realizados fueron mínimos, más que todo de redundancia en algunos US. Por ejemplo, había gherkins que pedían probar la misma lógica en temperatura y en humedad; la IA eliminó la humedad, mencionando que es redundante y es mejor mantener las pruebas limpias. Supongo que por lo mismo de querer mantener un entorno limpio, cambió nombres de IDs por nombres más descriptivos; esto lo revertí. A mí personalmente me gusta mantener pocos nombres y cortos, más cuando es un código breve, como es el caso; así me confundo menos.

Para finalizar, sí creó el módulo madre que le pedí; sin embargo, este en un principio no usaba la parte de lectura y guardado de los datos leídos por el sensor (04 y 05). Cuando le pedí que agregara todos los módulos, lo terminé agregando manualmente (igual puede no usarse y por eso lo ignoro, pero eso lo veré en el proceso).

## Entrada 1

### Objetivo

Auditar mis US, verificar formatos y saber si son verificables, qué tan ambiguos son y qué casos borde faltan.

### Prompt

> La semana 2 en mi curso se basa en:
>
> - Aplicar Scrum completo: roles, eventos, artefactos y valores.
> - Escribir user stories profesionales con criterios de aceptación en Gherkin.
> - Practicar TDD estricto: el test siempre antes del código, sin excepción.
>
> Como actividad 2 se me pide hacer 10 user stories, no especifica bien de que, sin embargo hay un par de actividades mas en la semana que use para escribir los US, son estas:
>
> 1. Día 3 · Miércoles — TDD estricto ...
> 2. Día 4 · Jueves — Definition of Done y calidad automatizada ...
> 3. Día 5 · Viernes — EVALUACIÓN 1 ...
>
> *(Pegue las instrucciones completas, aqui lo substituyo por los 3 puntos)*
>
> Evalua mis US, se estricto con el Gherkin, mencioname ¿es verificable? ¿es ambiguo? ¿qué caso borde falta?
>
> `[Aqui pegue el texto de mi .md]`

### Resultados

Me explicó que comúnmente en US se redactan únicamente funcionalidades reales del sistema, no documentación, lo cual es un gran problema ya que 5 de mis 10 US se basan en documentación o tareas de proceso (como el .toml), por lo que debo de reescribir 5 US. Del lado de las que sí cumplen, todas las marcó como parcialmente verificables y ambiguas. No me generó un texto de referencia, pero sí me dejó los errores por cada US, ejemplo:

```text
¿Es verificable? Parcialmente. ¿Ambiguo? Sí.

Problemas:
• "registrado en el SensorRegistry": ¿cómo se registra? No hay un escenario de registro. Solo cubres consulta.
• "devuelve la instancia correspondiente": muy vago. ¿Qué atributos debe tener esa instancia? ¿ID, tipo, ubicación?
• SensorNotFoundError: bien que uses una excepción concreta, pero no especificas si es checked o runtime.
```

---

## Semana 1

## Entrada 9

### Objetivo

Mi archivo test_device.py, a pesar de tener una función de test para cada función de la clase UartDevice, marcaba error al commitear, en la prueba de cobertura exactamente. La IA debía solucionar eso dándome un banco de pruebas para device.py.

### Prompt

> Revisa el archivo `recorder.py` y `test_recorder.py`, me esta dando error en pytest-cov no se a que se debe si tengo una prueba para cada funcion de device. Realiza un pytest y pytest-cov para que verifiques que el coverage es bajo. Al final entregame en el archivo `test_recorder.py` un banco de test que cumpla con +90% de coverage y verificalo con los mismos comandos de pytest y pytest-cov.

### Resultados

Error mío, estaba probando las funciones de device, funciones que tienen herencias de config y parsers, sin importar al código las clases, por eso me tiraba error. Solo importó las funciones de config y parsers, creando @pytest.fixture (entornos de pruebas) y reinterpreto los test que tenía agregándole los entornos importados y dependencias necesarias.

## Entrada 8

### Objetivo

Explicar qué es NMEA, cómo funciona, qué parámetros pide y completar parsers.py.

### Prompt

> La ultima practica de la semana 1 de mi curso me pide implementar un driver UART modernizado usando 4 archivos: config, device, parsers y recorder. De estos cuento con config que es el siguiente codigo:
>
> `[Adjunte el codigo de config.py]`
>
> Y tengo iniciado el codigo de parsers, que es el siguiente:
>
> `[Adjunte el codigo de parsers.py]`
>
> Para parsers.py se me pide hacer MessageParser (ABC con parse() y can_parse())+ ModbusParser (frames RTU) + NMEAParser (sentencias $GPGGA) implementando SOLID como pilar fundamental de la estructura del codigo. El problema es que no se que es NMEA, hasta el momento hice 2 drivers UART, uno en LL y otro en Verilog, pero nunca en HAL, se comunicaban por ASCII.
> Explicame que es NMEA, como funciona por dentro (que parametros se necesitan, como se setean, cuales valores son incorrectos, hay reglas claras para NMEA?), evita usar terminos de bajo nivel, los entiendo muy bien pero quiero empezar a llevar mis conceptos a alto nivel.
>
> Al final entregame mi codigo de parsers.py con la implementacion de NMEA, no implementes MessageParser de ser posible (aunque es muy sencillo).

### Resultados

Usé este mismo prompt en Gemini y en DeepSeek, para comparar respuestas; como no sé qué es NMEA pensé que no podría fiarme de una sola respuesta. Los 2 me dieron respuestas prácticamente iguales, me explicaron todo lo solicitado, Gemini incluso me dejó fuentes NMEA 0183 (no sabía que era una especie de estándar) y generaron el código. Elegí el de DeepSeek ya que nunca me gustó Gemini para programación, pero a Gemini le escribí otro mensaje explicándole lo que entendí y un poco del código que generó para que validara si comprendí lo que me trató de decir (lo tengo configurado para que no siempre me dé la razón), teniendo éxito en un 70% de mi explicación y me volvió a explicar lo que tenía erróneo. Por el lado de DeepSeek, me entregó el código fuente con NMEA y 6 tests de los cuales elegí los 4 que me parecieron más compatibles con mi forma de escribir los test, de hecho 3 de ellos son muy similares a los que escribí para la primera versión del código.

## Entrada 7

### Objetivo

Aclarar dudas sobre qué hizo en las correcciones del prompt anterior.

### Prompt

> Lo que no termino de entender es:
> Si protocol es un intermediario entre el proceso a bajo nivel como el guardado o lectura y el de alto nivel que es toda la logica de como se mueven las cosas, por que en estos codigos tanto PostgreSQLRepository e InMemoryRepository no llaman nunca a la funcion de protocol.

### Resultados

Me explicó el concepto de "Duck Typing" y cómo básicamente no hay necesidad de llamar a las clases protocol en los módulos de bajo nivel si estos tienen los argumentos establecidos en la clase protocol, me dio el siguiente ejemplo:

```text
- El protocolo `DataRepository` dice que un almacén de datos debe tener los métodos save() y get_latest().

- La clase `PostgreSQLRepository` tiene los métodos save() y get_latest().*

Como la clase tiene exactamente los mismos métodos que pide el protocolo, Python y tu validador estático (Mypy)
dicen de forma automática: "Perfecto, esta clase es un DataRepository válido". No hace falta que la clase lo declare
o lo llame explícitamente.
```

Incluso al final me dio una analogía de hardware y de firmware, lo cual me sorprendió porque dedujo que lo entendería mejor así teniendo un muy breve contexto de mí.

## Entrada 6

### Objetivo

Validar la implementación de los principios SOLID (ISP, DIP) en la práctica y probar DeepSeek (web) para medir su desempeño y confirmar si debería pasarme a una IA local (Ollama con DeepSeek, que investigando es uno de los combos más potentes) o seguir en GitHub Copilot.

### Prompt

> Comportate como un ingeniero en software senior, experto en Python, especificamente en Programacion Orientada a Objetos (POO), plataformas de servidores API y contenedores. Estoy llevando un curso para orientar mis conocimientos de firmware embebido hacia la creación de software profesional.
>
> Se divide en 6 semanas, en este momento me encuentro en la primera de ellas. Esta etapa se centra en los siguientes objetivos:
>
> - Mapear conceptos de hardware/firmware a sus equivalentes de software de alto nivel.
> - Escribir Python idiomático: type hints, dataclasses, enums, protocolos — no “C con otra sintaxis”.
> - Aplicar los 5 principios SOLID con ejemplos del dominio de sensores.
>
> Actualmente me encuentro terminando la ultima practica de los fundamentos SOLID, especificamente practicas para ejecutar los principios ISP y DIP, me dieron el siguiente codigo de ejemplo:
>
> `[Adjunte el breve codigo de ejemplo de la guia]`
>
> Mi código funciona y los tests pasan (casi todos Green) con pytest, pero quiero revisar si los principio esta bien implementado y los test prueban todo, la practica solicita un codigo de el principio mal ejecutado y un codigo del principio bien ejectuado + 2 test por principio (yo lo voy llevando como test del incorrecto y test del correcto). Revisa los siguientes codigos:
>
> `[Aqui le adjunte el codigo de los 2 archivos, primero el fuente y luego el test]`
>
> Verifica si cumple.

### Resultados

Al ser la versión web del modelo no pude aceptar ni rechazar algo, sin embargo me dio una buena retroalimentación.
La sección ISP era correcta y completa, no hizo cambios allí; por otro lado, la sección DIP tuvo fuertes cambios: Primero parece ser que no logré entender del todo las clases InMemoryRepository y PostgreSQLRepository por lo que refactorizó las clases, no entendí del todo qué hizo y eso conllevó a la entrada 7 (esto fue un error mío en el prompt, se me olvidó por completo agregarle que hiciera un resumen explicando los cambios, quizás esta IA es más estricta con lo que se le pide y lo que entrega). También hizo las debidas correcciones en el test y había un test que corría al 96% y no logré leer el error en la terminal (porque no le entendía) y lo solucionó; de mi parte eliminé la sección en la que probaba PostgreSQLRepository y puse como comentario la clase debido a que en la guía pide explícitamente que se pruebe únicamente con InMemoryRepository.

## Entrada 3, 4 y 5

**Nota:** Anteriormente actualicé AI_LOG con este prompt únicamente como "Entrada 3", en ese momento solo tenía programados los 2 códigos de ejemplo de SRP y mandé el prompt enfocado solo en SRP. Conforme fui generando los demás ejemplos le solicité a la IA hacer exactamente lo mismo copiando y pegando el prompt, cambiando SRP por OCP, LSP y los parámetros que tiene que evaluar para que no se confundiera, por esto englobo este prompt como "Entrada 3, 4 y 5", asimismo para identificar dónde fueron los cambios entre Prompts, acomodaré las diferencias en listas.

### Objetivo

Validar la implementación de los principios SOLID (SRP, OCP, LSP) en la práctica.

### Prompt

> Desarrolle un ejemplo del principio
>
> 1. SRP (Single Responsability Principle)
> 2. OCP (Open-Closed Principle)
> 3. LSP (Liskov Substitution Principle)
>
> en los archivos `solid_srp_ocp_lsp.py` (codigo fuente) y `test_srp_ocp_lsp.py` (pruebas con Pytest). Actualmente el codigo funciona y los tests pasan (Green), pero quiero revisar si el principio esta bien implementado.
>
> Realiza una revision de codigo y verifica si cumple, en caso contrario, refactoriza ambos archivos enfocandote en el cumplimiento estricto de
>
> 1. SRP:
> 2. OCP:
> 3. LSP:
>
> Evalua si cada clase y funcion
>
> 1. tiene una unica razon para cambiar. Si detectas responsabilidades acopladas, separalas.
> 2. esta cerrada a la modificacion pero el codigo si es expandible. Si no cumple divide las clases y funciones.
> 3. no modifica el comportamiento de la clase madre.
>
> Tambien revisa la calidad de las Pruebas (Pytest), verifica que los tests sean limpios.
>
> Al final realiza un pytest -v para revisar que todo funcione correctamente y entregame un resumen de que estuvo bien, que estuvo mal, que cambiaste y por que.

### Resultados

La primera vez que generé esta entrada no tuve cuidado en ver qué estaba haciendo Copilot, y me generó un código lleno de errores y warnings, al final se freezeó y tuve que repetir la instrucción. En la segunda (SRP), tercera (OCP), cuarta (LSP) iteración estuve al pendiente de qué hacía y no cometió errores (salvo algunos comandos en la terminal sin sentido que quería hacer y no le permití). El código estaba bien estructurado, citando:

```text
En conclusión, el código original ya era muy bueno y funcional. La refactorización se centró en llevar la implementación
y, sobre todo, las pruebas a un nivel de cumplimiento más estricto y expresivo de los principios SOLID, eliminando cualquier
posible ambigüedad conceptual.
```

Corrigió un par de imprecisiones que tenía el código de test de LSP que hacía que no cumpliera con el 100% de coverage y cambios menores para no confundir clases.

## Entrada 2

### Objetivo

Generar configuraciones (archivos) para automatizar el proceso de verificación de calidad con Mypy, Ruff y Pytest, pidiéndole que verifique el correcto funcionamiento de dichos archivos usando una secuencia previamente establecida para reducir los errores al mínimo. Al ser dentro del mismo chat, a partir de este mensaje no se le establecerá un rol a menos que sea estrictamente necesario.

### Prompt

> En este repositorio requiero mantener un estándar de calidad extremadamente alto (Mypy, Ruff, Pytest con coverage cercano al 90%-100%). Investigando encontré que se puede automatizar la tarea de ejecutar los linters y test con "pre-commit".
>
> Necesito que me generes la configuración necesaria para automatizar este flujo de verificación de forma rápida y local antes de subir mi código.
>
> Genera la siguiente solucion:
>
> 1. Configuración de Git Hooks con la herramienta "pre-commit":
>
> - Genera el archivo de configuración `.pre-commit-config.yaml`.
> - Incluye los hooks para Ruff (tanto linter como formatter), Mypy y la ejecución de Pytest con el reporte de coverage.
>
> Al terminar, ejecuta el siguiente flujo en mi terminal para verificar que funcionen las configuraciones:
>
> 1. Crear un archivo temporal de prueba en Python (ej. 'test_sandbox.py').
> 2. Añadirlo al Staging Area ('git add test_sandbox.py').
> 3. Intentar realizar un commit local ('git commit -m "test: sandbox validation"') para forzar la ejecución de los hooks de pre-commit que validan el código (validar que funciona el .yaml).
> 4. Deshacer el commit inmediatamente después usando 'git reset HEAD~1' (o el comando adecuado) para mantener el historial de Git completamente limpio y revertir el archivo temporal.
> 5. Eliminar físicamente el archivo temporal 'test_sandbox.py'.
> 6. Genera en el chat un resumen claro que me diga explícitamente si el flujo fue EXITOSO o si FALLÓ (detallando qué linter o test detuvo el proceso).
>
> Restricciones:
>
> - Las herramientas deben leer sus configuraciones de los archivos estándar del proyecto (como pyproject.toml), no metas flags excesivas en el script si pueden ir en el archivo de configuración.
> - El comando de Pytest debe incluir los argumentos para fallar si el coverage baja de un umbral específico (por ejemplo, --cov-fail-under=90).
> - El script DEBE ser 100% local. Bajo ninguna circunstancia debe ejecutar 'git push'.
> - Debe manejar correctamente los códigos de salida (exit codes) para que, si el pre-commit falla en el paso 3, el script no se detenga abruptamente y pueda ejecutar correctamente los pasos de limpieza (reset y borrado del archivo temporal).
> - Dame las instrucciones claras de cómo instalar las herramientas y cómo ejecutar este flujo con un solo comando corto desde mi terminal.

### Resultados

Generó los archivos `.pre-commit-config.yaml` y `pyproject.toml`. En un principio generó una configuración extraña en el .yaml donde no respetaba su propio archivo .toml; tuve que rechazar varias veces los cambios, ya que en un punto quería modificar los archivos .py de las prácticas. Al final generó una configuración bastante profesional: Ruff es muy estricto y en Pytest debo superar el 90% en el coverage para que permita realizar un commit.

## Entrada 1

### Objetivo

Establecer el rol de la IA como experto para el chat usando CO-RE-CON (Contexto-Restricciones-Consigna) para escribir el prompt. Obtener una explicación profunda línea por línea de la sintaxis de Type Hints, omitiendo la lógica de programación y los principios SOLID por el momento. También solicitar la estructura base para el desarrollo de las 5 funciones puras asignadas.

### Prompt

> Actua como un profesor egresado de ingeniería en software o similares, experto en Python orientado a objetos y plataformas de servidores API y contenedores. Actualmente estoy en un curso para orientar mis conocimientos de firmware embebido hacia la creación de software profesional.
>
> Se divide en 6 semanas, en este momento me encuentro en la primera de ellas. Esta etapa se centra en los siguientes objetivos:
>
> - Mapear conceptos de hardware/firmware a sus equivalentes de software de alto nivel.
> - Escribir Python idiomático: type hints, dataclasses, enums, protocolos — no “C con otra sintaxis”.
> - Aplicar los 5 principios SOLID con ejemplos del dominio de sensores.
>
> Como primera actividad se me pide realizar 5 funciones puras de reading (conversión de unidades, detección de umbral, serializacion) con type hints y verificarlo con ruffs y mypy. Me dieron este codigo de ejemplo:
>
> `[Aqui pegue el codigo dado en la guia de estudios]`
>
> No seas vago o impreciso con tu explicación, alargate, me gustan las explicaciones completas, basate puramente en la documentacion oficial de python, por el momento no me expliques SOLID enfocate únicamente en type hints, no expliques la logica de programacion.  
>
> Explicame la sintaxis linea por linea, especialmente los type hints, que significa, donde se usa, por que me deberia importar para POO (Programacion orientada a objetos), API, IA. Por ultimo y siguiendo con el ejercicio, generame el "esqueleto" (los def con los argumentos vacíos) para que yo los rellene con la logica y los type hints.

### Resultados

La IA asumió el rol solicitado y proporcionó un desglose técnico enfocado en las Type Hints de Python, así como su relevancia en las áreas mencionadas. En el código, entregó la estructura inicial para las 5 funciones puras orientadas al procesamiento de lecturas de sensores, dejando un breve contexto como comentario.
