import sys

file_path = r'c:\Users\agustin\Documents\workspace\pong_kombat\pong_kombat\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(620, 630):
    line = lines[i]
    prefix = line[:50]
    print(f"Linea {i+1}: '{prefix.replace(' ', 'S').replace('\t', 'T')}'")

# Solución radical: Convertir todos los inicios de línea de esa zona a espacios puros
for i in range(600, 700):
    lines[i] = lines[i].expandtabs(4)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Tabulaciones expandidas a espacios.")
