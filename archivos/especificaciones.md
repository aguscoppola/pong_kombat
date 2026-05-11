# Pong Kombat - Documento de Especificaciones Técnicas (v0.6.0)

## 1. Visión General
**Pong Kombat** es una evolución del clásico arcade que introduce mecánicas de combate, gestión de poderes y alteración del entorno mediante ítems. La v0.6.0 introduce el **Modo Arcade**, una campaña de un solo jugador con progresión de dificultad y recompensas desbloqueables.

---

## 2. Sistema de Controles (Input Mapping)
... (Igual que v0.5.0) ...

### Modo SOLO (IA de Supervivencia Avanzada)
*   **Radar de Amenazas Letales**: La IA detecta balas del **REVÓLVER** y bolas **NARANJAS** en trayectoria de colisión. Prioriza la esquiva absoluta (moviéndose 70px fuera de la trayectoria) a menos que la pelota esté a menos de 80px de su fondo.
*   **Gestión de Poder SLEEP**: La IA utiliza el poder de sueño apuntando al centro de la paleta del jugador. Detecta las mini-bolas violetas y las esquiva si no tiene la pelota principal cerca.
*   **Gestión Defensiva**: Si la IA posee el poder **REVOLVER**, no disparará si la pelota principal está en peligro de gol; primero asegurará el punto para mantener el poder.

---

## 3. Modos de Juego (v0.6.0)
### MODO ARCADE
*   **Estructura:** 5 niveles consecutivos sin posibilidad de error.
*   **Dificultad:** La velocidad de la paleta enemiga y la agresividad aumentan un 15% por nivel.
*   **Nivel Final:** El Nivel 5 presenta una ambientación roja y una IA con reflejos máximos.
*   **Recompensa:** Al completar el Nivel 5, se desbloquea el modificador **CROWN (Corona)** permanentemente.

---

## 4. Diccionario de Modificadores (Match Modifiers)
...
*   **SLEEPING (The Dreamer Update):** 
    *   **Logic:** Lanza un proyectil violeta que se divide en 3 al cruzar la mitad del campo (ángulos de 45°).
    *   **Effect:** Inmoviliza al oponente por 4 segundos si es impactado.
    *   **Velocity:** El proyectil viaja a 2.5x la velocidad base de la pelota.
*   **CROWN HAT (Reward):** 
    *   Accesorio visual desbloqueable tras vencer el modo Arcade. Puede asignarse al Jugador 1, Jugador 2 o ambos.
...

---

## 7. Sistema de Tutoriales
*   **Tutorial General:** Accesible mediante el botón "?" pixelado en el menú principal. Guía al usuario por la configuración de idioma, volumen y el uso de modificadores antes de entrar en combate.
*   **Tutorial Arcade:** Guía específica dentro del menú SOLO que explica la estructura de los 5 niveles y la recompensa de la Corona.
*   **Interacción:** Ambos sistemas utilizan un manto negro de enfoque y navegación mediante la barra espaciadora con efecto de escritura palabra por palabra.

---

## 8. Lógica de Versionado (SemVer)
*   **v0.4.0**: "The Solo & Settings Update" - Modo contra IA y panel de ajustes.
*   **v0.5.0**: "The REVOLVER Update" - Combate letal, IA pistolera y poder de chicle.
*   **v0.5.1**: "The Architect & Survival Update" - Arquitectura modular, IA con radar de esquiva.
*   **v0.6.0**: "The Arcade & Sleep Update" - Modo campaña, poder de sueño, recompensas desbloqueables e IA táctica.
