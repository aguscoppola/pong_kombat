import wave
import struct
import math
import random

def crear_x2(nombre_archivo):
    sample_rate = 44100
    duration = 0.6 
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(sample_rate)
    
    num_samples = int(sample_rate * duration)
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # Sonido de moneda/jackpot: dos tonos ascendentes rápidos
        if t < 0.15:
            freq = 987.77 # Si (B5)
        elif t < 0.3:
            freq = 1318.51 # Mi (E6)
        else:
            freq = 1318.51 * math.exp(-3.0 * (t - 0.3)) # Decaimiento
            
        # Vibrato brillante
        freq += math.sin(t * 100) * 10
        
        wave_val = math.sin(2.0 * math.pi * freq * t)
        
        # Envolvente
        amp = 0.8
        if t > 0.3:
            amp = 0.8 * math.exp(-4.0 * (t - 0.3))
            
        sample = wave_val * amp
        
        value = int(max(-1, min(1, sample)) * 32767 * 0.7)
        archivo.writeframesraw(struct.pack('<h', value))
        
    archivo.close()

import os
output_path = os.path.join('..', 'x2.wav')
crear_x2(output_path)
print(f"Efecto X2 (Jackpot) creado en: {os.path.abspath(output_path)}")
