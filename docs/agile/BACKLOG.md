# Registro de User Stories

Este documento organiza el trabajo pendiente siguiendo los principios de SCRUM. Cada US está diseñada bajo BDD con Gherkin, priorización MoSCoW y estimación por Story Points, manteniendo cada historia enfocada, pequeña y alcanzable.

---

## Sprint 3

## US-01: Umbrales configurables por sensor

**Prioridad:** Must Have  
**Dificultad:** 2 Story Points

**As** desarrolladora de la plataforma, **I want to** que el registro y la actualización de un `sensor` acepte un `sensor_umbral` en el payload, **So that** cada sensor pueda disponer de un umbral configurable por dispositivo incorporado al modelo del sensor.

```gherkin
Scenario: Registrar sensor con umbral
  Given envío {"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C", "sensor_umbral": {"max": 35.0, "min": -40.0}} 
  When hago POST /sensors
  Then recibo 201 "Created"

Scenario: Actualizar umbral mediante PUT
  Given un sensor existente con umbral
  When hago PUT /sensors/{id} con {"sensor_umbral": {"max": 30.0}}
  Then recibo 200 "OK"

Scenario: Registrar sensor sin umbral
  Given envío {"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C", "sensor_umbral": {"max": "", "min": ""}} 
  When hago POST /sensors
  Then recibo 400 "Bad Request"

Scenario: Validación de umbral inválido en registro
  When intento registrar un sensor con {"sensor_umbral": {"max": "alto"}}
  Then recibo 422 "Unprocessable Entity"
  And un mensaje de validación indicando tipo numérico requerido

Scenario: Validación de umbral inválido en actualización
  When intento actualizar un sensor con {"sensor_umbral": {"max": "alto"}}
  Then recibo 422 "Unprocessable Entity"
  And un mensaje de validación indicando tipo numérico requerido
```

## US-02: Detección de anomalías al recibir lecturas

**Prioridad:** Must Have  
**Dificultad:** 3 Story Points

**As** operadora del sistema, **I want to** que al registrar una lectura del sensor el sistema compare el valor contra el `sensor_umbral` y genere una `alerta` si se supera, **So that** las anomalías se detecten en el punto de ingestión y queden registradas.

```gherkin
Scenario: Lectura que supera umbral genera alerta
  Given un sensor con sensor_umbral.max = 35.0
  When envío POST /sensors/{id}/readings con {"value": 36.5, "unit": "C"}
  Then recibo 201 "Created"
  And se persiste una alerta asociada al sensor con tipo HIGH_TEMPERATURE y value 36.5

Scenario: Lectura dentro de umbral no genera alerta
  Given un sensor con sensor_umbral.max = 35.0
  When envío POST /sensors/{id}/readings con {"value": 22.0, "unit": "C"}
  Then recibo 201 "Created"

Scenario: Lectura que supera umbral fisico genera alerta
  Given un sensor con sensor_umbral.min = -500.0
  When envío POST /sensors/{id}/readings con {"value": -500.0, "unit": "C"}
  Then recibo 201 "Created"
  And se persiste una alerta asociada al sensor con tipo INVALID_TEMPERATURE y value -500.0

Scenario: Alerta incluye metadatos para auditoría
  Given se genera una alerta por lectura
  Then la alerta contiene: id, sensor_id, type, value, unit, timestamp, reading_id
```

## US-03: Gestión de alertas consultables

**Prioridad:** Must Have  
**Dificultad:** 2 Story Points

**As** analista de operaciones, **I want to** consultar las `alerta` generadas a través de un endpoint de solo lectura, **So that** pueda revisar eventos anómalos sin posibilidad de crear, modificar o borrar alertas vía API.

```gherkin
Scenario: Listar alertas de un sensor
  Given existen varias alertas asociadas a un sensor
  When hago GET /alerts?sensor_id={id}&limit=10&offset=0
  Then recibo 200 "OK"
  And la respuesta contiene una lista de alerta ordenadas por timestamp descendente

Scenario: Obtener alerta por id
  Given existe una alerta con id 1
  When hago GET /alerts/1
  Then recibo 200 "OK"
  And el cuerpo contiene los campos id, sensor_id, type, value, unit, timestamp, reading_id

Scenario: Filtrado por rango de fechas
  Given existen alertas en un sensor en diferentes fechas
  When hago GET /alerts?from=2026-07-01T00:00:00&to=2026-07-31T23:59:59
  Then recibo 200 "OK"
  And solo las salertas dentro del rango
```

