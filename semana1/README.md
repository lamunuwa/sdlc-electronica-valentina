# Semana 1 — Python profesional y principios SOLID

Semana inicial, debíamos implementar conceptos de hardware/firmware a sus equivalentes de software. Mediante las prácticas desarrollamos:

- Python idiomático (type hints, dataclasses, enums, protocolos)
- Los fundamentos SOLID

Entre algunas otras habilidades como git/github y generación de documentos como una bitácora de IA.

---

## Proceso de instalación y validación

**Nota:** El repositorio lo estoy desarrollando en WSL2: Debian. A pesar de eso, cualquier distro de Linux o WSL/WSL2 debería de funcionar para probar el repositorio.

1. Descargar el repositorio:

```bash
git clone https://github.com/lamunuwa/sdlc-electronica-valentina.git
```

2. Activar el entorno virtual:

```bash
source .venv/bin/activate
```

3. Instalar el paquete de librerías:

```bash
pip install -r requirements.txt
```

4. Verificar instalación:

```bash
pip list
```

5. Correr validación mediante pytest:

```bash
pytest semana1/ -v --cov=semana1 --cov-report=term-missing
```

## Reflexión SOLID

Las reglas SOLID son una filosofía de diseño orientada a evitar generación de códigos ilegibles, difíciles de modificar, expandir o reutilizar.

Sin embargo, es importante saber que no siempre se deben implementar; el aplicar de forma rígida los principios puede llevar a extender códigos simples o no tan elaborados, lo que también es una mala práctica.

Lo que entendí por cada fundamento:

SRP - Single Responsibility Principle: Cada clase o función debe encargarse de una sola cosa, una sola función del software. El crear clases "todo en uno" viola esta norma directamente.

OCP - Open/Closed Principle: El código debe estar abierto a su extensión pero cerrado a su modificación, es decir, deberíamos poder agregar nuevas funciones al software sin necesidad de modificar el código existente.

LSP - Liskov Substitution Principle: Los subtipos de una clase deben poder reemplazar a la clase sin alterar el programa. Hay un ejemplo que vi en internet donde decían que la clase "Pingüino" que hereda de la clase "Ave" rompe el principio, ya que dicha clase tiene una función "volar()" y los pingüinos no pueden volar.

4. ISP - Interface Segregation Principle: El más simple, es mejor tener muchas interfaces pequeñas y específicas que una sola interfaz "todo en uno" con funciones inútiles.

5. DIP - Dependency Inversion Principle: Seguido la más complicada, como tal la definición es "Depende de abstracciones, no de concreciones", lo cual no dice nada, pero se entiende como que los módulos de alto nivel no deben depender de los módulos de bajo nivel; por ejemplo, la clase "Procesamiento" (módulo de alto nivel) no debe heredar la clase "Base de datos" (módulo de bajo nivel), para hacerlos trabajar juntos hacemos una función abstracta (@abstractmethod/ABC) que fije los valores que intercambiarán.