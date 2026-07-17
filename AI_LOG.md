# Registro de Uso de IA (AI Log)

Este documento registra las interacciones con Inteligencia Artificial generativa utilizadas como asistencia para el desarrollo de las actividades durante el curso.

**Nota:** En casi todos las entradas la IA comete errores menores que no explico, por ejemplo poner Dict en vez de dict, o usar Optional en vez de "|".

## Semana 1

## Entrada 9

### Objetivo

Mi archivo test_device.py a pesar de tener una funcion de test para cada funcion de la clase UartDevice marcaba error al commitear, en la prueba de covertura exactamente. La IA debia solucionar eso dandome un banco de pruebas para device.py

### Prompt

> Revisa el archivo `recorder.py` y `test_recorder.py`, me esta dando error en pytest-cov no se a que se debe si tengo una prueba para cada funcion de device. Realiza un pytest y pytest-cov para que verifiques que el coverage es bajo. Al final entregame en el archivo `test_recorder.py` un banco de test que cumpla con +90% de coverage y verificalo con los mismos comandos de pytest y pytest-cov.

### Resultados

Error mio, estaba probando las funciones de device, funciones que tienen herencias de config y parsers, sin importar al codigo las clases, por eso me tiraba error. Solo importo las funciones de config y parsers, creando @pytest.fixure (entornos de pruebas) y reinterpreto los test que tenia agregandole los entornos importados y dependencias necesarias.

## Entrada 8

### Objetivo

Explicar que es NMEA, como funciona, que parametros pide y completar parsers.py

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

Use este mismo prompt en Gemini y en Deepseek, para comparar respuestas, como no se que es NMEA pense que no podria fiarme de una sola respuesta. Los 2 me dieron respuestas practicamente iguales, me explicaron todo lo solicitado, Gemini incluso me dejo fuentes NMEA 0183 (no sabia que era una especie de estandar) y generaron el codigo, elegi el de Deepseek ya que nunca me gusto Gemini para programacion, pero a Gemini le escribi otro mensaje explicandole lo que entendi y un poco del codigo que genero para que validara si comprendi lo que me trato de decir (lo tengo configurado para que no siempre me de la razon), teniendo exito en un 70% de mi explicacion y me volvio a explicar lo que tenia erroneo. Por el lado de Deepseek me entrego el codigo fuente con NMEA y 6 tests de los cuales elegi los 4 que me parecieron mas compatibles con mi forma de escribir los test, de hecho 3 de ellos son muy similares a los que escribi para la primera version del codigo.

## Entrada 7

### Objetivo

Aclarar dudas sobre que hizo en las correcciones del prompt anterior.

### Prompt

> "Lo que no termino de entender es:
> Si protocol es un intermediario entre el proceso a bajo nivel como el guardado o lectura y el de alto nivel que es toda la logica de como se mueven las cosas, por que en estos codigos tanto PostgreSQLRepository e InMemoryRepository no llaman nunca a la funcion de protocol."

### Resultados

Me explico el concepto de "Duck Typing" y como basicamente no hay necesidad de llamar a las clases protocol a los modulos de bajo nivel si estos tiene los argumentos establecidos en la clase protocol, me dio el siguiente ejemplo:
<br>
*"- El protocolo `DataRepository` dice que un almacén de datos debe tener los métodos save() y get_latest().*
<br>
*- La clase `PostgreSQLRepository` tiene los métodos save() y get_latest().*
<br>
*Como la clase tiene exactamente los mismos métodos que pide el protocolo, Python y tu validador estático (Mypy) dicen de forma automática: "Perfecto, esta clase es un DataRepository válido". No hace falta que la clase lo declare o lo llame explícitamente"*
<br>
Incluso al final me dio una analogia de hardware y de firmware, lo cual me sorprendio por que dedujo que lo entenderia mejor asi teniendo muy breve contexto de mi.

## Entrada 6

### Objetivo

