import wave
import struct
import math
import os

sample_rate = 44100
duration = 1.2
base_freq = 140.0

num_samples = int(sample_rate * duration)
audio_data = []

for i in range(num_samples):
    t = float(i) / sample_rate
    
    # Pitch modulation: Una risa que baja de tono lentamente
    freq = base_freq * (1.0 - 0.3 * (t / duration))
    
    # Tremolo: Esto crea el efecto "Ha-ha-ha" (8 veces por segundo)
    # Usamos una onda cuadrada suave para marcar los cortes de la risa
    tremolo = 0.5 + 0.5 * math.sin(2 * math.pi * 8 * t)
    if tremolo < 0.3: tremolo = 0 # Silenciamos los huecos para que suene entrecortado
    
    # Onda: Combinamos seno y un poco de sierra para darle textura "sucia"
    val = 0.7 * math.sin(2 * math.pi * freq * t) + 0.3 * (2.0 * (freq * t - math.floor(0.5 + freq * t)))
    
    # Envolvente general: Aparece y desaparece suavemente
    envelope = math.sin(math.pi * t / duration)
    
    final_val = val * tremolo * envelope
    
    # Normalizamos
    final_val = max(-1.0, min(1.0, final_val))
    sample = int(final_val * 32767.0)
    audio_data.append(sample)

# Aseguramos que la ruta existe relativa a la raíz del proyecto
os.makedirs('sounds', exist_ok=True)
with wave.open('sounds/fantasma.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    for sample in audio_data:
        wav_file.writeframesraw(struct.pack('<h', sample))

print("Sonido fantasma.wav generado con éxito.")
