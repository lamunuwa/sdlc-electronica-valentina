# Registro de Retrospectivas por Sprint

Este documento registra las sesiones de retrospectiva al finalizar cada Sprint para evaluar el proceso de trabajo, identificar mejoras y hacer seguimiento a los compromisos de mejora.

---

## Sprint 2

### ¿Qué salió bien?

La API fue desarrollada e implementada con éxito, satisfaciendo la totalidad de los requisitos que me puse en el Sprint. Aunque con tropiezos logre implementar la arquitectura limpia por capas: Se logró una separación de responsabilidades clara y legible:

- Estructura de dominio: división explícita de componentes entre sensors y readings en todas las carpetas de app/.
- Lógica de negocio: código en módulos de servicios (catalog, ingestion y validators), lo que facilitará la escalabilidad y mantenimiento del proyecto.

### ¿Qué puedo mejorar?

Durante la sesión de seguimiento identifiqué que mi conocimiento de SQL es puramente operativo/superficial. Domino lo básico para realizar consultas estándar sin perderme, pero me faltan bases sólidas. Por otro lado, al intentar aplicar una división de archivos como lo que se pedia, 5 subcarpetas (yo hice 6), la complejidad me sobrepasó. Esto derivó en confusión sobre el flujo de la aplicación y me terminó burnouteando.

### Acción concreta para lograrlo

1. Ruta de práctica en SQL: dedicarme en el futuro a resolver ejercicios prácticos de SQL en plataformas, agregaciones y subconsultas, despues ir subiendo el nivel.

2. Práctica de diseño modular progresivo: Iniciar proyectos con una estructura como la realizada; en módulos (solo cuando la complejidad del código realmente lo exija). Posiblemente aplicar mapeo visual previa a código, dibujar diagramas simples de clases/dependencias antes de dividir archivos.

---

## Sprint 1

### ¿Qué salió bien?

Logré aplicar con éxito los conceptos de Scrum, estructurando el backlog con User Stories, estimación con Story Points, Issues, priorización por MoSCoW. y la redacción de criterios de aceptación utilizando sintaxis Gherkin. TDD fue el avance más significativo. Escribir las pruebas antes del código de producción garantizó que la implementación se limitara estrictamente a la funcionalidad requerida (solo en un US tire mas codigo del que deberia, pero fue pura vanidad).

Esto no entra como avance del sprint 1 como tal pero la aplicación de los principios SOLID facilitó el desarrollo cuando tenia US que hacian cambios en un mismo codigo. Asimismo, la automatización de linters y pruebas, la division en ramas (branches) y Pull Requests, mejoro el flujo de trabajo.

### ¿Qué puedo mejorar?

Identifique 2 puntes graves:

1. Commits: aunque mantuve TDD siempre y mi versión básica de Conventional Commits, los mensajes de commit fueron demasiado genéricos. Con el fin de mantener "limpieza visual", sacrifiqué lo descriptivos que eran mis commits.

2. Lectura de errores: Aunque TDD redujo significativamente los errores, se presentaron fallos recurrentes de tipado (como AttributeError o retornos inesperados de tipo NoneType). La interpretación de estos errores consumió tiempo que pudo optimizarse con un mejor análisis.

### Acción concreta para lograrlo

Para mitigar los puntos débiles de este sprint, voy a volver a mis commits más descriptivos, aunque eso arruine mi idea de limpieza visual, y practicaré más mi tipado en el código; en su mayoría, intentaré dejar de usar Win + . para ver el error.