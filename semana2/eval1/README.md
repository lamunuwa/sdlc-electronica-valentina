# Funcionamiento del sistema IoT

El sistema es un pipeline de monitoreo y detección de anomalías en una bodega. La idea es organizar todo el flujo de los datos recolectados por sensores (por ejemplo, sensores de temperatura, humedad, proximidad): desde su simulación hasta el printeo de alertas.

El diseño sigue una arquitectura donde todos los módulos son independientes y son orquestados por la clase madre PipelineModule.

## Módulos

1. **Módulo `registry`:** Administra el catalogo de sensores en el sistema; SensorData y SensorType definen las propiedades del sensor (ID, ubicación y tipo como TEMPERATURE o HUMIDITY), SensorRepository actúa como almacenamiento central, SensorRegistry valida reglas de negocio para el alta de sensores (impide IDs vacíos o duplicados), SensorLister permite consultar info de los sensores, SensorDeleter da de baja sensores registrados.
2. **Módulo `reading`:** Almacena y gestiona el historial de lecturas del sistema; SensorReading define la estructura de la lectura (sensor_id, valor y timestamp), ReadingRecorder valida la existencia previa del sensor antes de guardar la lectura y ReadingHistory permite consultar el historial (total o filtrado por fechas).
3. **Módulo `anomaly`:** Evalúa las lecturas para detectar valores fuera del límite. AnomalyType y ThresholdConfig definen los tipos de anomalía y límites máximos; ThresholdConfigManager administra la configuración de umbrales por sensor (ID) y AnomalyDetector analiza la lectura frente a su configuración para emitir un AnomalyResult.
4. **Módulo `alert`:** Notifica las anomalías detectadas a diferentes formatos. Alert define una base abstracta, ConsoleAlert muestra los mensajes en terminal, FileAlert registra las alertas en un archivo (alerts.log) y AlertManager coordina todos los formatos para mandar las alertas al mismo tiempo.
5. **Módulo `gauss_distro`:** Genera lecturas simuladas para forzar el comportamiento de sensores; SensorSimulator utiliza una distribución normal o gaussiana (basada en media y desviación estándar) para simular datos.
6. **Módulo `device`:** Actúa como "módulo madre"; PipelineModule acopla todos los módulos mediante inyección de dependencias, ejecutando todo: obtención de lecturas, almacenamiento, evaluación de anomalías y emisión de alertas.

---

Consulta el [Diagrama C4 Nivel 2](Diagrama_C4.png) para ver la interacción entre módulos de forma gráfica.