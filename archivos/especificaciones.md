# Pong Kombat - Documento de Especificaciones Técnicas (v0.7.1)

## 1. Visión General
**Pong Kombat** es una evolución del clásico arcade que introduce mecánicas de combate, gestión de poderes y alteración del entorno mediante ítems. La v0.7.1 consolida la **Infraestructura Móvil y Web**, introduciendo soporte para redes locales, sonido ambiental generativo y estabilidad absoluta de carga.

---

## 2. Sistema de Controles (Input Mapping)
### Entrada Táctil y Móvil (v0.7.0)
*   **Gestión de Dedos (Multitouch)**: El motor rastrea múltiples IDs de contacto de forma simultánea. Permite el movimiento independiente de ambas paletas y el uso de poderes sin bloqueos de entrada.
*   **Modo Clásico (Botones Virtuales)**: Botones temáticos de dirección (ʌ, v) y activación de poder (POW). El botón POW cambia de color dinámicamente según el poder cargado.
*   **Modo Geográfico (Position-Based)**: El usuario toca directamente la posición de destino. El campo se divide verticalmente en dos zonas de control (Mitad Izquierda: P1, Mitad Derecha: P2).
*   **Unificación de Entrada (Virtual Finger)**: El ratón en PC simula el comportamiento de un dedo, permitiendo pruebas de UX móvil en entornos de escritorio sin discrepancias de lógica.

### Modo SOLO (IA de Supervivencia Avanzada)
*   **Radar de Amenazas Letales**: La IA detecta balas del **REVÓLVER** y bolas **NARANJAS** en trayectoria de colisión. Prioriza la esquiva absoluta (moviéndose 70px fuera de la trayectoria) a menos que la pelota esté a menos de 80px de su fondo.
*   **Defensa vs Fantasmas (v0.6.1)**: La IA ahora combina la lista de pelotas reales y fantasmales del oponente. Elegirá como objetivo la que esté más cerca de su posición horizontal (`centerx`), permitiendo defender goles espectrales de forma efectiva.
*   **Gestión de Poder SLEEP**: La IA utiliza el poder de sueño apuntando al centro de la paleta del jugador. Detecta las mini-bolas violetas y las esquiva si no tiene la pelota principal cerca.
*   **Gestión Defensiva**: Si la IA posee el poder **REVOLVER**, no disparará si la pelota principal está en peligro de gol; primero asegurará el punto para mantener el poder.

---

## 3. Modos de Juego (v0.6.1)
### MODO ARCADE
*   **Estructura:** 5 niveles consecutivos sin posibilidad de error.
*   **Persistencia (v0.6.1):** El estado de completado se guarda en `save_data.json`. Si se completa el modo Arcade, el selector de niveles y la corona permanecen desbloqueados permanentemente.
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
*   **ACTIVE POWER RESTRICTION (v0.6.1):**
    *   Si una paleta tiene un efecto activo (Imán, Chicle, Fantasma, Sueño), no podrá recibir un nuevo poder mediante el sistema de toques (hits) hasta que el efecto termine.
    *   **Excepción:** Los poderes de contacto (Fuego y Naranja) pueden ser recibidos en cualquier momento.

---

## 7. Sistema de Tutoriales
*   **Tutorial General:** Accesible mediante el botón "?" pixelado en el menú principal. Guía al usuario por la configuración de idioma, volumen y el uso de modificadores antes de entrar en combate. **Se autogestiona mediante persistencia para no aparecer repetitivamente.**
*   **Tutorial Arcade:** Guía específica dentro del menú SOLO que explica la estructura de los 5 niveles y la recompensa de la Corona.
*   **Interacción:** Ambos sistemas utilizan un manto negro de enfoque y navegación mediante la barra espaciadora con efecto de escritura palabra por palabra.

---

## 8. Lógica de Versionado (SemVer)
*   **v0.4.0**: "The Solo & Settings Update" - Modo contra IA y panel de ajustes.
*   **v0.5.0**: "The REVOLVER Update" - Combate letal, IA pistolera y poder de chicle.
*   **v0.5.1**: "The Architect & Survival Update" - Arquitectura modular, IA con radar de esquiva.
*   **v0.6.0**: "The Arcade & Sleep Update" - Modo campaña, poder de sueño, recompensas desbloqueables e IA táctica.
*   **v0.6.1**: "The Persistence & Credits Update" - Sistema de guardado JSON, panel de créditos y balance de combate.
*   **v0.7.0**: "The Mobile & Web Update" - Soporte táctil, Modo Geográfico, Escalado Dinámico Inteligente e infraestructura PWA para funcionamiento offline.
*   **v0.7.1**: "The Rainy Combat & Local Network Update" - Sonido generativo de lluvia pura, Interceptor de Fetch Global (Fetch Monkeypatching) para móviles por Wi-Fi, apertura de Firewall automatizada e inyección dinámica de CSS móvil.

---

## 9. Arquitectura Móvil y Web (v0.7.1)
*   **Escalado Dinámico (SCALED)**: El motor utiliza `pygame.SCALED` para desacoplar la lógica de 800x600 de la resolución física. Esto permite que el juego se adapte a cualquier relación de aspecto (21:9, 4:3, etc.) sin deformar las colisiones.
*   **Infraestructura PWA**: 
    *   **Offline Mode**: Mediante Service Workers, el juego es jugable sin internet.
    *   **Standalone Experience**: El `manifest.json` permite la instalación como app nativa, forzando la orientación horizontal y eliminando la interfaz del navegador.
    *   **Haptic Feedback**: Integración de la API `vibrate()` del navegador para sincronizar impactos visuales con vibración física en móviles.
*   **Interceptor de Peticiones Global (Fetch Monkeypatching)**:
    *   Para evitar fallos de CORS y 404s silenciosos en redes Wi-Fi locales al descargar la rueda de Pygame (`pygame_ce`), se inyectó una función interceptora que monitorea el objeto `window.fetch`. 
    *   Si detecta una solicitud de descarga dirigida al CDN oficial de Pygame-web para el `.whl` del motor, reescribe de forma transparente el destino apuntando a `window.location.origin` (nuestro servidor local). Esto permite que los archivos de configuración JSON genéricos se carguen de internet y la biblioteca pesada se transmita de forma local e instantánea.
*   **Inyección Dinámica de CSS Móvil**:
    *   Se eliminaron las restricciones estáticas de visualización en la cabecera que rompían los clics del puntero en PC. 
    *   El motor ahora detecta dinámicamente si el navegador del cliente es móvil (`/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i`). Si es afirmativo, inyecta mediante JS en tiempo de ejecución las reglas de transformación física a 90° (Landscape) y el bloqueo absoluto de zoom. En caso contrario (Desktop PC), se omiten al 100%, restaurando la interacción del ratón original.
    *   **Clima y Sonido Generativo Ambiental**:
        *   **Sonido de Lluvia (`rainy.wav`)**: Generado mediante un script matemático (`crear_lluvia.py`) combinando tres capas de ruido con filtros de paso bajo para graves, medios y agudos, y un cross-fade lineal de 0.3 segundos para lograr un loop ininterrumpido sin clicks de fase.
        *   **Clima Lluvioso**: El modificador visual "RAINY DAY" dibuja partículas de gotas de lluvia cayendo en diagonal, sincronizadas con el nuevo canal inmersivo de audio tridimensional.
