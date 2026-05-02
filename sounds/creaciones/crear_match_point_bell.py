import wave
import struct
import math
import os

sample_rate = 44100
duration = 1.0
frequency = 900.0 # Tono más agudo para el "Ting"

num_samples = int(sample_rate * duration)
audio_data = []

for i in range(num_samples):
    t = float(i) / sample_rate
    val = 0
    # Generamos 3 golpes rápidos (0.0s, 0.15s, 0.3s)
    for start_time in [0.0, 0.15, 0.3]:
        if t >= start_time:
            dt = t - start_time
            # Onda de campana
            ting = math.sin(2 * math.pi * frequency * dt)
            ting += 0.6 * math.sin(2 * math.pi * frequency * 2.05 * dt) # Armónico metálico
            
            # Envolvente de decaimiento muy rápido para sonar percusivo
            envelope = math.exp(-25 * dt)
            val += ting * envelope
    
    # Normalizamos para evitar distorsión
    val = max(-1.0, min(1.0, val))
    sample = int(val * 32767.0)
    audio_data.append(sample)

os.makedirs('sounds', exist_ok=True)
with wave.open('sounds/match_point_bell.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for sample in audio_data:
        wav_file.writeframesraw(struct.pack('<h', sample))
