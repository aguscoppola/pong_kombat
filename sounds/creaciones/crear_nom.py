import wave
import struct
import math
import random
import os

def create_nom_sound(filename):
    sample_rate = 44100
    duration = 0.2  # Corto y seco
    num_samples = int(sample_rate * duration)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Frecuencia descendente para el efecto "munch"
            freq = 400 * math.exp(-15 * t)
            
            # Onda base
            sample = math.sin(2 * math.pi * freq * t)
            
            # Añadir un poco de ruido para el "crunch"
            noise = (random.random() * 2 - 1) * 0.4 * math.exp(-25 * t)
            sample += noise
            
            # Envolvente
            envelope = math.exp(-12 * t)
            sample *= envelope
            
            # Clamp y conversión
            sample = max(-1, min(1, sample))
            packed_sample = struct.pack('<h', int(sample * 32767))
            f.writeframes(packed_sample)

if __name__ == "__main__":
    create_nom_sound("sounds/nom.wav")
    print("Sonido ÑOM creado en sounds/nom.wav")
