# Pong Kombat - Documento de Especificaciones Técnicas (v0.5.1.1)

## 1. Visión General
**Pong Kombat** es una evolución del clásico arcade que introduce mecánicas de combate, gestión de poderes y alteración del entorno mediante ítems. El juego utiliza una arquitectura desacoplada donde la lógica de decisiones (AIController) y las leyes físicas (PhysicsEngine) están separadas del bucle principal de juego.

---

## 2. Sistema de Controles (Input Mapping)
... (Igual que v0.5.0) ...

### Modo SOLO (IA de Supervivencia)
*   **Radar de Amenazas**: La IA detecta proyectiles amarillos (balas) en trayectoria de colisión y prioriza la esquiva sobre cualquier otra acción.
*   **Gestión Defensiva**: Si la IA posee el poder **REVOLVER**, no disparará si la pelota principal está en peligro de gol; primero asegurará el punto para mantener el poder.
*   **Aiming (Revolver)**: Una vez a salvo, la IA alineará su centro con la paleta del jugador para disparar con precisión quirúrgica.

---
... (Resto de secciones igual) ...

## 4. Diccionario de Modificadores (Match Modifiers)
...
*   **REVOLVER (The Architect & Survival Update):** 
    *   **Logic:** Ítem orbital que otorga 3 disparos letales.
    *   **Precision:** Trayectoria recta horizontal con seguro de disparo de 0.1s.
    *   **Probability of Appear:** Sub-modificador configurable: Low (10%), Default (25%), Quite (50%) y Always (100%).
...

---

## 8. Lógica de Versionado (SemVer)
*   **v0.4.0**: "The Solo & Settings Update" - Modo contra IA y panel de ajustes.
*   **v0.5.0**: "The REVOLVER Update" - Combate letal, IA pistolera y poder de chicle.
*   **v0.5.1**: "The Architect & Survival Update" - Arquitectura modular, IA con radar de esquiva y probabilidad de revólver.
*   **v0.5.1.1**: "The Stability & UI Fix" - Motor de física centralizado, fixes de colisión y pulido de UI.
