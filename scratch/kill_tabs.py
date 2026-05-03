import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Solución radical: Expandir todas las pestañas a espacios (4)
new_content = content.expandtabs(4)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Todas las tabulaciones han sido convertidas a espacios.")