---

## Sprint 2

## US-01: Inicialización de la API base

**Prioridad:** Must Have <br>
**Dificultad:** 1 Story Points

**As** cliente de la API, **I want to** consultar el estado de el servicio, **So that** verificar si el servicio está en ejecución y operativo.

```gherkin
Scenario: Verificar el estado del servicio
  Given el servicio SensorHub está activo en la raíz del repositorio
  When envío una solicitud GET a '/health'
  Then recibo una respuesta HTTP con código de estado 200
  And el cuerpo de la respuesta contiene '{"status": "ok"}'
```

## US-02: Registro de sensores

**Prioridad:** Must Have <br>
**Dificultad:** 2 Story Points

**As** administradora, **I want to** dar altas de sensores con `name`, `type`, `unit`, **So that** incorporarlos al sistema antes de recibir lecturas.

```gherkin
Scenario: Registro exitoso
  Given envío {"name": "TEMP-01", "type": "TEMPERATURE", "unit": "C"}
  When hago POST /sensors
  Then recibo 201 "Created"
  And el sensor creado y su ID

Scenario: Nombre duplicado
  Given ya existe un sensor con el mismo nombre
  When envío POST /sensors con ese nombre
  Then recibo 409 "Conflict"

Scenario: Payload inválido (tipo de dato incorrecto o falta campo obligatorio)
  When envío un JSON incorrecto o con campos erróneos
  Then recibo 422 "Unprocessable Entity"
```

## US-03A: Consultar, actualizar y desactivar sensores

**Prioridad:** Must Have <br>
**Dificultad:** 3 Story Points

**As** desarrolladora de la plataforma, **I want to** listar todos los sensores por id, modificarlo parcialmente (PATCH) y desactivarlo, **So that** mantener el catalogo actualizado sin perder historial.

```gherkin
Scenario: Listar sensores
  Given que existen sensores registrados
  When hago GET /sensors
  Then recibo 200 "OK" 
  And la lista completa

Scenario: Actualizacion tipo PATCH
  Given un sensor existente
  When hago PATCH /sensors/{id} con {"unit": "F"}
  Then recibo 200 "OK" 
  And los datos actualizados

Scenario: Desactivar sensor
  Given un sensor existente
  When hago DELETE /sensors/{id}
  Then recibo 204 "No Content"
  And el sensor queda con active=false
```

## US-03B: Gestion de errores

**Prioridad:** Must Have <br>
**Dificultad:** 2 Story Points

**As** usuario de la API, **I want to** recibir mensajes de error claros, **When** intento una petición incorrecta, **So that** corregir mis solicitudes.

```gherkin
Scenario: Obtener sensor por ID inexistente
  When hago GET /sensors/9999
  Then recibo 404 "Not Found"

Scenario: Error al actualizar sensor inexistente
  When hago PATCH /sensors/9999 con {"unit": "F"}
  Then recibo 404 "Not Found" 
  And un mensaje "Sensor con id 9999 no encontrado."

Scenario: Error por nombre duplicado al actualizar
  Given existen sensores "TEMP-01" y "TEMP-02"
  When hago PATCH /sensors/{id_TEMP-01} con {"name": "TEMP-02"}
  Then recibo 409 "Conflict" 
  And un mensaje de nombre duplicado

Scenario: Error al desactivar sensor inexistente
  When hago DELETE /sensors/9999
  Then recibo 404 "Not Found"
```

## US-04: Registrar lectura con validación de unidades y rangos físicos

**Prioridad:** Must Have <br>
**Dificultad:** 5 Story Points

**As** desarrolladora de la plataforma, **I want to** enviar una lectura a POST /sensors/{id}/readings, **So that** que se almacene solo si la unidad es compatible con el tipo de sensor y el valor respeta límites reales.

```gherkin
Scenario: Lectura válida
  Given un sensor de tipo "TEMPERATURE"
  When envío {"value": 24.5, "unit": "C"} a /sensors/{id}/readings
  Then recibo 201 "Created" 
  And el id de la lectura y timestamp

Scenario: Sensor no encontrado
  When envío una lectura a /sensors/9999/readings
  Then recibo 404 "Not Found"

Scenario: Unidad no soportada para el tipo
  Given un sensor de temperatura
  When envío {"value": 20, "unit": "PSI"}
  Then recibo 422 "Unprocessable Entity"

Scenario: Valor fuera del rango físico
  Given un sensor de temperatura
  When envío {"value": -345.67, "unit": "C"} (por debajo de -273.15 °C)
  Then recibo 400 "Bad Request"

Scenario: Intento de registrar lectura duplicada en el mismo timestamp
  Given una lectura ya procesada con el mismo hash/timestamp
  When reenvío la misma lectura a /sensors/{id}/readings
  Then recibo 409 "Conflict"
```

