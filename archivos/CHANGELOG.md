## [0.7.2] - 2026-05-18
### The Meditation, Arcade Rework & Web Sound Update (v0.7.2)
Esta actualización rediseña por completo el Reloj Violeta con un sistema de meditación quieta, reestructura por completo el Modo Arcade con 7 niveles dinámicos con reglas específicas de puntaje (Golden Goal, Match Point, variantes climatológicas y peleas de jefe), desbloquea incondicionalmente el selector de nivel "TEST LEVEL" en el menú para facilitar las pruebas y **reactiva el sonido nativo en la versión Web Assembly para celulares y PC** con una arquitectura de insonorización segura ante excepciones.

#### Agregado (Mecánica de Meditación y Extras)
- **Audio Web Segura**:
    - Se eliminaron las restricciones estáticas de `sys.platform == "emscripten"` en el `AudioManager`.
    - Todas las llamadas del mezclador de canales de Pygame (`pygame.mixer.Sound` y `pygame.mixer.music`) ahora corren bajo bloques `try...except Exception` protectores, tolerando políticas de autoplay y restricciones de códecs de los navegadores sin crashear el motor del juego.
- **Reloj Violeta Rediseñado**:
    - Se elimina la antigua mecánica de toques (hits) para obtener poderes con el Reloj Violeta activo.
    - **Nueva mecánica de Meditación**: Si la paleta del **jugador que capturó el reloj** se mantiene **totalmente quieta durante 3 segundos** de forma voluntaria, medita y recibe un poder aleatorio directamente. El rival no se ve afectado ni recibe este beneficio.
    - **Visualización en tiempo real**: Se dibuja una barra de carga violeta pixel art sobre la paleta que indica el progreso de la meditación. Si la paleta se desplaza, la barra y el temporizador se reinician a cero de inmediato.
    - **Sonido e Impacto**: Al completarse la carga, se reproduce el sonido característico de campana (`bell`) y se emite un estallido de partículas violetas alrededor de la paleta.
- **Inteligencia Artificial (IA) Integrada**:
    *   La IA (Player 2) ahora comprende y evalúa de forma estratégica la meditación violeta en `ai_controller.py`.
    *   Toma la decisión de quedarse completamente quieta para cargar su poder cuando no hay amenazas enemigas en curso y la pelota se encuentra en la mitad contraria del campo.
    *   Bajo peligro inminente (pelota cruzando la mitad o proyectiles letales), interrumpe su meditación de forma inmediata para volver a defender el arco.
- **Tutorial Integrado**:
    - Actualización del texto descriptivo del paso 18 en el tutorial para explicar detalladamente el funcionamiento de la meditación y el temporizador de 3 segundos.
- **Selector de Nivel para Pruebas Desbloqueado**:
    - Se elimina el requisito de haber completado la campaña para ver e interactuar con el panel **TEST LEVEL** en la selección de submodos Solo.
    - Se incrementó el límite de selección a 7 niveles para permitir saltar directamente a cualquiera de los nuevos desafíos.
    - Se actualizó el tutorial integrado para reflejar la existencia de los 7 niveles.

