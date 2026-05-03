import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Localizamos la zona problemática (alrededor de 625)
for i in range(600, 700):
    if 'elif self.power_auto_grant_hits_rect' in lines[i]:
        # Aplicamos la indentación correcta (37 espacios y 41 espacios)
        lines[i] = '                                     elif self.power_auto_grant_hits_rect.collidepoint(event.pos) or self.power_auto_grant_hits_text_rect.collidepoint(event.pos):\n'
        lines[i+1] = '                                         self.pop_sound.play()\n'
        lines[i+2] = '                                         self.power_auto_grant_hits_idx = (self.power_auto_grant_hits_idx + 1) % len(self.power_auto_grant_hits_options)\n'
        break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Indentación forzada con éxito.")