## US-05: Consultar lecturas paginadas y filtradas por fecha

**Prioridad:** Must Have <br>
**Dificultad:** 5 Story Points

**As** analista de datos, **I want to** quiero consultar las lecturas de un sensor, **So that** obtener un subconjunto de datos sin saturar la red.

```gherkin
Scenario: Paginación y filtro por fechas
  Given 100 lecturas para el sensor en julio 2026
  When hago GET /sensors/{id}/readings?from=2026-07-01T00:00:00&to=2026-07-27T00:00:00&limit=10&offset=0
  Then recibo 200 "OK" 
  And exactamente las primeras 10 lecturas dentro del rango

Scenario: Índices justificados
  Given `readings` (tabla) tiene un índice compuesto (sensor_id, created_at)
  When se realiza la consulta con filtro por sensor y rango de fechas
  Then el plan de ejecución usa el índice, garantizando rendimiento

Scenario: Sensor no encontrado
  When consulto lecturas de un sensor inexistente
  Entonces recibo 404 "Not Found"

Scenario: Validación de parámetros de consulta
  When envío "limit" con un valor no numérico
  Entonces recibo 422 "Unprocessable Entity"
```

## US-06: Swagger

**Prioridad:** Must Have <br>
**Dificultad:** 2 Story Points

**As** code reviewer, **I want to** una Swagger UI en /docs, **So that** validar el comportamiento del sistema.

```gherkin
Scenario: Swagger funcional
  Given la API está corriendo
  When visito /docs
  Then veo Swagger UI
  And todos los endpoints y esquemas
```

---

## Sprint 1

## US-01: Altas y bajas de sensores

**Prioridad:** Must Have <br>
**Dificultad:** 2 Story Points

**As** encargada del monitoreo de la planta, **I want to** registrar y dar de baja sensores en el sistema, **So that** solo los dispositivos autorizados puedan enviar lecturas.

```gherkin
Scenario: Registrar un sensor nuevo
  Given el SensorRegistry está vacío
  When registro un sensor con ID "TEMP-01", tipo TEMPERATURE y ubicación "Bodega A"
  Then el sensor "TEMP-01" queda almacenado en el SensorRegistry
  And el sensor tiene ID "TEMP-01"
  And el sensor tiene tipo TEMPERATURE
  And el sensor tiene ubicación "Bodega A"

Scenario: Rechazar registro de sensor con ID vacío
  Given el SensorRegistry está vacío
  When intento registrar un sensor sin ID, tipo TEMPERATURE y ubicación "Bodega A"
  Then el sistema lanza la excepción InvalidSensorDataError
  And el mensaje indica "ID no puede estar vacío"

Scenario: Rechazar registro de sensor con ID duplicado
  Given el sensor con ID "TEMP-01" ya está registrado en el SensorRegistry
  When intento registrar otro sensor con ID "TEMP-01", tipo TEMPERATURE en cualquier ubicación
  Then el sistema lanza la excepción SensorAlreadyExistsError
  And el mensaje indica "ID existente"

Scenario: Dar de baja un sensor existente
  Given el sensor con ID "TEMP-01" está registrado en el SensorRegistry
  When doy de baja el sensor "TEMP-01"
  Then el sensor "TEMP-01" deja de existir
```

## US-02: Consultar un sensor específico

**Prioridad:** Must Have <br>
**Dificultad:** 1 Story Points

**As** encargada del monitoreo de la planta, **I want to** consultar los datos de un sensor específico por su ID, **So that** pueda verificar su configuración o estado actual.

```gherkin
Scenario: Consultar un sensor existente
  Given el sensor con ID "TEMP-01" está registrado en el SensorRegistry
  When solicito el sensor con ID "TEMP-01"
  Then el sistema devuelve un sensor con ID "TEMP-01"
  And el sensor tiene tipo TEMPERATURE
  And el sensor esta en "Bodega A"

Scenario: Consultar un sensor inexistente
  Given ningún sensor con ID "GHOST-99" existe en el SensorRegistry
  When solicito el sensor con ID "GHOST-99"
  Then el sistema lanza la excepción SensorNotFoundError
```

