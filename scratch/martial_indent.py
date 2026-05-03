import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Función para limpiar los espacios al principio y poner exactamente 36 o 40
def fix_indent(line, indent_level):
    return ' ' * indent_level + line.lstrip()

# Localizamos el bloque y aplicamos la ley marcial de espacios
for i in range(600, 700):
    if 'elif self.watch_spawn_hits_rect' in lines[i]:
        lines[i] = fix_indent(lines[i], 36)
        lines[i+1] = fix_indent(lines[i+1], 40)
        lines[i+2] = fix_indent(lines[i+2], 40)
        lines[i+3] = fix_indent(lines[i+3], 36) # El nuevo elif de power
        lines[i+4] = fix_indent(lines[i+4], 40)
        lines[i+5] = fix_indent(lines[i+5], 40)
        break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Ley marcial de espacios aplicada. 36/40.")
