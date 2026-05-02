import wave
import struct
import math
import os

sample_rate = 44100
duration = 1.0

num_samples = int(sample_rate * duration)
audio_data = []

# Un acorde mayor (ej. Do mayor: C, E, G) para sonar angelical/poderoso
freqs = [261.63, 329.63, 392.00, 523.25] 

for i in range(num_samples):
    t = float(i) / sample_rate
    val = 0
    for f in freqs:
        val += math.sin(2 * math.pi * f * t)
    
    # Envolvente: ataque suave, decaimiento largo
    envelope = min(1.0, t / 0.1) * math.exp(-2 * t)
    val = (val / len(freqs)) * envelope
    
    val = max(-1.0, min(1.0, val))
    sample = int(val * 32767.0)
    audio_data.append(sample)

os.makedirs('sounds', exist_ok=True)
with wave.open('sounds/divino.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for sample in audio_data:
        wav_file.writeframesraw(struct.pack('<h', sample))