Validar la implementacion de los principios SOLID (ISP, DIP) en la practica y probar DeepSeek (web) para medir su desempeño y confirmar si deberia pasarme a una IA local (Ollama con DeepSeek, que investigando es uno de los combos mas potentes) o seguir en Github Copilot.

### Prompt

> "Comportate como un ingeniero en software senior, experto en Python, especificamente en Programacion Orientada a Objetos (POO), plataformas de servidores API y contenedores. Estoy llevando un curso para orientar mis conocimientos de firmware embebido hacia la creación de software profesional.
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

Al ser la version web del modelo no pude aceptar ni rechazar algo, sin embargo me dio una buena retroalimentacion.
La seccion ISP era correcta y completa, no hizo cambios alli, por otro lado la seccion DIP tuvo fuertes cambios: Primero parece ser que no logre entender del todo las clases InMemoryRepository y PostgreSQLRepository por lo que refactorizo las clases, no entendi del todo que hizo y eso conllevo a la entrada 7 (esto fue un error mio en el prompt, se me olvido por completo agregarle que hiciera un resumen explicando los cambios, quizas esta IA es mas estricta con lo que se le pide y lo que entrega). Tambien hizo las debidas correcciones en el test y habia un test que corria al 96% y no logre leer el error en la terminal (por que no le entendia) y lo soluciono, de mi parte elimine la seccion en la que probaba PostgreSQLRepository y puse como comentario la clase debido a que en la guia pide explicitamente que se pruebe unicamente con InMemoryRepository.

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

La primera vez que generé esta entrada no tuve cuidado en ver qué estaba haciendo Copilot, y me generó un código lleno de errores y warnings, al final se freezeó y tuve que repetir la instrucción. En la segunda (SRP), tercera (OCP), cuarta (LSP) iteración estuve al pendiente de qué hacía y no cometió errores (salvo algunos comandos en la terminal sin sentido que quería hacer y no le permití). El código estaba bien estructurado, citando *"En conclusión, el código original ya era muy bueno y funcional. La refactorización se centró en llevar la implementación y, sobre todo, las pruebas a un nivel de cumplimiento más estricto y expresivo de los principios SOLID, eliminando cualquier posible ambigüedad conceptual"*. Corrigió un par de imprecisiones que tenía el código de test de LSP que hacía que no cumpliera con el 100% de coverage y cambios menores para no confundir clases.

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

Generó los archivos `.pre-commit-config.yaml` y `pyproject.toml.` En un principio generó una configuración extraña en el .yaml donde no respetaba su propio archivo .toml; tuve que rechazar varias veces los cambios, ya que en un punto quería modificar los archivos .py de las prácticas. Al final generó una configuración bastante profesional: Ruff es muy estricto y en Pytest debo superar el 90% en el coverage para que permita realizar un commit.

## Entrada 1

### Objetivo

Establecer el rol de la IA como experto para el chat usando CO-RE-CON (Contexto-Restricciones-Consigna) para escribir el prompt. Obtener una explicación profunda línea por línea de la sintaxis de Type Hints, omitiendo la lógica de programación y los principios SOLID por el momento. También solicitar la estructura base para el desarrollo de las 5 funciones puras asignadas.

### Prompt

> "Actua como un profesor egresado de ingeniería en software o similares, experto en Python orientado a objetos y plataformas de servidores API y contenedores. Actualmente estoy en un curso para orientar mis conocimientos de firmware embebido hacia la creación de software profesional.
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
> Explicame la sintaxis linea por linea, especialmente los type hints, que significa, donde se usa, por que me deberia importar para POO (Programacion orientada a objetos), API, IA. Por ultimo y siguiendo con el ejercicio, generame el "esqueleto" (los def con los argumentos vacíos) para que yo los rellene con la logica y los type hints."

### Resultados

La IA asumió el rol solicitado y proporcionó un desglose técnico enfocado en las Type Hints de Python, así como su relevancia en las áreas mencionadas. En el código, entregó la estructura inicial para las 5 funciones puras orientadas al procesamiento de lecturas de sensores, dejando un breve contexto como comentario.
