import wave
import struct
import random
import math
import os

def crear_lluvia_pura(nombre_archivo, duracion=6.0):
    tasa_muestreo = 44100
    total_frames = int(tasa_muestreo * duracion)
    
    # Región de cross-fade para hacer el bucle 100% continuo y sin clicks (0.3 segundos)
    fade_len = int(tasa_muestreo * 0.3)
    # Generamos un buffer ligeramente más largo para aplicar el cross-fade
    generar_frames = total_frames + fade_len
    
    buffer = [0.0] * generar_frames
    
    # Inicializamos los estados de los tres filtros de paso bajo para las capas de lluvia
    y1, y2, y3 = 0.0, 0.0, 0.0
    
    # 1. Generar la textura de agua combinando 3 capas de ruido filtrado de forma ininterrumpida
    for i in range(generar_frames):
        # Capa 1: Rugido/Grave profundo (Lluvia lejana / agua golpeando el suelo)
        ruido1 = random.uniform(-1.0, 1.0)
        y1 = y1 + (ruido1 - y1) * 0.025
        mod1 = 0.8 + 0.15 * math.sin(2.0 * math.pi * 0.08 * i / tasa_muestreo)
        capa1 = y1 * mod1 * 0.35
        
        # Capa 2: Cuerpo/Medio (El salpicar de las gotas de agua)
        ruido2 = random.uniform(-1.0, 1.0)
        y2 = y2 + (ruido2 - y2) * 0.07
        mod2 = 0.75 + 0.2 * math.sin(2.0 * math.pi * 0.14 * i / tasa_muestreo)
        capa2 = y2 * mod2 * 0.50
        
        # Capa 3: Brillo/Hiss agudo (El rocío y la brisa húmeda de la lluvia)
        ruido3 = random.uniform(-1.0, 1.0)
        y3 = y3 + (ruido3 - y3) * 0.16
        mod3 = 0.85 + 0.1 * math.sin(2.0 * math.pi * 0.25 * i / tasa_muestreo)
        capa3 = y3 * mod3 * 0.15
        
        buffer[i] = capa1 + capa2 + capa3

    # 2. Aplicar Cross-Fade lineal al inicio y al final para lograr el loop perfecto y sin fisuras
    for j in range(fade_len):
        w = j / float(fade_len)
        # Mezclamos el final sobrante (N a N+C) con el inicio (0 a C)
        buffer[j] = (1.0 - w) * buffer[total_frames + j] + w * buffer[j]
        
    # Recortar el buffer para que tenga la duración exacta solicitada
    buffer = buffer[:total_frames]

    # 3. Normalizar el nivel de audio al 85% para mantener el sonido nítido y libre de distorsión
    max_val = max(abs(x) for x in buffer)
    if max_val > 0:
        scale = 0.85 / max_val
        buffer = [x * scale for x in buffer]
        
    # 4. Guardar archivo WAV
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(tasa_muestreo)
    
    for x in buffer:
        valor = int(32767.0 * x)
        if valor > 32767: valor = 32767
        if valor < -32768: valor = -32768
        archivo.writeframesraw(struct.pack('<h', valor))
        
    archivo.close()
    print(f"Sonido de lluvia pura de agua guardado con éxito en: {nombre_archivo}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sounds_dir = os.path.dirname(script_dir)
    target_path = os.path.join(sounds_dir, "rainy.wav")
    
    crear_lluvia_pura(target_path, 6.0)
