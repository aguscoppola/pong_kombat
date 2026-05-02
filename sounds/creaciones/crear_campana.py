import wave
import struct
import math
import os

sample_rate = 44100
duration = 1.0
frequency = 400.0

num_samples = int(sample_rate * duration)
audio_data = []

for i in range(num_samples):
    t = float(i) / sample_rate
    # Onda principal (Campana)
    val = math.sin(2 * math.pi * frequency * t)
    # Armónico de campana 
    val += 0.3 * math.sin(2 * math.pi * frequency * 2.1 * t)
    
    # Envolvente exponencial suave (simula el golpe "Pim" y resonancia)
    envelope = math.exp(-4 * t)
    val *= envelope
    
    val = max(-1.0, min(1.0, val))
    sample = int(val * 32767.0)
    audio_data.append(sample)

os.makedirs('sounds', exist_ok=True)
with wave.open('sounds/campana.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for sample in audio_data:
        wav_file.writeframesraw(struct.pack('<h', sample))