## US-03: Listar sensores registrados

**Prioridad:** Must Have <br>
**Dificultad:** 1 Story Points

**As** encargada del monitoreo de la planta, **I want to** obtener un listado completo de todos los sensores registrados, **So that** pueda tener una visión general del sistema de monitoreo.

```gherkin
Scenario: Listar todos los sensores registrados
  Given el sensor "TEMP-01" y el sensor "TEMP-02" están registrados en el SensorRegistry
  When solicito la lista de todos los sensores
  Then el sistema devuelve una lista con 2 sensores
  And la lista contiene un sensor con ID "TEMP-01"
  And la lista contiene un sensor con ID "TEMP-02"

Scenario: Listar cuando no hay sensores registrados
  Given el SensorRegistry está vacío
  When solicito la lista de todos los sensores
  Then el sistema devuelve una lista vacía
```

## US-04: Registrar lectura de sensor

**Prioridad:** Must Have <br>
**Dificultad:** 3 Story Points

**As** operadora de planta, **I want to** registrar la lectura de un sensor con su timestamp, **So that** pueda mantener un historial consultable de las mediciones.

```gherkin
Scenario: Registrar lectura válida de sensor existente
  Given el sensor con ID "TEMP-01" está registrado en el SensorRegistry
  And la lectura tiene temperatura 22.5 °C
  When registro la lectura para el sensor "TEMP-01" con timestamp
  Then la lectura queda almacenada en el sistema
  And la lectura tiene ID "TEMP-01"
  And la lectura tiene temperatura 22.5
  And la lectura tiene timestamp

Scenario: Rechazar lectura de sensor no registrado
  Given ningún sensor con ID "GHOST-99" existe en el SensorRegistry
  When intento registrar una lectura para el sensor "GHOST-99"
  Then el sistema lanza la excepción SensorNotFoundError

Scenario: Rechazar lectura sin timestamp
  Given el sensor "TEMP-01" está registrado
  When intento registrar una lectura sin timestamp
  Then el sistema lanza la excepción InvalidReadingError
  And el mensaje indica "Timestamp requerido"

Scenario: Registrar lecturas de múltiples sensores
  Given el sensor "TEMP-01" y el sensor "TEMP-02" están registrados
  When registro lectura para "TEMP-01" con temperatura 22.5 °C
  And registro lectura para "TEMP-02" con temperatura 19.0 °C
  Then ambas lecturas quedan almacenadas
  And cada lectura tiene su ID correspondiente
```

## US-05: Consultar historial de lecturas

**Prioridad:** Should Have <br>
**Dificultad:** 3 Story Points

**As** operadora de planta, **I want to** consultar el historial de lecturas de un sensor específico, **So that** pueda analizar la evolución de las mediciones.

```gherkin
Scenario: Consultar historial de lecturas de un sensor
  Given el sensor "TEMP-01" tiene 3 lecturas registradas
  And las lecturas tienen sus timestamps
  When consulto el historial del sensor "TEMP-01"
  Then el sistema devuelve 3 lecturas
  And las lecturas están ordenadas por timestamp ascendente
  And cada lectura contiene ID, temperatura y timestamp

Scenario: Consultar historial con filtro de fechas
  Given el sensor "TEMP-01" tiene lecturas desde 2026-07-19 hasta 2026-07-21
  When consulto el historial del sensor "TEMP-01" entre las fechas
  Then el sistema devuelve solo las lecturas del día 2026-07-20

Scenario: Consultar historial de sensor sin lecturas
  Given el sensor "TEMP-01" está registrado pero no tiene lecturas
  When consulto el historial del sensor "TEMP-01"
  Then el sistema devuelve una lista vacía

Scenario: Consultar historial de sensor inexistente
  Given ningún sensor "GHOST-99" existe
  When consulto el historial del sensor "GHOST-99"
  Then el sistema lanza la excepción SensorNotFoundError
```

## US-06: Detección de Anomalías

**Prioridad:** Must Have <br>
**Dificultad:** 2 Story Points

**As** supervisora de calidad de la planta, **I want to** evaluar las lecturas contra umbrales definidos ($T>35.0 °C$), **So that** detectar a tiempo situaciones de peligro que puedan dañar la mercancía de la bodega.

