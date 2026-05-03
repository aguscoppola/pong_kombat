import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Eliminamos las inyecciones fallidas (buscamos el bloque entero que inyecté)
bad_block = '''        # --- SISTEMA DE GENERACIÓN (Relojes y Poderes) ---
        self.global_hits += 1
        if self.global_hits >= self.watch_spawn_hits_options[self.watch_spawn_hits_idx]:
            self.global_hits = 0
            self.spawn_random_watch()
            
        self.global_power_hits += 1
        if self.global_power_hits >= self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]:
            self.global_power_hits = 0
            paddle.grant_random_power(self)
            self.life_sound.play()'''

# Limpiamos el archivo de este bloque invasor
content = content.replace(bad_block, "")

# También limpiamos posibles variantes con espacios distintos
content = content.replace("# --- SISTEMA DE GENERACIÓN (Relojes y Poderes) ---", "")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Inyecciones fallidas eliminadas.")