#### Modificado (Rework y Balance del Modo Arcade)
- **Campaña de 7 Niveles**:
    - **Nivel 1 & 2**: Limitados a 1 punto bajo la regla de **GOL DE ORO** (`is_golden_goal_round`).
    - **Nivel 3**: Limitado a 1 punto base pero con **MATCH POINT** activo (se debe ganar por una ventaja de 2 puntos).
    - **Nivel 4**: Configurado a 3 puntos tanto para la variante 1 (Poderes raros) como para la variante 2 (Ratón + Clásicos).
    - **Nivel 5 (Duelo Táctico Estacionario con Planetas)**:
        - Configurado a **3 puntos** base sin Match Point.
        - Se activan **2 portales** (`portals_enabled = True`, `more_portals_enabled = False`).
        - Planetas por defecto (no destructibles, gravedad Planet, radio 180) activos en pista (`floating_planets_enabled = True`, `destructible_planets_enabled = False`).
        - Solo poderes clásicos (rojo, verde, amarillo, naranja) y **revólver** activos. El resto de poderes raros quedan desactivados.
        - Frecuencia de poder/reloj ajustada a **5 toques**.
        - Mecánica de **Los relojes se quedan** (`watches_kept_enabled = True`) activa.
        - Mecánica de **Números encapsuladores** (`encapsulate_powers_enabled = True`) activa.
    - **Nivel 6 (El Clima de la Discordia)**:
        - **Variante 1**:
            - Día Lluvioso (`rainy_day_enabled = True`) con todos sus sub-modificadores al máximo (Gota TORRENCIAL y Precipitación de 50 mm) + Relámpagos (`lightning_enabled = True`).
            - Restricción estricta de habilidades: Solo poderes Chicle, Fantasma, Sueño y Revólver al 100% de aparición.
            - Frecuencia de poder/reloj a **3 toques**. Partida al mejor de 3 (sin Match Point).
        - **Variante 2**:
            - Día Nublado (`cloudy_day_enabled = True`) con intensidad TORRENCIAL.
            - Día Lluvioso básico (10 mm, sin relámpagos).
            - Planetas por defecto (no destructibles, gravedad Planet, radio 180) activos en pista (`floating_planets_enabled = True`, `destructible_planets_enabled = False`).
            - **TODOS** los poderes clásicos y raros activos en pista.
            - Solo activado el **reloj violeta** (el resto de relojes se eliminan).
            - Frecuencia de poder/reloj a **3 toques**, partida al mejor de 3, con **2 portales** activos.
    - **Nivel 7 (Boss Final Definitivo - Rediseño Rojo Oscuro)**:
        - **TODOS los modificadores de EXTRAS activos** (exceptuando el ratón). Esto incluye planetas flotantes con gravedad, portales, multiplicador de X2, etc.
        - **4 portales** activos.
        - Planetas flotantes destructibles (`floating_planets_enabled = True`, `destructible_planets_enabled = True`).
        - Regla de **Gol de Oro experimental** (`experimental_golden_goal = True`), **Match Point** y multiplicador **X2** inicial activos en partida al mejor de 6 puntos.
        - Frecuencia de poder/reloj a **5 toques**.
        - Clima nublado y lluvioso por defecto con relámpagos activos (`lightning_enabled = True`).
        - Revólver con 100% de aparición.

## [0.7.1] - 2026-05-18
### The Rainy Kombat & Local Network Update (v0.7.1)
Esta actualización consolida la versión web y móvil del juego, solucionando todos los bloqueos de red local, agregando la espectacular ambientación y el sonido generativo de lluvia, y garantizando la compatibilidad perfecta tanto en PC de escritorio como en celulares.

#### Agregado (Clima y Sonido Generativo)
- **Sonido de Lluvia Generativo (`rainy.wav`)**:
    - Nuevo sonido ambiental de lluvia pura creado mediante algoritmos matemáticos en `crear_lluvia.py`.
    - Combinación de tres filtros de paso bajo (grave, medio y agudo) que simulan lluvia lejana, salpicaduras y brisa húmeda.
    - Aplicación de un cross-fade de 0.3 segundos para lograr un bucle (loop) 100% continuo y libre de clics.
    - Volumen balanceado en el `AudioManager` para actuar como fondo inmersivo.
- **Ambiente "RAINY DAY"**:
    - Efecto visual de lluvia torrencial sincronizado con el nuevo audio ambiental para una inmersión atmosférica total.

#### Arreglado (Compatibilidad y Red Local)
- **Interceptor de Fetch Global (Fetch Monkeypatching)**:
    - Solución definitiva al error de carga infinita ("Loading, please wait") en dispositivos móviles de red local.
    - Desvío al vuelo del archivo Pygame WASM wheel de la CDN oficial al servidor de la PC local, mientras que los índices JSON remotos continúan cargando normalmente de internet.
- **Desbloqueo Dinámico del Firewall**:
    - Comando de PowerShell automatizado con elevación de Administrador para abrir el Firewall de Windows en el puerto `8000`.
- **Corrección de Clics en PC de Escritorio**:
    - El estilo de bloqueo de pantalla y orientación vertical de 90 grados ahora se inyecta dinámicamente mediante JavaScript solo en dispositivos móviles. La PC mantiene el diseño original de Pygbag permitiendo clics perfectos en el botón "Ready to start".
- **Alineación de Puerto Pygbag**:
    - Restablecimiento del puerto del servidor a `8000` en `servidor_final.py` para sincronizar con los interceptores del motor.

## [0.7.0] - 2026-05-13
### The Mobile & Web Update (v0.7.0)
Esta actualización prepara el terreno para la expansión multiplataforma, introduciendo soporte táctil completo, un nuevo modo de juego intuitivo y compatibilidad con navegadores web.

#### Agregado (Soporte Móvil)
- **Controles Táctiles (Mobile Controls)**:
    - Botones virtuales temáticos (**ʌ**, **v**, **POW**) con diseño estilo cristal y feedback visual.
    - Soporte **Multitouch**: Permite mover ambas paletas y usar poderes simultáneamente.
    - **Botones Dinámicos**: El botón de poder se tiñe automáticamente del color de tu habilidad actual con contraste de texto inteligente.
