import wave
import struct
import math
import os

def create_victory_sound(filename):
    sample_rate = 44100
    # Definimos la melodía: Frecuencia (Hz) y Duración (segundos)
    # Una fanfarria clásica: C4, G4, C5, E5, C5
    melody = [
        (261.63, 0.3), # C4
        (392.00, 0.3), # G4
        (523.25, 0.3), # C5
        (659.25, 0.3), # E5
        (523.25, 1.8)  # C5 FINAL (Sostenido)
    ]
    
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        
        for freq, dur in melody:
            num_samples = int(sample_rate * dur)
            for i in range(num_samples):
                t = i / sample_rate
                
                # Mezcla de ondas para sonido retro (Seno + algo de Cuadrada sutil)
                sine = math.sin(2.0 * math.pi * freq * t)
                square = 0.3 if math.sin(2.0 * math.pi * freq * t) > 0 else -0.3
                sample = (sine * 0.7 + square * 0.3)
                
                # Envolvente (Ataque rápido, decaimiento al final de cada nota)
                envelope = 1.0
                if i < 500: # Attack
                    envelope = i / 500
                if i > num_samples - 2000: # Release
                    envelope = (num_samples - i) / 2000
                
                value = int(sample * envelope * 32767 * 0.5)
                f.writeframesraw(struct.pack('<h', value))

if __name__ == "__main__":
    # La carpeta 'sounds' está un nivel arriba de 'creaciones'
    output_dir = os.path.join(os.getcwd(), 'sounds')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'victory_arcade.wav')
    create_victory_sound(output_path)
    print(f"Melodía de victoria creada en: {output_path}")
