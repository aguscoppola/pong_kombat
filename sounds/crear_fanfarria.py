import wave
import struct
import math

def crear_fanfarria(nombre_archivo):
    tasa_muestreo = 44100
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(tasa_muestreo)
    
    # Notas clásicas de una "fanfarria" de victoria (Do5, Mi5, Sol5, Do6)
    # Suena muy parecido al famoso "Turututuu" de los juegos de rol.
    notas = [523.25, 659.25, 783.99, 1046.50]
    duracion_nota = 0.12 # Cada nota es cortita y rápida
    
    for frecuencia in notas:
        for i in range(int(tasa_muestreo * duracion_nota)):
            t = float(i) / float(tasa_muestreo)
            
            # Fade out rápido para que las notas no se empasten entre sí
            volumen = math.exp(-10.0 * t)
            
            # Usamos una mezcla de onda senoidal y cuadrada para que suene a "Nintendo 64" o "GameBoy"
            onda_seno = math.sin(frecuencia * math.pi * 2.0 * t)
            onda_cuadrada = 1.0 if onda_seno > 0 else -1.0
            
            # Mezclamos ambas y ponemos el volumen general en 30% para no saturar los tímpanos
            mezcla = (onda_seno + onda_cuadrada) * 0.3 * volumen
            
            valor = int(32767.0 * mezcla)
            archivo.writeframesraw(struct.pack('<h', valor))
            
    archivo.close()

# Creamos el archivo de sonido
crear_fanfarria('item_get.wav')