- **Nuevo Modo: CONTROLES GEOGRÁFICOS**:
    - Sub-opción en Settings que permite desplazarse tocando directamente cualquier punto de la pantalla.
    - División de zonas: Mitad izquierda para el Jugador 1 y mitad derecha para el Jugador 2.
    - El poder se activa mediante un único botón centralizado, dejando el resto de la pantalla para el movimiento directo.
- **Despliegue Web (Web-Ready & PWA)**:
    - Compatibilidad completa con **pygbag** mediante la refactorización asíncrona del motor.
    - Soporte **PWA (Progressive Web App)**: Instalable en móviles con soporte offline.
    - **Iconografía Premium**: Nuevo icono pixel art de 512px para la pantalla de inicio.
- **Escalado Dinámico Inteligente**:
    - Implementación de `pygame.SCALED` que permite jugar en cualquier resolución manteniendo la lógica de colisiones perfecta.
- **Pulido Táctil (Touch Polish)**:
    - Botones aumentados (120x85) para mayor confort.
    - Estética **Glassmorphism** y feedback háptico (vibración) sincronizado con el gameplay.

#### Mejorado (UX y Estabilidad)
- **Unificación de Entrada**: El ratón ahora simula un "dedo virtual", permitiendo probar la experiencia móvil al 100% desde PC sin fallos de "hover" o clics fantasma.
- **Consolidación de Eventos**: Eliminación de bucles redundantes para evitar la pérdida de inputs críticos (como soltar el botón).
- **Persistencia Móvil**: El estado de los controles móviles y el modo geográfico se guardan en el perfil del jugador.

## [0.6.1] - 2026-05-12
### The Persistence & Credits Update (v0.6.1)
Esta actualización introduce la memoria permanente al juego, un panel de agradecimientos y ajustes críticos en el equilibrio de los combates.

#### Agregado (Nuevas cosas)
- **Sistema de Persistencia (Guardado/Carga)**:
    - Se guarda automáticamente el estado del tutorial (no aparece más de una vez).
    - Se guarda el progreso del modo ARCADE y la corona desbloqueada.
    - Se guardan los ajustes de volumen, idioma y efectos visuales.
    - Archivo de guardado: `save_data.json`.
- **Panel de CRÉDITOS**:
    - Acceso mediante botón "+" pixelado en la esquina del menú principal.
    - Información del autor: Agustin Martinez Coppola.
    - Soporte bilingüe completo (Español/Inglés).
- **Ajustes de MÚSICA (Settings)**:
    - Control de volumen independiente para la música.
    - Opción de activar/desactivar la música globalmente.
    - Nuevo interruptor para activar la música específicamente durante la partida.

#### Mejorado (Balance y Audio)
- **Restricción de Poderes Activos**:
    - Si tienes un poder activo (Imán, Chicle, Sueño, etc.), no recibirás uno nuevo por toques para evitar el "overpowering".
    - **Excepción**: Los poderes de contacto (ROJO y NARANJA) se siguen recibiendo normalmente.
- **Transiciones de Audio**:
    - FadeIn y FadeOut cinemáticos de 1500ms para la música en todas las transiciones del motor.
- **Lógica de GOL DE ORO**:
    - La animación y el sonido característico ahora solo se activan si el modificador está habilitado en EXTRAS.

#### Arreglado (Bugs)
- **IA: Defensa Espectral**: Corregido el bug donde la IA ignoraba las pelotas fantasmales del rival si había una real en juego.
- **IA: Letalidad**: Unificada la destrucción instantánea al contacto con proyectiles críticos (Naranja/Balas).
- **Limpieza de Estado**: Reset forzado de `max_score` al salir del modo Arcade para no contaminar partidas clásicas.

## [0.6.0] - 2026-05-11
### The Arcade & Sleep Update (v0.6.0)
Esta es la actualización más ambiciosa hasta la fecha, introduciendo un modo campaña, un nuevo sistema de combate no letal y una IA con instinto de supervivencia real.

#### Agregado (Nuevas cosas)
- **Modo ARCADE**:
    - Sistema de 5 niveles con dificultad escalonada.
    - IA nivel 5 con reflejos "Ultra-Instinto".
    - Tutorial interactivo específico para el modo Arcade (Botón rojo "?").
    - Sistema de persistencia de victoria.
- **Nuevo Poder: SLEEP (SUEÑO)**:
    - Proyectil de triple trayectoria (45 grados).
    - Efecto de inmovilización por 4 segundos.
    - Sonidos espaciales dedicados para disparo y estado "dormido".
