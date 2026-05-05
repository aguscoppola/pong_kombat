import wave
import struct
import math
import os

def create_squeak_sound(filename):
    sample_rate = 44100
    duration = 0.4
    num_samples = int(sample_rate * duration)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Un chillido de cobayo suele tener una frecuencia que sube y baja rápido (vibrato agudo)
            # Frecuencia base alta: 2000Hz
            # Modulación: pequeños pulsos agudos
            freq = 2000 + 500 * math.sin(2 * math.pi * 15 * t) 
            
            # Envolvente con pulsos (el "ui-ui-ui")
            pulse = (math.sin(2 * math.pi * 10 * t) + 1) / 2
            envelope = math.exp(-3 * t) * pulse
            
            sample = math.sin(2 * math.pi * freq * t) * envelope
            
            # Clamp y conversión
            sample = max(-1, min(1, sample))
            packed_sample = struct.pack('<h', int(sample * 32767))
            f.writeframes(packed_sample)

if __name__ == "__main__":
    create_squeak_sound("sounds/squeak.wav")
    print("Sonido SQUEAK (cobayo) creado en sounds/squeak.wav")
