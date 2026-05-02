import wave
import struct
import math

def crear_error(nombre_archivo):
    tasa_muestreo = 44100
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(tasa_muestreo)
    
    # "tu-ru" de error o acceso denegado (Frecuencias muy graves)
    notas = [200.0, 140.0]
    duracion_nota = 0.15 
    
    for frecuencia in notas:
        for i in range(int(tasa_muestreo * duracion_nota)):
            t = float(i) / float(tasa_muestreo)
            
            # Onda cuadrada pura para que suene bien a chicharra o "buzzer" de máquina
            onda_seno = math.sin(frecuencia * math.pi * 2.0 * t)
            onda_cuadrada = 1.0 if onda_seno > 0 else -1.0
            
            # Le bajamos el volumen un montón porque las ondas cuadradas graves suenan muy fuerte
            valor = int(32767.0 * onda_cuadrada * 0.15) 
            archivo.writeframesraw(struct.pack('<h', valor))
            
    archivo.close()

crear_error('error.wav')