- **Tutoriales Interactivos**:
    - **Tutorial General**: Guía paso a paso desde el menú principal para aprender modificadores y ajustes.
    - **Tutorial Arcade**: Explicación de la progresión de niveles y recompensas (Botón rojo "?").
    - **Mecánica Typewriter**: Texto palabra por palabra con efectos de sonido 'pop' sincronizados.
- **Sistema de Recompensas**:
    - **Accesorio de CORONA**: Desbloqueable permanentemente al ganar el modo Arcade.
    - Selector de corona en la pestaña SKINS para ambos jugadores.
- **IA: Evasión Táctica**:
    - Radar de balas para esquivar disparos del Revólver y bolas Naranjas.
    - Inteligencia de priorización: primero la vida, luego la pelota (a menos que el gol sea inminente).

#### Mejorado (Audio y Visual)
- **Audio Overhaul**: Nuevos sonidos de alta calidad para explosiones, victoria y poderes especiales.
- **UI Refinement**: Menú de selección de submodo Solo (Clásico vs Arcade).
- **Estética Retro**: Botones de ayuda pixelados uniformemente en todos los menús.

#### Arreglado (Bugs)
- **Física de Sueño**: Corregida la colisión instantánea al disparar el proyectil violeta.
- **Sincronización de Tutorial**: Fix en el efecto 'typewriter' que se bloqueaba en ciertas resoluciones.
- **Balance de Poderes**: Ajuste de velocidades de proyectiles para un gameplay más justo.

## [0.5.1.1] - 2026-05-09
### Physics Engine Stability & UI Polish (v0.5.1.1)
Esta es una actualización de corrección de errores (Hotfix) para estabilizar la nueva arquitectura del motor de física y pulir la experiencia de usuario.

#### Arreglado (Corrección de errores)
- **Físicas: Rebote de Paredes**: Corregido el efecto "metralleta" al sincronizar la posición flotante de la pelota tras el impacto.
- **Físicas: Movimiento de Pelota**: Restaurada la actualización de posición que dejaba la bola estática tras la refactorización.
- **Físicas: Planetas Fantasma**: Las colisiones con planetas ahora se desactivan correctamente si el modificador no está activo.
- **Mecánicas: Portales**: Restaurado el sistema de cooldown (anti-spam) e impulsos de velocidad para todos los colores de portales.
- **Mecánicas: Reloj Púrpura**: Restaurada la lógica de otorgar poderes cada 3 toques que se había perdido.
- **Mecánicas: Revólver**: Restaurada la órbita y recolección del ítem en el centro de la pista.
- **UI: Tooltips**: Sincronización completa de descripciones en Inglés/Español y filtrado por pestañas para evitar solapamientos.
- **UI: Game Over**: Corregido NameError (tw/sy) que cerraba el juego al ganar por Gol de Oro y corregido el tag |YELLOW| en los textos de victoria.
- **UI: Colores de Menú**: Añadido resaltado de color para las opciones de gravedad (MOON, STAR, etc.).

## [0.5.1] - 2026-05-08
### The Architect & Survival Update (v0.5.1)
Esta actualización marca la madurez del proyecto con una arquitectura profesional y una IA que ha aprendido a sobrevivir a los duelos de pistolas.

#### Agregado (Nuevas cosas)
- **Refactorización de Carpetas**: El proyecto ahora sigue una estructura organizada (`codigo_fuente/`, `codigo/`, `sounds/`, `archivos/`).
- **Sub-modificador: Probability of Appear (Revólver)**: Permite ajustar la frecuencia del ítem orbital en 4 niveles: Low (10%), Default (25%), Quite (50%) y Always (100%).
- **Lanzador Centralizado**: Nuevo `main.py` en la raíz que conecta dinámicamente todos los módulos distribuidos.

#### Mejorado (IA y Supervivencia)
- **IA: Esquiva de Balas**: La computadora ahora detecta proyectiles amarillos en trayectoria de colisión y los esquiva activamente.
- **IA: Táctica de Duelo**: Con el revólver, la IA prioriza defender la pelota principal antes que disparar, asegurando que no pierda el poder por un descuido.
- **Carga de Audio Profesional**: El `AudioManager` ahora usa rutas absolutas, garantizando que los sonidos se carguen sin importar la ubicación del script.

#### Arreglado (Bugs)
- **Restauración de Audio**: Corregido el error de "juego mudo" tras la reestructuración de archivos.
- **Estabilidad de Imports**: Eliminados los fallos de `ModuleNotFoundError` mediante configuración dinámica de `sys.path`.

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
