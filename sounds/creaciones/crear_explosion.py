import wave
import struct
import math
import random

def crear_explosion(nombre_archivo):
    sample_rate = 44100
    duration = 1.2 
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(sample_rate)
    
    num_samples = int(sample_rate * duration)
    
    # Fase inicial para que la onda senoidal sea continua
    fase = 0.0
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # 1. Base del IMPACTO (Baja frecuencia decreciente)
        # Empieza en un tono bajo y cae a un infra-grave
        freq_start = 130
        freq_end = 40
        current_freq = freq_start - (freq_start - freq_end) * min(1.0, (i / (num_samples * 0.5)))
        
        fase += 2.0 * math.pi * current_freq / sample_rate
        pum_wave = math.sin(fase)
        
        # 2. Ruido de escombros (Ruido blanco filtrado por el fade out)
        noise = random.uniform(-1, 1)
        
        # Mezclamos: Mucho cuerpo grave al principio, ruido para el estruendo
        # Al principio el ruido es más fuerte, luego domina el grave residual
        noise_mix = 0.5 if t < 0.1 else 0.2
        sample = (pum_wave * 0.8 + noise * noise_mix)
        
        # 3. Fade Out dramático
        # Caída exponencial para un efecto natural de disipación
        decay = math.exp(-4.0 * t) 
        
        # Limitamos el valor para evitar clipping
        value = int(max(-1, min(1, sample)) * 32767 * decay * 0.8)
        archivo.writeframesraw(struct.pack('<h', value))
        
    archivo.close()

# Lo creamos directamente en la carpeta de sonidos
import os
output_path = os.path.join('..', 'explosion.wav')
crear_explosion(output_path)
print(f"Sonido creado en: {os.path.abspath(output_path)}")
