# Registro de Cambios (Changelog)

Aquí guardaremos una lista de todas las cosas nuevas que le vayamos agregando al juego o los errores que vayamos arreglando. Así no nos olvidamos de nada y cualquier persona que vea el proyecto sabrá en qué estuvimos trabajando.

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
