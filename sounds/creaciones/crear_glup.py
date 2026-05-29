import pygame
import math
import struct
import time
import wave  # <-- IMPORTANTE: Este módulo guarda el archivo
import os

def generate_retro_gulp():
    """Genera matemáticamente un sonido chiptune de trago"""
    sample_rate = 22050  # Frecuencia estándar retro
    num_glugs = 4        # Cantidad de "glu" en la ráfaga
    glug_duration = 0.12 # Duración de cada trago en segundos
    
    samples_per_glug = int(sample_rate * glug_duration)
    buffer = bytearray()
    
    for g in range(num_glugs):
        phase = 0.0
        for i in range(samples_per_glug):
            t = i / samples_per_glug  # Progreso (0.0 a 1.0)
            
            # Frecuencia base empieza en 140Hz y sube a 450Hz (efecto burbuja ascendente)
            freq = 140 + (310 * t)
            
            phase += (2 * math.pi * freq) / sample_rate
            
            # Onda cuadrada pura (estilo retro)
            sample = 12000 if math.sin(phase) > 0 else -12000
            
            # Suavizado al final para evitar chasquidos (pops)
            if t > 0.8:
                sample = int(sample * (1.0 - (t - 0.8) / 0.2))
                
            buffer.extend(struct.pack('<h', sample))
            
        # Micro silencio de separación entre cada "glu"
        silence_samples = int(sample_rate * 0.02)
        for _ in range(silence_samples):
            buffer.extend(struct.pack('<h', 0))
            
    return bytes(buffer)

def save_wav_file(filename, data, sample_rate):
    """Guarda los bytes crudos en un archivo .wav válido"""
    # Configuramos los parámetros del archivo WAV: Mono, 2 bytes por muestra, sample rate
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 2 bytes (16-bit signed)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)

def main():
    # Definimos la ruta de salida (asumimos que 'creaciones' está dentro de 'sounds')
    output_filename = os.path.join("..", "glup.wav")
    sample_rate = 22050
    
    print("Fabricando los bytes del sonido retro...")
    raw_audio = generate_retro_gulp()
    
    print(f"Guardando archivo en {output_filename}...")
    save_wav_file(output_filename, raw_audio, sample_rate)
    
    print("¡Archivo creado! Ahora puedes verlo en VS Code. 🍻")
    print("Reproduciendo una vez para probar...")

    # Opcional: También lo reproducimos para que lo escuches ahora
    pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
    gulp_sound = pygame.mixer.Sound(buffer=raw_audio)
    gulp_sound.play()
    time.sleep(1.5)
    pygame.mixer.quit()

if __name__ == "__main__":
    main()