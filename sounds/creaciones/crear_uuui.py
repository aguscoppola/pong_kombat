import wave
import struct
import math
import os

sample_rate = 44100
duration = 0.4
start_freq = 200.0
end_freq = 1000.0

num_samples = int(sample_rate * duration)
audio_data = []

for i in range(num_samples):
    t = float(i) / sample_rate
    # Integral de la frecuencia (sweep) para obtener la fase
    phase = start_freq * t + (end_freq - start_freq) * (t**2) / (2 * duration)
    
    # Onda de sonido (Seno)
    val = math.sin(2 * math.pi * phase)
    
    # Envolvente: Volumen sube rápido y decae un poco para que suene caricaturesco
    envelope = min(1.0, t / 0.05) * math.exp(-1.5 * t)
    val *= envelope
    
    # Normalizamos
    val = max(-1.0, min(1.0, val))
    sample = int(val * 32767.0)
    audio_data.append(sample)

os.makedirs('sounds', exist_ok=True)
with wave.open('sounds/uuui.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for sample in audio_data:
        wav_file.writeframesraw(struct.pack('<h', sample))
