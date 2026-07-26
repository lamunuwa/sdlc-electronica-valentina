# Definition of Done

Este documento marca la checklist de calidad que debe pasar cualquier funcionalidad para poder ser considerada **done** antes de ser integrada a la rama principal.

---

## 1. Calidad de código

- [ ] **Errores:** `ruff check` no reporta advertencias ni errores (reglas `E`, `F`, `I`, `UP`, `B`).
- [ ] **Formato:** el código cumple con el formato configurado en `ruff`.

## 2. Tipado

- [ ] **Compatibilidad:** el código es compatible con **Python 3.13**.
- [ ] **Definición de Tipos:** todas las funciones y métodos tienen sus tipos definidos.
- [ ] **Verificación:** `mypy` se ejecuta sin errores ni advertencias.

## 3. Pruebas y cobertura

- [ ] **Feats:** cada nueva funcionalidad lleva sus respectivos test.
- [ ] **Pruebas:** `pytest` ejecuta los tests y todos aprueban exitosamente.
- [ ] **Umbral de Cobertura:** la cobertura total del código no cae por debajo del **90%**.

## 4. Automatización

- [ ] **Pre-commit:** todos los hooks locales (`ruff-lint`, `ruff-format`, `mypy`, `pytest-cov`) se ejecutan y pasan sin errores antes de confirmar el commit GREEN.

## 5. Documentación y Control de Versiones

- [ ] **Comentarios:** las clases cuentan con un comentario inferior que explica su funcionalidad.
- [ ] **Pull Request:** El PR describe claramente los cambios realizados.
