# Registro de Cambios (Changelog)

Aquí guardaremos una lista de todas las cosas nuevas que le vayamos agregando al juego o los errores que vayamos arreglando. Así no nos olvidamos de nada y cualquier persona que vea el proyecto sabrá en qué estuvimos trabajando.

## [0.3.3] - 2026-05-03
### The Celestial & Aesthetics Update (v0.3.3 Final)
Esta versión marca el cierre de la etapa de pulido visual y expansión de modificadores, introduciendo personalización de skins y una identidad única para cada cuerpo celeste.

#### Agregado (Nuevas cosas)
- **Identidad Planetaria**: Los planetas ahora tienen nombres y colores específicos (Tierra, Marte, Júpiter, Saturno).
- **Explosiones Temáticas**: Partículas de colores coordinadas con el astro destruido (Azul, Rojo, Beige, Tan, Amarillo, Gris).
- **Sistema de Skins (Pestaña SKINS)**:
    - **Orange Power**: Skins "Default" y "Hadouken".
    - **Yellow Watch**: Skins "Default" y **"CROSS"** (Cruz Bíblica de madera).
- **Modificador "Initial ball speed"**: 5 niveles de velocidad de saque (Low a FLASH).
- **Modificador "Ball speed increase"**: Nombres descriptivos (Low, Default, Original, Fast) y valores técnicos.
- **Visualización Técnica**: Los selectores muestran valores numéricos (multiplicadores, gravedad, radio) debajo de los nombres.

#### Arreglado (Bugs y Pulido)
- **Cura de Audio**: Buffer optimizado a 2048 y pre-inicialización para eliminar crujidos en Windows.
- **Tooltips Inteligentes**: Filtrado de mensajes de ayuda por pestaña activa.
- **Independencia de Acordeones**: Los clics en "Remove a power" funcionan de forma independiente.
- **Scroll Dinámico**: Recálculo automático del límite de desplazamiento al expandir secciones.
- **Iconografía Unificada**: Flechas tipo "V" dentro de cuadrados consistentes.
- **Formato Numérico**: Corrección de decimales (p. ej. "0.01" en lugar de "0.010").
- **Fijación de la Cruz**: Simetría perfecta de 10x8 píxeles para la skin de la cruz bíblica.

#### Cambiado (Estética)
- **Nombres en MAYÚSCULAS**: Colores resaltados en mayúsculas en las opciones de eliminación.
- **Feedback de Color**: Las opciones de skins cambian de color al seleccionarlas.
- **Grosor de Paletas**: Ajuste definitivo a **15px**.

## [0.3.2] - 2026-05-03
### Orbital Chaos Update
Esta versión revolucionó las físicas del juego introduciendo la interacción con cuerpos celestes y nuevas formas de puntuar.

#### Agregado (Nuevas cosas)
- **Modificador "Allow floating planets"**: Añade dos planetas que atraen la pelota con gravedad real.
- **Jerarquía Astronómica**: Niveles de gravedad y radio configurables (Moon, Planet, Gas Giant, Star).
- **Planetas Destruibles**: Los planetas ahora tienen resistencia y explotan tras recibir impactos.
- **Multiplicador X2**: Nuevo ítem de campo dorado que duplica el valor del siguiente gol anotado.
- **X2 Goal Animation**: Texto de puntuación dorado para goles con multiplicador activo.

#### Arreglado (Bugs y Estabilidad)
- **Físicas de Atracción**: Optimización de los vectores de gravedad para evitar que la pelota se quede orbitando infinitamente.
- **Spawn de Ítems**: El ícono X2 ahora respeta el área de juego y no aparece dentro de las paletas.

## [0.3.1.1] - 2026-05-02
### Inicio Potente & Hotfixes (Power Start Update)
Esta versión introduce una nueva dinámica de inicio de ronda y soluciona varios errores visuales y de lógica detectados en la 0.3.1.

#### Agregado (Nuevas cosas)
- **Modificador "Start with a Power"**: Ahora puedes elegir empezar cada ronda con un poder aleatorio ya cargado. Activado por defecto para maximizar la acción.

