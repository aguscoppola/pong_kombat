# -*- coding: utf-8 -*-
import os

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\especificaciones.md'

new_section = """

---

## 8. Lógica de Versionado (SemVer)
El proyecto utiliza un sistema de tres dígitos `X.Y.Z` para el seguimiento del progreso:
*   **X (Lanzamiento)**: Se mantiene en `0` durante el desarrollo. Pasará a `1.0.0` en el lanzamiento oficial.
*   **Y (Adiciones Grandes)**: Se incrementa cuando se añaden múltiples poderes, relojes o sistemas de modificadores complejos (ej: de `0.2.x` a `0.3.x`).
*   **Z (Cambios Pequeños)**: Se incrementa para arreglos de bugs, optimizaciones o la implementación de una sola mejora puntual (ej: de `0.3.0` a `0.3.1`).
"""

with open(file_path, 'a', encoding='utf-8') as f:
    f.write(new_section)

print("Lógica de versionado añadida con éxito.")
