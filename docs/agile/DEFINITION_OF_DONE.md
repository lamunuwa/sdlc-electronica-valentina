# Definition of Done

Este documento marca la checklist de calidad que debe pasar cualquier funcionalidad para poder ser considerada **done** antes de ser integrada a la rama principal.

---

## 1. Calidad de código

- [ ] **Errores:** `ruff check` no reporta advertencias ni errores (reglas `E`, `F`, `I`, `UP`, `B`).
- [ ] **Formato:** el código cumple con el formato configurado en `ruff`.
- [ ] **Arquitectura:** el código respeta la separación en 4 capas (`routers` -> `services` -> `repositories` -> `models/schemas`).

## 2. Tipado

- [ ] **Compatibilidad:** el código es compatible con **Python 3.13**.
- [ ] **Definición de Tipos:** todas las funciones y métodos tienen sus tipos definidos.
- [ ] **Verificación:** `mypy` se ejecuta sin errores ni advertencias.

## 3. Pruebas y cobertura

- [ ] **Feats:** cada nueva funcionalidad lleva sus respectivos test.
- [ ] **Pruebas:** `pytest` ejecuta los tests y todos aprueban exitosamente.
- [ ] **Umbral de Cobertura:** la cobertura total del código no cae por debajo del **90%**.

## 4. Documentación

- [ ] **Swagger:** Todos los endpoints y modelos Pydantic cuentan con descripciones, tipos y ejemplos funcionales en `/docs`.
- [ ] **Decisiones de Diseño:** Las decisiones de índices o arquitectura quedan documentadas en la carpeta `docs/adr/`.
- [ ] **Comentarios:** las clases cuentan con un comentario inferior que explica su funcionalidad.

## 5. Control de Versiones

- [ ] **Issues:** Todos los User Stories se adjuntan como Issues y se encuentran en la tabla del proyecto.
- [ ] **Pull Request:** El PR incluye una descripción clara, resumen de cambios y guía paso a paso para probar la API.
- [ ] **AI Log:** Se registró la interacción con la IA en `AI_LOG.md`.