#### Arreglado (Bugs y Pulido)
- **Tooltips Fantasmas**: Corregido el error que permitía ver tooltips de modificadores invisibles o de otras pestañas.
- **Relojes Acelerados**: Solucionado el error de conteo doble de hits globales; ahora los relojes aparecen exactamente según la frecuencia configurada.
- **Poderes Iniciales**: Corregido el bug que otorgaba poderes al empezar la partida incluso con el modificador desactivado.

## [0.3.1] - 2026-05-02
### Kombat Evolved (Aesthetics & Stability Patch)
Esta es la versión más estable y completa hasta la fecha, introduciendo mecánicas experimentales ("EXTRAS") y un panel de control total sobre la partida.

#### Agregado (Nuevas cosas)
- **Pestaña "EXTRAS"**: Un nuevo rincón para mecánicas experimentales.
    - **Poder MAGNET (Imán)**: Atrae la pelota hacia tu paleta, permitiendo controlar la trayectoria.
    - **Reloj Naranja (Instant Chaos)**: Activa el efecto de la Pelota Gigante (Demolition) al instante.
    - **Random GOLDEN GOAL**: Añade un 10% de probabilidad de que cualquier ronda se convierta en muerte súbita.
- **MATCH POINT**: Implementada la regla de ganar por ventaja de 2 puntos para finales de infarto.
- **Tooltips Informativos**: Cada modificador ahora tiene su propia explicación técnica al pasar el ratón.
- **Nuevo Esquema de Versionado**: Adopción de SemVer (Major.Minor.Patch) para una gestión profesional del proyecto.

#### Arreglado (Bugs y Estabilidad)
- **Puntos Dobles**: Solucionado el error que sumaba dos goles en un solo impacto.
- **Sentido del Saque**: Corregido para que saque siempre quien recibió el gol.
- **Crash de Frecuencias**: Eliminados los `AttributeError` y `NameError` al cambiar ajustes en el menú.
- **Bucle de Escudo**: Los golpes con el Escudo activo ya no cuentan para el siguiente poder, evitando paletas gigantes permanentes.
- **Conflictos de Relojes**: Se congela el spawn de relojes mientras el Muro Blanco está activo.
- **Fuga de Pelota Naranja**: Añadida lógica de seguridad para detener el procesamiento tras un gol de demolición.

#### Cambiado (Estética y Balance)
- **Estética Golden Goal**: El texto de advertencia ahora brilla en color **ORO** (255, 200, 0).
- **Consolidación de Frecuencias**: 
    - Relojes: Opciones simplificadas a [3, 5, 10, 15].
    - Poderes: Opciones ajustadas a [3, 5, 7, 10, 12] (eliminado el caótico 1-tap).
- **Limpieza de UI**: Renombrado de modificadores para mayor claridad ("Power spawn frequency").
- **Ajuste de Fuentes**: Redimensionado de textos de victoria para pantallas de cualquier tamaño.

## [0.3.0] - 2026-05-02
### ¡LA GRAN ACTUALIZACIÓN KOMBAT!
Esta versión transforma el juego por completo, añadiendo profundidad táctica, una interfaz renovada y mucho más carisma.

#### Agregado (Nuevas cosas)
- **Nuevo Poder de Paleta: "Bola de Demolición" (Naranja)**. Aumenta el tamaño de la pelota al doble y su velocidad un 50%.
- **Nuevos Relojes de Arena (Mecánicas de Campo)**:
    - **Reloj Violeta**: Carga rápida de poderes (3 hits).
    - **Reloj Amarillo**: Vida Extra (Barrera trasera).
    - **Reloj Blanco**: Muro Absoluto de 5 rebotes.
- **Panel de Modificadores**: Centro de control con scroll para personalizar la partida.

## [0.2.1] - 2026-04-24
### Agregado (Nuevas cosas)
- Nuevo Poder de Paleta: "Velocista" (Amarillo).
- Sistema de Poder Acumulativo y Mecánica de "Reroll".
- Ítem de Campo: Reloj de Arena (Azul para cámara lenta, Rojo para trampa).

## [0.2.0] - 2026-04-23
### Agregado (Nuevas cosas)
- Implementación oficial del Modo Kombat.
- Sistema de Poderes (Bola de Fuego y Escudo Gigante).
- Sistema de Sonidos Generativos y organización de carpetas.

## [0.1.0] - 2026-04-23
### Agregado (Nuevas cosas)
- Estructura básica, paletas, pelota y sistema de puntuación.