```gherkin
Scenario: Detectar anomalía por alta temperatura
  Given un AnomalyDetector configurado con umbral máximo de temperatura 35.0 °C
  And una lectura del sensor "TEMP-01" con temperatura 36.5
  When el detector evalúa la lectura
  Then el resultado indica que hay anomalía
  And la anomalía es de tipo HIGH_TEMPERATURE
  And la anomalía contiene el ID del sensor "TEMP-01"
  And la anomalía contiene el valor de temperatura 36.5

Scenario: Normalidad dentro de umbrales
  Given un AnomalyDetector configurado con umbral máximo de temperatura 35.0 °C
  And una lectura del sensor "TEMP-01" con temperatura 22.0
  When el detector evalúa la lectura
  Then el resultado indica que no hay anomalía

Scenario: Valor exactamente en el umbral no se considera anomalía
  Given un AnomalyDetector configurado con umbral máximo de temperatura 35.0 °C
  And una lectura del sensor "TEMP-01" con temperatura 35.0
  When el detector evalúa la lectura
  Then el resultado indica que no hay anomalía
```

## US-07: Configuración de umbrales por tipo de sensor

**Prioridad:** Must Have <br>
**Dificultad:** 1 Story Points

**As** supervisora de calidad, **I want to** poder configurar umbrales diferentes para diferentes sensores, **So that** pueda adaptar la detección a los requisitos de la bodega.

```gherkin
Scenario: Configurar umbrales para tipo de sensor específico
  Given un sistema de monitoreo sin umbrales dinámicos
  When configuro un umbral máximo de 15.0 cm para un sensor "ULTRASONIC-01"
  Then el sistema almacena la regla de umbral para "ULTRASONIC-01"
  And el umbral límite configurado es 15.0 cm

Scenario: Detectar anomalía usando umbrales específicos del tipo de sensor
  Given el umbral configurado para "ULTRASONIC-01" es 15.0 cm
  And una lectura del sensor "ULTRASONIC-01" con valor de distancia 18.1 cm
  When el detector evalúa la lectura
  Then se detecta la anomalía de tipo TOO_FAR
```

## US-08: Canal de alertas en consola

**Prioridad:** Must Have <br>
**Dificultad:** 1 Story Points

**As** responsable de mantenimiento, **I want to** ver las anomalías en la consola en tiempo real, **So that** pueda reaccionar inmediatamente a situaciones críticas.

```gherkin
Scenario: Mostrar anomalía en consola
  Given un ConsoleAlert configurado
  And se ha detectado una anomalía HIGH_TEMPERATURE para sensor "TEMP-01" con valor 38.0
  When el ConsoleAlert procesa la anomalía
  Then imprime en consola el mensaje "ALERTA: Sensor TEMP-01, HIGH_TEMPERATURE, 38.0°C"
```

## US-09: Canal de alertas en archivo

**Prioridad:** Must Have <br>
**Dificultad:** 2 Story Points

**As** responsable de mantenimiento, **I want to** que todas las anomalías se registren en un archivo de log, **So that** tenga un historial de las anomalías que se han detectado.

```gherkin
Scenario: Registrar anomalía en archivo
  Given un FileAlert configurado con ruta "alerts.log"
  And se ha detectado una anomalía HIGH_TEMPERATURE para sensor "TEMP-01" con valor 38.0
  When el FileAlert procesa la anomalía
  Then el archivo "alerts.log" contiene una línea con "TEMP-01", "HIGH_TEMPERATURE", "38.0"

Scenario: Archivo acumula entradas sin sobrescribir
  Given el archivo "alerts.log" ya contiene 5 líneas
  When se registra una nueva anomalía
  Then el archivo contiene 6 líneas
```

## US-10: Gestor de alertas

**Prioridad:** Must Have <br>
**Dificultad:** 2 Story Points

**As** responsable de mantenimiento, **I want to** un gestor que envíe las anomalías a todos los canales configurados, **So that** garantice que la notificación llegue por todos los medios.

```gherkin
Scenario: Enviar anomalía a todos los canales
  Given un AlertManager configurado con ConsoleAlert y FileAlert
  And se ha detectado una anomalía HIGH_TEMPERATURE para sensor "TEMP-01" con valor 38.0
  When el AlertManager procesa la anomalía
  Then el ConsoleAlert recibe la anomalía
  And el FileAlert recibe la anomalía

Scenario: AlertManager funciona sin canales configurados
  Given un AlertManager sin canales configurados
  And se ha detectado una anomalía
  When el AlertManager procesa la anomalía
  Then no se produce ningún error
  And la anomalía se ignora silenciosamente
```

