import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Renombrar variables viejas a Watch Spawn
content = content.replace('self.hourglass_spawn_hits_rect', 'self.watch_spawn_hits_rect')
content = content.replace('self.hourglass_spawn_hits_text_rect', 'self.watch_spawn_hits_text_rect')
content = content.replace('self.hourglass_spawn_hits_idx', 'self.watch_spawn_hits_idx')
content = content.replace('self.hourglass_spawn_hits_options', 'self.watch_spawn_hits_options')

# 2. Añadir el clic de Auto-Power (buscamos el clic de Watch Spawn para ponerlo debajo)
old_click = 'self.watch_spawn_hits_idx = (self.watch_spawn_hits_idx + 1) % len(self.watch_spawn_hits_options)'
new_click = old_click + '\n                                     elif self.power_auto_grant_hits_rect.collidepoint(event.pos) or self.power_auto_grant_hits_text_rect.collidepoint(event.pos):\n                                         self.pop_sound.play()\n                                         self.power_auto_grant_hits_idx = (self.power_auto_grant_hits_idx + 1) % len(self.power_auto_grant_hits_options)'
content = content.replace(old_click, new_click)

# 3. Añadir la lógica de juego en paddle_hit (buscamos el final del bloque de rebote)
old_bounce = 'self.ball.x_float = float(self.ball.rect.x)'
new_logic = old_bounce + '\n        \n        # --- SISTEMA DE GENERACIÓN (Relojes y Poderes) ---\n        self.global_hits += 1\n        if self.global_hits >= self.watch_spawn_hits_options[self.watch_spawn_hits_idx]:\n            self.global_hits = 0\n            self.spawn_random_watch()\n            \n        self.global_power_hits += 1\n        if self.global_power_hits >= self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]:\n            self.global_power_hits = 0\n            paddle.grant_random_power(self)\n            self.life_sound.play()'

content = content.replace(old_bounce, new_logic)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Cambios aplicados con éxito.")
