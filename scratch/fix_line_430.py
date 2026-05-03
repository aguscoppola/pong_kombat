import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Arreglamos la línea 430 (recordando que en Python las listas son 0-indexadas, así que es la 429)
# Buscamos la línea que tiene el error de lógica en el init
for i, line in enumerate(lines):
    if 'self.power_auto_grant_hits_idx = (' in line and i < 500:
        lines[i] = '        self.power_auto_grant_hits_idx = 3 # 7 hits (Predeterminado)\n'
        break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Línea 430 corregida.")
