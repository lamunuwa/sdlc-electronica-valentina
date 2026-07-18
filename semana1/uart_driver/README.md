# Driver con CAN & Thread-Safe

Incorporé los submodulos del driver UART para cumplir con los requerimientos de la distinción por Alto Potencial, le di soporte CAN Bus, una forma de almacenamiento Thread-Safe y hacer un Logging legible y estructurado JSON.

## 1. CAN (Controller Area Network)

### ¿Qué es y por qué se incluye?

CAN (Controller Area Network) es un protocolo de comunicación basado en prioridades, muy utilizado en la industria. En este driver, al ser UART, emulamos la estructura de un CAN clásico de un canal serie. Esto permite al sistema clasificar, validar e identificar flujos de datos provenientes de múltiples nodos periféricos utilizando un identificador único (ID).

### Implementación en parsers.py

Para integrar este protocolo sin romper lo que ya tenia, se desarrolló `CanParser`. El formato UART-CAN maneja un flujo estático de 12 bytes fijos:

- SOF (Start of Frame): Un byte de sincronía fijo (0x5A).
- ID: 2 bytes que determinan la identidad y prioridad en el bus.
- DLC (Data Length Code): 1 byte que indica cuántos de los siguientes 8 bytes contienen información.
- DATA: Bloque fijo de 8 bytes de data, bloqueado a 8 por el valor del DLC.

El método parse() extrae estos valores mediante y retorna una instancia inmutable de la dataclass CanFrame.

## 2. Buffer Thread-Safe

### Race Conditions

En un sistema, el hilo encargado de la lectura del puerto serie y el hilo encargado del procesamiento de datos en la aplicación operan de forma asíncrona. Si ambos hilos intentan modificar la lista de datos simultáneamente, ocurre una condición de carrera, corrompiendo la integridad de la memoria del buffer.

### Threading.Lock (pedido en el documento)

Para garantizar la seguridad entre hilos, la clase `ThreadSafe` implementa exclusión mediante "Lock" que actúa bajo la siguiente secuencia:

1. El hilo escritor recibe un paquete de datos.
2. Los datos llegan en formato serial y son almacenados temporalmente.
3. Antes de modificar el buffer, el hilo escritor intenta adquirir el Lock.
4. Si Lock marca que está actualmente con el hilo lector, el escritor entra en estado de espera (bloqueo) hasta que sea liberado.
5. Una vez que el candado es adquirido, el hilo escritor tiene acceso unico al buffer compartido.
6. Una vez completada la escritura, el hilo libera el candado.

## 3. Logging JSON

### ¿Qué hice?

En este, la verdad, no investigué mucho; sin embargo, desde que entré en el mundo de sistemas embebidos, me encuentro recurrentemente con los típicos pines de debug del microcontrolador o la placa y siempre es muy difícil saber dónde está el error sin que se me vaya indicando paso a paso cómo va el sistema. Entonces implementé eso, agregando el nivel de severidad del problema, qué pasó y el diccionario printeado.
