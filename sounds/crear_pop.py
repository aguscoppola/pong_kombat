import wave
import struct
import math

def crear_pop(nombre_archivo, duracion):
    tasa_muestreo = 44100
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(tasa_muestreo)
    
    # Para hacer un sonido de "POP" como una burbuja, hacemos que 
    # la frecuencia (tono) baje súper rápido, ¡como un globo desinflándose velozmente!
    for i in range(int(tasa_muestreo * duracion)):
        t = float(i) / float(tasa_muestreo)
        
        # La frecuencia arranca en 800Hz y baja súper rápido
        frecuencia_actual = 800.0 * math.exp(-25.0 * t) 
        
        # El volumen también baja rápido para que se sienta como un chasquido
        volumen = math.exp(-20.0 * t)
        
        valor = int(32767.0 * volumen * math.sin(frecuencia_actual * math.pi * t))
        archivo.writeframesraw(struct.pack('<h', valor))
    archivo.close()

# Creamos el pop de 0.1 segundos
crear_pop('pop.wav', 0.1)
