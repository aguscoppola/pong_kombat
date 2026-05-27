# Pong Kombat - Documento de Especificaciones Técnicas (GDD - v0.8.0)

## 1. VISIÓN GENERAL Y ARQUITECTURA
**Pong Kombat** es un motor de físicas 2D competitivo (PVP y PVE) desarrollado en Pygame-CE. Transforma el concepto clásico del Pong mediante un sistema de combate activo, gestión de proyectiles, alteración de físicas de entorno y modos de juego con muerte súbita.

* **Resolución y Escalado:** El juego utiliza una resolución base interna de `800x600`. Se despliega utilizando `pygame.SCALED` para adaptarse dinámicamente a cualquier monitor o dispositivo móvil manteniendo el aspect ratio y la integridad de las colisiones.
* **Soporte Multiplataforma (PWA):** El motor está insonorizado (`try...except` en el mixer) y adaptado (Fetch Monkeypatching) para compilar en WebAssembly vía `pygbag`. Soporta ejecución offline, haptic feedback (`vibrate()`) y transformaciones CSS a 90° dinámicas para dispositivos móviles.

---

## 2. DICCIONARIO DE ESTADOS DE LA UI (State Machine)
El motor principal (`game_engine.py`) funciona en base a una máquina de estados finitos que controla qué menú o lógica se renderiza.

* `STATE_MAIN_MENU`: Menú de inicio. Gestiona la bifurcación entre Solo, Multiplayer, Settings, Extras y Skins.
* `STATE_MODE_SELECTION`: Selector de modo multijugador.
* `STATE_SOLO_SUBMODE_SELECTION`: Submenú de 1 Jugador. Contiene los botones `btn_classic_rect` (Clásico), `btn_arcade_rect` (Arcade) y `btn_endless_rect` (Sin Fin).
* `STATE_ARCADE_TUTORIAL`: Estado temporal para renderizar el tutorial del modo campaña.
* `STATE_ENDLESS_TUTORIAL`: Nuevo estado v0.8.0. Renderiza la UI del submenú en segundo plano con un manto negro semitransparente (`SRCALPHA` a 220) por encima. Solo redibuja el botón "SIN FIN" para resaltarlo.
* `STATE_SETTINGS` / `STATE_MODIFIERS` / `STATE_SKINS`: Menús de configuración.
* `STATE_GAME`: El bucle del motor de físicas y gameplay.
* `STATE_GAME_OVER`: Pantalla de victoria/derrota.

---

## 3. DICCIONARIO DE PODERES Y ARMAS
Los jugadores adquieren poderes capturando relojes, golpeando la pelota repetidas veces o recolectando ítems orbitales. Existe una **Restricción de Poder Activo**: Si un jugador tiene un efecto de alteración activo (Imán, Chicle, Fantasma, Sueño), no puede adquirir otro poder nuevo hasta que se agote, a excepción de los poderes de impacto físico (Naranja/Revólver).

* **BEER WATCH (Reloj Cerveza - ID 7):**
    * **Mecánica:** Modificador de estado que altera la percepción y control del oponente. Emite un sonido chiptune sintetizado (`glup.wav`).
    * **Efecto Jugador Humano:** Invierte los controles físicos de movimiento obligando a jugar en reversa.
    * **Efecto Inteligencia Artificial:** Ignora la inversión del motor físico (`entities.py`). En su lugar, induce un *cooldown* de pánico de 2 segundos donde la IA convulsiona sin rumbo, seguido de una miopía táctica permanente que aplica un desfase de 20 píxeles a su cálculo de intercepción.
* **VIOLET WATCH (Reloj Violeta - Meditación):** * **Mecánica:** Se activa manteniendo la paleta completamente inmóvil durante 3 segundos.
    * **Visuales:** Renderiza una barra de carga dinámica sobre la paleta. Al completarse, emite sonido de campana y explosión de partículas.
    * **Resultado:** Otorga un poder aleatorio al instante.
* **ESPECTRAL (Teletransportación Asesina):**
    * **Mecánica:** Otorga munición para ejecutar un ataque sorpresivo basado en la posición de la pelota.
    * **Impacto:** Permite gatillar una reacción rápida cuando la pelota cruza el medio campo, desestabilizando la defensa rival mediante físicas impredecibles.
