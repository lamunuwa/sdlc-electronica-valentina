# Registro de Uso de IA (AI Log)

Este documento registra las interacciones con Inteligencia Artificial generativa utilizadas como asistencia para el desarrollo de las actividades durante el curso.

## Semana 1

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
