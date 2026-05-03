import wave
import struct
import math
import random

def crear_hadouken(nombre_archivo):
    sample_rate = 44100
    duration = 1.0 
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(sample_rate)
    
    num_samples = int(sample_rate * duration)
    
    # Variables para la fase de la onda (para que sea continua)
    fase = 0.0
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # 3 Fases del grito/ataque
        if t < 0.2: # HA (Bajo y corto)
            freq = 200 + random.randint(-5, 5)
            amp = 0.5
        elif t < 0.5: # DOU (Ascendente y con cuerpo)
            freq = 300 + (t - 0.2) * 800
            amp = 0.7
        else: # KEN + BLAST (Impacto de energía)
            freq = 900 - (t - 0.5) * 400
            amp = 0.9 * math.exp(-3.0 * (t - 0.5)) # Decaimiento rápido
            
        fase += 2.0 * math.pi * freq / sample_rate
        wave_sample = math.sin(fase)
        
        # Ruido de plasma (más fuerte al final)
        noise_amp = 0.1 if t < 0.4 else 0.4
        noise = random.uniform(-1, 1) * noise_amp
        
        sample = (wave_sample * 0.7 + noise) * amp
        
        # Limitación y escritura
        value = int(max(-1, min(1, sample)) * 32767 * 0.8)
        archivo.writeframesraw(struct.pack('<h', value))
        
    archivo.close()

import os
output_path = os.path.join('..', 'hadouken.wav')
crear_hadouken(output_path)
print(f"Efecto HADOUKEN creado en: {os.path.abspath(output_path)}")
