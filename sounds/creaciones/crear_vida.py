import wave
import struct
import math
import os

sample_rate = 44100
duration = 0.8
num_samples = int(sample_rate * duration)
audio_data = [0.0] * num_samples

freqs = [440.0, 554.37, 659.25, 880.0] # A4, C#5, E5, A5

for i in range(num_samples):
    t = float(i) / sample_rate
    val = 0.0
    
    for idx, freq in enumerate(freqs):
        start_time = idx * 0.1
        if t >= start_time:
            t_note = t - start_time
            note = math.sin(2 * math.pi * freq * t_note) * 0.25
            env = math.exp(-3 * t_note)
            val += note * env
            
    audio_data[i] = val

os.makedirs('sounds', exist_ok=True)
with wave.open('sounds/vida.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for val in audio_data:
        val = max(-1.0, min(1.0, val))
        sample = int(val * 32767.0)
        wav_file.writeframesraw(struct.pack('<h', sample))

print("Sonido de vida extra generado: vida.wav")