* **REVOLVER (Arma Orbital):**
    * **Mecánica:** Aparece en el centro del campo con una probabilidad configurable (10%, 25%, 50%, 100%).
    * **Munición:** Otorga 3 balas amarillas. Posee un seguro de disparo (`bullet_immunity` de 0.1s) para no autoinfligirse daño.
    * **Impacto:** Las balas viajan en línea horizontal recta a 2x la velocidad base. Cualquier impacto directo contra el rival causa explosión inmediata y pérdida del punto (Muerte Súbita/Gol).
* **SLEEP (Sueño):**
    * **Mecánica:** Dispara un proyectil violeta que viaja a 2.5x la velocidad de la pelota.
    * **Físicas:** Al cruzar la mitad del campo (coordenada `SCREEN_WIDTH // 2`), el proyectil se divide en 3 esferas (una recta, dos a 45°).
    * **Impacto:** Inmoviliza completamente la paleta rival durante 4 segundos.
* **GUM (Chicle):**
    * **Mecánica:** Tiñe la paleta de rosa. La pelota principal se queda pegada magnéticamente a la paleta al hacer contacto, permitiendo retenerla.
    * **Ofensiva:** Permite disparar proyectiles gigantes de chicle con físicas de rebote erráticas para confundir y empujar al oponente.
* **GHOST (Fantasma):**
    * **Mecánica:** Dispara un proyectil blanco-azulado espectral. Viaja a una velocidad 50% más lenta.
    * **Impacto:** Si el rival no lo atrapa/bloquea con su paleta, el proyectil cruzará la línea de gol y le sumará un punto válido al jugador que lo disparó.
* **MAGNET (Imán) / RED (Fuego) / ORANGE (Demolición):**
    * Poderes elementales de control de trayectoria e impactos físicos violentos de repulsión.

---

## 4. DICCIONARIO DE MODIFICADORES (Pestaña EXTRAS & CAOS)
Reglas ambientales que alteran las matemáticas de la pista.

* **TIC-TAC-TOE (Ta-Te-Ti) [v0.8.0]:**
    * **Comportamiento:** Renderiza una grilla de 3x3 en el centro del campo. Las líneas y celdas son cuerpos rígidos (colliders).
    * **Efecto:** Altera radicalmente el control del medio campo, bloqueando proyectiles y rebotando la pelota en ángulos asimétricos.
* **ENDLESS CHAOS (Caos Infinito) [v0.8.0]:**
    * **Gated Content:** Bloqueado y oculto por defecto. Se activa en `save_data.json` únicamente tras completar el Nivel 7 del Modo SIN FIN en una sola racha.
    * **Efecto:** Fuerza al motor a saturar las físicas (portales máximos, gravedad severa, proyectiles erráticos).
* **PORTALS (Portales Dimensionales):**
    * **Comportamiento:** Pares conectados (Azul/Naranja, Rojo/Verde). Soportan 5 tamaños (Minion a GIANT). Pueden orientarse verticalmente u horizontalmente.
    * **Físicas:** Al cruzar, la pelota gana +0.5% de velocidad y altera su ángulo 5° para evitar bucles infinitos de teletransporte (infinite loops).
* **FLOATING PLANETS (Planetas Flotantes):**
    * **Comportamiento:** Cuerpos celestes con nombres, colores y sistemas de partículas temáticos (Tierra, Marte, Júpiter, Saturno).
    * **Físicas:** Ejercen gravedad en área (Moon, Planet, Gas Giant, Star). Pueden configurarse como indestructibles o destructibles (explotan tras 3 impactos).
* **WEATHER SYSTEM (Sistema de Clima):**
    * **Lluvioso (Rainy):** De 10mm a 50mm (Torrencial). Físicas de gotas cayendo en diagonal, sonido ambiental dinámico de 3 capas superpuestas (cross-fade de 0.3s).
    * **Nublado / Relámpagos (Cloudy / Lightning):** Oscurecimiento de pantalla y flashes fotográficos esporádicos.
* **MOUSE (Ratón):**
    * Entidad NPC que corre por el campo. Velocidad inicial y tiempo de aparición (delay spawn) configurables.
* **REGLAS DE PUNTUACIÓN:**
    * **Golden Goal:** El primer punto gana la partida.
    * **Match Point:** Requiere ganar por una diferencia estricta de 2 puntos.
    * **Multiplicador X2:** Ítem dorado en el campo que duplica los puntos del siguiente gol.