## US-11: SensorSimulator con distribución gaussiana

**Prioridad:** Should Have <br>
**Dificultad:** 3 Story Points

**As** ingeniera del sistema IoT, **I want to** un simulador de 10 sensores que genere mediciones con distribución gaussiana cada 30 segundos, **So that** recrear las condiciones reales de la bodega sin depender de hardware.

```gherkin
Scenario: Generar lecturas periódicas para sensores
  Given un SensorSimulator configurado con 10 sensores de temperatura
  And cada sensor cuenta con una media y desviación estándar de temperatura definidas
  When ejecuto 60 ciclos de simulación con intervalo de 30 segundos
  Then el simulador genera exactamente 600 lecturas
  And cada lectura contiene un ID del conjunto de sensores configurados
  And cada lectura contiene un valor de temperatura
  And cada lectura incluye un timestamp válido

Scenario: Rechazar configuración con ciclos negativos
  Given un SensorSimulator configurado con x sensores
  When intento ejecutar -5 ciclos de simulación
  Then el sistema lanza la excepción InvalidCycleCountError
```

## US-12: Pipeline centralizado de monitoreo

**Prioridad:** Won't Have <br>
**Dificultad:** 5 Story Points

**As** ingeniera del sistema IoT, **I want to** integrar todos los módulos anteriores en una pipeline (Simulación → Registro → Detección → Alertas), **So that** se ejecute la solución integral de extremo a extremo de forma coherente y auditable.

```gherkin
Scenario: Ejecutar ciclo completo guardando lectura sin anomalías
  Given un PipelineModule orquestado con:
    | Componente      | Configuración                              |
    | SensorRegistry  | Sensor registrado "TEMP-01"                |
    | SensorSimulator | Sensor "TEMP-01", temp_media=22.0 °C       |
    | ReadingStorage  | Almacenamiento de lecturas vacío           |
    | AnomalyDetector | Umbral máximo de temperatura = 35.0 °C     |
    | AlertManager    | Configurado con ConsoleAlert y FileAlert   |
  When el pipeline ejecuta 1 ciclo de monitoreo
  Then el pipeline almacena 1 lectura en el ReadingStorage para "TEMP-01"
  And el AnomalyDetector evalúa la lectura almacenada y confirma que no existe anomalía
  And el AlertManager no emite ninguna alerta

Scenario: Ejecutar ciclo completo guardando lectura anómala que dispara alerta
  Given un PipelineModule orquestado con:
    | Componente      | Configuración                              |
    | SensorRegistry  | Sensor registrado "TEMP-01"                |
    | SensorSimulator | Sensor "TEMP-01", temp_anómala=38.0 °C     |
    | ReadingStorage  | Almacenamiento de lecturas vacío           |
    | AnomalyDetector | Umbral máximo de temperatura = 35.0 °C     |
    | AlertManager    | Configurado con ConsoleAlert y FileAlert   |
  When el pipeline ejecuta 1 ciclo de monitoreo
  Then el pipeline almacena 1 lectura en el ReadingStorage para "TEMP-01"
  And el AnomalyDetector detecta 1 anomalía de tipo HIGH_TEMPERATURE
  And la anomalía contiene sensor_id "TEMP-01" y valor 38.0 °C
  And el AlertManager notifica exactamente 1 alerta a los canales
  And el archivo de salida "alerts.log" refleja la nueva entrada

Scenario: Simulación de carga distribuida E2E (10 sensores / 60 ciclos)
  Given un PipelineModule orquestado with:
    | Componente      | Configuración                              |
    | SensorRegistry  | 10 sensores registrados ("TEMP-01"..."TEMP-10") |
    | SensorSimulator | 10 sensores (temp_media=22.0 °C, std=5.0 °C)  |
    | ReadingStorage  | Almacenamiento de lecturas vacío           |
    | AnomalyDetector | Umbral máximo de temperatura = 35.0 °C     |
    | AlertManager    | Configurado con FileAlert ("alerts.log")   |
  When el pipeline ejecuta 60 ciclos de monitoreo
  Then el ReadingStorage acumula exactamente 600 lecturas persistidas
  And el archivo "alerts.log" se crea o actualiza en disco
  And el número de registros "alerts.log" es exactamente igual al número de anomalías detectadas
```