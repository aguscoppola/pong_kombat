import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Si la línea tiene el error de indentación (espacios de más antes de power_auto_grant)
    if ' elif self.power_auto_grant_hits_rect' in line:
        new_lines.append('                                     elif self.power_auto_grant_hits_rect.collidepoint(event.pos) or self.power_auto_grant_hits_text_rect.collidepoint(event.pos):\n')
    elif '  self.pop_sound.play()' in line and 'power_auto' in new_lines[-1]:
         new_lines.append('                                         self.pop_sound.play()\n')
    elif '  self.power_auto_grant_hits_idx' in line:
         new_lines.append('                                         self.power_auto_grant_hits_idx = (self.power_auto_grant_hits_idx + 1) % len(self.power_auto_grant_hits_options)\n')
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Indochentación corregida.")
