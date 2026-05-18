import wave
import struct
import math
import random
import os

def crear_trueno(nombre_archivo, duracion=4.0):
    tasa_muestreo = 44100
    total_frames = int(tasa_muestreo * duracion)
    
    buffer = [0.0] * total_frames
    
    # Fase inicial para osciladores de graves
    fase_boom = 0.0
    lpf_state = 0.0
    
    for i in range(total_frames):
        t = i / tasa_muestreo
        
        # --- ETAPA 1: PRE-DISPAROS (Stepped Leaders) entre 0.0s y 0.7s ("..tum..tum..tum...") ---
        if t < 0.7:
            # Generar tres pulsos secos "tum" decrecientes a los 0.15s, 0.35s y 0.55s
            beat_val = 0.0
            for tb in [0.15, 0.35, 0.55]:
                if t >= tb:
                    dt_beat = t - tb
                    # Frecuencia muy grave de 55 Hz retumbante con decaimiento rápido
                    beat_val += math.sin(2.0 * math.pi * 55.0 * dt_beat) * math.exp(-35.0 * dt_beat) * 0.35
            
            # Ruido estático de alta tensión pre-impacto esporádico (crackles)
            crackle = 0.0
            if random.random() < 0.015:
                crackle = random.uniform(-0.4, 0.4) * (t / 0.7) # Se intensifica conforme se acerca el rayo
                
            mix = beat_val + crackle
            
        # --- ETAPA 2: EL GRAN IMPACTO DIRECTO (Rayo que cae a pocos metros "¡¡¡PUUUUM!!!") ---
        else:
            t_strike = t - 0.7
            
            # 1. Crack inicial agudo del rayo rompiendo el aire (envolvente extremadamente rápida)
            impacto_crack = random.uniform(-1.0, 1.0) * math.exp(-22.0 * t_strike)
            
            # Chispas eléctricas distorsionadas que acompañan el primer medio segundo
            chispas = 0.0
            if t_strike < 0.5:
                if random.random() < 0.3:
                    chispas = random.uniform(-0.9, 0.9)
            
            # 2. El estallido de la onda expansiva sónica (PUM / Explosión de graves)
            # Un barrido descendente ultra-grave que hace temblar el suelo
            frec_boom = 75.0 - 45.0 * min(1.0, t_strike / 1.5)
            fase_boom += 2.0 * math.pi * frec_boom / tasa_muestreo
            graves_boom = math.sin(fase_boom) * 0.95 * math.exp(-1.4 * t_strike)
            
            # 3. El retumbo sónico rugiente de viento y aire ionizado (Ruido blanco de graves)
            ruido = random.uniform(-1.0, 1.0)
            cutoff = 0.03 + 0.10 * math.exp(-1.8 * t_strike)
            lpf_state = lpf_state + (ruido - lpf_state) * cutoff
            estruendo_ruido = lpf_state * 0.75 * math.exp(-0.7 * t_strike)
            
            # 4. Ondulación sísmica / Modulación de eco ondulante
            # Trémolo pronunciado para simular las reflexiones del sonido
            modulacion_eco = 1.0 + 0.55 * math.sin(2.0 * math.pi * 5.5 * t_strike) * math.exp(-0.35 * t_strike)
            
            # Mezclamos todos los elementos del gran impacto
            mix = (impacto_crack * 0.75 + chispas * 0.4 + estruendo_ruido * 0.55 + graves_boom * 0.8) * modulacion_eco
        
        # --- ETAPA 3: FADEOUT GENERAL DE 2000 ms desde t=2.0 hasta t=4.0 ---
        decay_general = 1.0
        if t > 2.0:
            fade_factor = max(0.0, 1.0 - (t - 2.0) / 2.0)
            decay_general *= fade_factor
            
        buffer[i] = mix * decay_general

    # Normalizar el audio al 92% para un sonido majestuoso, fuerte y sin distorsión
    max_val = max(abs(x) for x in buffer)
    if max_val > 0:
        scale = 0.92 / max_val
        buffer = [x * scale for x in buffer]
        
    # Guardar en archivo WAV
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
    print(f"Sonido de estruendo de trueno cercano guardado con éxito en: {nombre_archivo}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sounds_dir = os.path.dirname(script_dir)
    target_path = os.path.join(sounds_dir, "thunder.wav")
    
    crear_trueno(target_path, 4.0)