---

## 5. MODOS DE JUEGO (Lógica de Motor)
### 5.1. Modo ARCADE (Campaña de 7 Niveles)
El progreso se guarda. Vencer el nivel 7 desbloquea la Corona y el panel `TEST LEVEL`.
* **Nivel 1 & 2:** 1 Punto (Golden Goal).
* **Nivel 3:** 1 Punto (Match Point forzado).
* **Nivel 4:** 3 Puntos (Variante Poderes vs Variante Ratón).
* **Nivel 5:** 3 Puntos. Táctico. 2 Portales, Planetas fijos. Relojes persistentes.
* **Nivel 6:** 3 Puntos. Clima Extremo. Restricción masiva de habilidades según la variante climatológica.
* **Nivel 7 (Boss):** 6 Puntos (Match Point + Golden Goal experimental). X2 activo inicial. 4 Portales, clima extremo, revólver 100%, planetas destructibles.

### 5.2. Modo SIN FIN (Endless Mode) [v0.8.0]
Modo PVE de supervivencia procedimental y generativa.
* **Muerte Súbita:** `max_score = 1`. Perder 1 punto significa Game Over y reinicio del contador de racha (Win Streak) a cero.
* **Entropía Acumulativa:** La dificultad aumenta inyectando modificadores matemáticos y entidades físicas al azar. En cada nivel superado, se incrementa la cantidad de modificadores activos en la pista de forma simultánea.
* **Recompensas:** Guardado persistente de la mejor racha. Al llegar al nivel 7 continuo, desencadena el unlocker de `ENDLESS CHAOS`.

---

## 6. SISTEMAS DE INTELIGENCIA ARTIFICIAL (Player 2)
El script `ai_controller.py` contiene un árbol de decisiones jerárquico actualizado.
* **Manejo de Ebriedad (Drunk State):** La IA posee un escudo contra el motor físico que evita la inversión matemática de sus controles. Al emborracharse, simula torpeza humana: se paraliza durante 2 segundos convulsionando en el lugar, y luego intenta atajar la pelota sumándole un desfase permanente de 20 píxeles de error a su `final_y`. Cancela automáticamente cualquier intento de Meditación Violeta.
* **Evaluación de Radar Espectral y Fantasmas:** Detecta proyectiles GHOST. Calcula la cercanía horizontal (`centerx`) de las pelotas reales vs espectrales para decidir cuál atajar primero. Si posee el poder Espectral, espera inteligentemente a que la pelota cruce la mitad de la cancha para gatillarlo con un 20% de probabilidad por frame, buscando el error del jugador.
* **Supervivencia Absoluta:** La máxima prioridad es evadir colisiones fatales. Si un proyectil Revólver o bola Naranja se acerca, la IA aborta la persecución de la pelota y se mueve a una zona segura de 70px de distancia libre.
* **Gestión Táctica (Hold/Fire):** Con el revólver en mano, no dispara si está defendiendo su línea de fondo (evita soltar un tiro por error y perder el arma si recibe un gol).
* **Manejo de Meditación:** Lee el estado de la pelota y de la pista. Si no hay amenazas acercándose rápidamente, se queda inmóvil 3 segundos para cobrar el Reloj Violeta.

---

## 7. UX, RENDERING Y SISTEMA DE TEXTOS
* **Typewriter Engine (Máquina de escribir):**
    * Motor de renderizado en `game_engine.py` controlado por `tutorial_text_timer` y `tutorial_text_index`. Reproduce sonido `pop` por cada palabra procesada (`split(" ")`).
* **Soporte Multilínea Dinámico (v0.8.0):**
    * Procesa el carácter `\n`. En lugar de desbordar la caja, divide el texto y calcula el `get_height()` de la tipografía `small_font` para apilar y centrar verticalmente hasta 3 renglones dentro de un bloque negro inferior de borde blanco (100px de altura total).
* **Focus Rendering (Manto de Foco):**
    * Se dibuja una Surface de `(0,0,0, 220)` sobre toda la UI para oscurecer botones inactivos (incluyendo el botón Back). Solo los elementos esenciales de la interacción actual se dibujan en una capa Z superior (ej: el botón de la modalidad seleccionada o el contenedor de texto).