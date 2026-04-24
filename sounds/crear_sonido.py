import wave
import struct
import math

def crear_pitido(nombre_archivo, frecuencia, duracion):
    tasa_muestreo = 44100 # Calidad de CD estándar
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1) # Audio Mono
    archivo.setsampwidth(2)
    archivo.setframerate(tasa_muestreo)
    
    for i in range(int(tasa_muestreo * duracion)):
        # Fórmula matemática (seno) para crear una onda de sonido pura tipo Atari
        valor = int(32767.0 * math.sin(frecuencia * math.pi * float(i) / float(tasa_muestreo)))
        archivo.writeframesraw(struct.pack('<h', valor))
    archivo.close()
    print(f"Sonido '{nombre_archivo}' creado con éxito.")

# Creamos un pitido agudo (600 Hz) y súper cortito (0.1 segundos) para el rebote
crear_pitido('hit.wav', 600.0, 0.1)
