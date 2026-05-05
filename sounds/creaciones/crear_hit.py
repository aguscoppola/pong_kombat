import wave
import struct
import math
import os

sample_rate = 44100
duration = 0.1  # Muy corto, un golpe seco
frequency = 150.0

num_samples = int(sample_rate * duration)
audio_data = []

for i in range(num_samples):
    t = float(i) / sample_rate
    
    # Pitch drop: El golpe baja de tono rápido
    freq = frequency * math.exp(-10 * t)
    
    # Onda: Mezclamos seno con un poco de ruido para el impacto
    import random
    noise = random.uniform(-0.2, 0.2)
    val = math.sin(2 * math.pi * freq * t) + noise
    
    # Envolvente: Ataque instantáneo y caída exponencial rápida
    envelope = math.exp(-20 * t)
    val *= envelope
    
    # Normalizamos
    val = max(-1.0, min(1.0, val))
    sample = int(val * 32767.0)
    audio_data.append(sample)

os.makedirs('sounds', exist_ok=True)
with wave.open('sounds/hit.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for sample in audio_data:
        wav_file.writeframesraw(struct.pack('<h', sample))

print("Nuevo hit.wav generado con éxito (44100Hz).")
