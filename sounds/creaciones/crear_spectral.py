import wave
import struct
import math
import random

# --- CONFIGURACIÓN DEL AUDIO ---
SAMPLE_RATE = 44100  # Calidad estándar de CD
DURATION = 0.85      # Duración total en segundos para que entren los dos "Fuhm"

def generate_fuhm_sound():
    audio_data = []
    phase1 = 0.0
    phase2 = 0.0

    print("Sintetizando frecuencias espectrales...")

    for i in range(int(SAMPLE_RATE * DURATION)):
        t = float(i) / SAMPLE_RATE
        sample = 0.0

        # --- PRIMER PULSO "FUHM" (0.0s a 0.35s) ---
        if 0.0 <= t < 0.35:
            local_t = t
            # Frecuencia: Cae rápido de 150Hz a 40Hz (Crea esa sensación de "agujero negro" tragando aire)
            freq = 150 - (110 * (local_t / 0.35))
            phase1 += 2 * math.pi * freq / SAMPLE_RATE
            
            # Envolvente: Sube rapidísimo (0.05s) para el impacto, y se desvanece de a poco
            if local_t < 0.05:
                env = local_t / 0.05
            else:
                env = math.exp(-(local_t - 0.05) * 10)
                
            # Ondas: Mezclamos una onda sinusoidal (grave) con ruido blanco (cenizas)
            sine = math.sin(phase1)
            noise = random.uniform(-1, 1) * 0.5 
            
            # Sumamos las ondas dándole 70% de protagonismo al bajo y 30% a la estática
            sample += (sine * 0.7 + noise * 0.3) * env

        # --- SEGUNDO PULSO "FUHM" (0.4s a 0.75s) ---
        elif 0.4 <= t < 0.75:
            local_t = t - 0.4
            # Frecuencia: Arranca un poco más grave (120Hz a 30Hz)
            freq = 120 - (90 * (local_t / 0.35))
            phase2 += 2 * math.pi * freq / SAMPLE_RATE
            
            if local_t < 0.05:
                env = local_t / 0.05
            else:
                env = math.exp(-(local_t - 0.05) * 12) # Se desvanece un poquito más rápido
                
            sine = math.sin(phase2)
            noise = random.uniform(-1, 1) * 0.4
            
            sample += (sine * 0.7 + noise * 0.3) * env

        # Evitar saturación (clipping) limitando los valores entre -1 y 1
        sample = max(-1.0, min(1.0, sample))
        
        # Convertir la muestra al formato 16-bit (el que entienden los archivos .wav)
        audio_data.append(int(sample * 32767.0))
        
    return audio_data

def save_wav(filename, data):
    print(f"Guardando el archivo mágico en: {filename}")
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 16 bits
        wav_file.setframerate(SAMPLE_RATE)
        # Empaquetamos la data de Python a bytes
        for sample in data:
            wav_file.writeframes(struct.pack('<h', sample))
    print("¡Éxito! El sonido está listo para ser usado.")

# --- EJECUCIÓN ---
if __name__ == '__main__':
    sound_data = generate_fuhm_sound()
    # Va a crear el archivo en la misma carpeta donde ejecutes este script
    save_wav('espectral.wav', sound_data)