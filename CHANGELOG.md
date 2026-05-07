# Registro de Cambios (Changelog)

Aquí guardaremos una lista de todas las cosas nuevas que le vayamos agregando al juego o los errores que vayamos arreglando. Así no nos olvidamos de nada y cualquier persona que vea el proyecto sabrá en qué estuvimos trabajando.

## [0.5.0] - 2026-05-07
### The REVOLVER & GUM Combat Update (v0.5.0 Final)
Esta actualización transforma el Pong en un duelo de disparos tácticos y control de masas, con armas letales y una IA que sabe defenderse y atacar.

#### Agregado (Nuevas cosas)
- **Nuevo Modificador: REVOLVER (Pestaña EXTRAS)**:
    - **Ítem Orbital**: Aparece con un 25% de probabilidad junto a cada reloj.
    - **Munición**: Otorga 3 balas amarillas de alta velocidad (x2 velocidad base).
    - **Letalidad Total**: Cualquier contacto con la bala provoca una explosión instantánea y pérdida del punto.
    - **Puntería Recta**: Las balas salen del centro de la paleta en trayectoria perfectamente horizontal.
    - **Sonido Arcade**: Feedback auditivo "PIUM" al disparar.
    - **IA Pistolera**: La computadora ahora reconoce el revólver, te apunta directamente y te dispara con precisión.
- **Nuevo Poder: GUM (CHICLE)**:
    - Las paletas se vuelven de color rosa.
    - **Adherencia Automática**: Las pelotas se quedan pegadas a la paleta al contacto.
    - **Proyectiles de Chicle**: Dispara bolas de chicle gigantes que confunden al rival y rebotan de forma errática.
    - **IA Táctica**: La IA usa el chicle para atrapar la bola, esquivar al ratón y disparar chicles de cobertura.

#### Arreglado (Bugs y Pulido)
- **Seguro de Disparo**: Añadido `bullet_immunity` de 0.1s para evitar que el jugador explote por su propia bala al disparar.
- **VFX Fluido**: Las explosiones de las balas y paletas ya no se congelan al marcar gol; las partículas siguen fluyendo durante el saque.
- **Transparencia en Goles**: Las balas que no impactan al jugador desaparecen sin sumar puntos injustos.
- **IA Anti-Bloqueo**: Corregido el error donde la IA se congelaba al tener la pelota pegada con el chicle.

## [0.4.0] - 2026-05-06
### The Solo & Settings Update
Introducción del modo para un jugador y control total sobre la configuración del juego.

#### Agregado (Nuevas cosas)
- **Modo SOLO (IA)**:
    - Menú de selección de modo (MULTIPLAYER vs SOLO).
    - IA adaptativa que busca ítems, esquiva amenazas y utiliza poderes estratégicamente.
- **Panel de SETTINGS**:
    - **Control de Volumen**: Ajuste maestro para efectos de sonido.
    - **Temblor de Pantalla (Screen Shake)**: Opción para activar/desactivar la vibración visual.
    - **Idioma**: Soporte completo para Inglés y Español.

## [0.3.4] - 2026-05-04
### The PORTAL Update (v0.3.4 Final)
Esta versión introduce la mecánica de teletransporte dimensional y una serie de mejoras críticas en la estabilidad del motor y la interfaz de usuario.

#### Agregado (Nuevas cosas)
- **Sistema de PORTALS (Pestaña EXTRAS)**:
    - **Teletransporte Bidireccional**: Los pares de portales (AZUL/NARANJA y ROJO/VERDE) conectan puntos del campo.
    - **Aceleración Dimensional**: Cada vez que la pelota cruza un portal, su velocidad aumenta un **0.5%**.
    - **Giro de Seguridad**: Al salir de un portal, la trayectoria rota **5 grados** para evitar bucles infinitos.
    - **Sub-modificadores**:
        - **PORTAL size**: 5 niveles (Minion, Short, Default, Big, GIANT).
        - **Vertical PORTALS**: Cambia la orientación a los postes laterales para un desafío diferente.
        - **2 more PORTALS**: Añade la conexión cruzada con portales ROJO y VERDE.
