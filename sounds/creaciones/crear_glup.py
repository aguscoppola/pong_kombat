import pygame
import math
import struct
import time

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

def main():
    # 1. Inicializamos SOLO el mixer de audio en modo Mono (1 canal)
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
    
    print("Fabricando los bytes del sonido retro...")
    raw_audio = generate_retro_gulp()
    
    # 2. Cargamos los bytes en un objeto de sonido de Pygame
    gulp_sound = pygame.mixer.Sound(buffer=raw_audio)
    
    print("¡Reproduciendo 'glu, glu, glu, glu'! 🍻")
    gulp_sound.play()
    
    # 3. Le damos tiempo para que suene antes de que el programa termine
    time.sleep(1.0)
    
    pygame.mixer.quit()

if __name__ == "__main__":
    main()