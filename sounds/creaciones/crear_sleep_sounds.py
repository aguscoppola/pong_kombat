import wave
import struct
import math
import os

def create_wave(filename, duration, freq_func, volume_func):
    sample_rate = 44100
    archivo = wave.open(filename, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(sample_rate)
    
    num_samples = int(sample_rate * duration)
    fase = 0.0
    
    for i in range(num_samples):
        t = i / sample_rate
        fase += 2.0 * math.pi * freq_func(t) / sample_rate
        # Mezclar con un poco de ruido para que se escuche mejor en parlantes pequeños
        import random
        noise = random.uniform(-0.1, 0.1)
        sample = math.sin(fase) * volume_func(t) + noise * volume_func(t) * 0.5
        
        value = int(max(-1, min(1, sample)) * 32767 * 0.95)
        archivo.writeframesraw(struct.pack('<h', value))
    
    archivo.close()

# 1. Sonido de DISPARO (Mas bajo y potente)
def shoot_freq(t): return 300 + 100 * math.cos(t * 40)
def shoot_vol(t): return 1.0 * (1.0 - t/0.5)

# 2. Sonido de SUEÑO (Magia / Campana mas baja)
def sleep_freq(t): return 600 + 50 * math.sin(t * 12)
def sleep_vol(t): 
    return 0.9 * (0.6 + 0.4 * math.sin(t * 8)) * (1.0 - t/1.8)

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.makedirs(output_dir, exist_ok=True)

create_wave(os.path.join(output_dir, "sleep_shoot.wav"), 0.5, shoot_freq, shoot_vol)
create_wave(os.path.join(output_dir, "sleep.wav"), 1.8, sleep_freq, sleep_vol)

print("Sonidos de sueño regenerados.")