- **Nuevo Poder Experimental: GHOST (FANTASMA)**:
    - Dispara 1 proyectil espectral de color blanco azulado un 50% más lento.
    - El rival debe atraparlo para hacerlo desaparecer; si cruza el fondo, suma puntos al dueño.
- **Nuevo Modificador: Add a MOUSE (Pestaña EXTRAS)**:
    - Introduce un ratón que corre por el campo de juego.
    - **Initial mouse speed**: Configurable entre varios niveles.
    - **It appears after**: Define cuántos segundos pasan antes de que el ratón entre en escena.

#### Arreglado (Bugs y Estabilidad)
- **Blindaje de Puntuación**: Eliminado el bug de puntos infinitos tras finalizar la partida.
- **Sincronización de Animaciones**: La animación de **GOLDEN GOAL** ahora termina exactamente tras 2.8s.
- **Saque Restaurado**: Reajustado el `serve_timer` a 2 segundos de cooldown real tras cada gol.
- **Memoria de Teletransporte**: Sistema de IDs (`last_portal_id`) para evitar que la pelota entre dos veces seguidas por el mismo portal.
- **Prioridad de Físicas**: Los portales se procesan antes que los rebotes de pared, garantizando colisiones precisas.

#### Cambiado (Estética y UI)
- **Tooltip Refined**: Las ayudas informativas ahora aparecen solo al pasar el ratón por el texto de los modificadores.
- **Layering Fix**: Los tooltips se dibujan siempre en la capa más alta de la interfaz.
- **Énfasis Visual**: Etiquetas de portales actualizadas a MAYÚSCULAS y con colores dinámicos (|RED|POR|GREEN|TALS).
- **Refactorización Multibola**: El motor ahora soporta múltiples proyectiles simultáneos.

## [0.3.3] - 2026-05-03
### The Celestial & Aesthetics Update (v0.3.3 Final)
Esta versión marca el cierre de la etapa de pulido visual y expansión de modificadores, introduciendo personalización de skins y una identidad única para cada cuerpo celeste.

#### Agregado (Nuevas cosas)
- **Identidad Planetaria**: Los planetas ahora tienen nombres y colores específicos (Tierra, Marte, Júpiter, Saturno).
- **Explosiones Temáticas**: Partículas de colores coordinadas con el astro destruido.
- **Sistema de Skins (Pestaña SKINS)**:
    - **Orange Power**: Skins "Default" y "Hadouken".
    - **Yellow Watch**: Skins "Default" y **"CROSS"** (Cruz Bíblica).
- **Modificador "Initial ball speed"**: 5 niveles de velocidad de saque (Low a FLASH).
- **Modificador "Ball speed increase"**: Nombres descriptivos (Low, Default, Original, Fast).

#### Arreglado (Bugs y Pulido)
- **Cura de Audio**: Buffer optimizado a 2048 y pre-inicialización.
- **Tooltips Inteligentes**: Filtrado de mensajes de ayuda por pestaña activa.
- **Independencia de Acordeones**: Los clics en "Remove a power" funcionan de forma independiente.
- **Scroll Dinámico**: Recálculo automático del desplazamiento.

## [0.3.2] - 2026-05-03
### Orbital Chaos Update
- **Modificador "Allow floating planets"**: Añade dos planetas con gravedad real.
- **Jerarquía Astronómica**: Niveles configurables (Moon, Planet, Gas Giant, Star).
- **Multiplicador X2**: Nuevo ítem de campo dorado que duplica el valor del gol.

## [0.3.1] - 2026-05-02
### Kombat Evolved
- **Pestaña "EXTRAS"**: Introducción del imán (MAGNET), reloj naranja y Golden Goal aleatorio.
- **MATCH POINT**: Regla de ganar por ventaja de 2 puntos.
- **Tooltips Informativos**: Explicaciones técnicas al pasar el ratón.

## [0.3.0] - 2026-05-02
### ¡LA GRAN ACTUALIZACIÓN KOMBAT!
- **Bola de Demolición (Naranja)**.
- **Relojes de Arena (Violeta, Amarillo, Blanco)**.
- **Panel de Modificadores con Scroll**.
