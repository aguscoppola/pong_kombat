import wave
import struct
import math
import os

def create_jackpot_sound(filename):
    sample_rate = 44100
    duration = 1.5
    num_samples = int(sample_rate * duration)
    fade_out_duration = 0.5
    fade_out_samples = int(fade_out_duration * sample_rate)
    
    # Notas (frecuencias) para un arpegio alegre de Do mayor (C, E, G, C)
    notes = [523.25, 659.25, 783.99, 1046.50]
    note_duration = 0.08 # Notas muy rápidas
    
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration)
        
        # Subimos de tono en cada ciclo del arpegio para efecto Jackpot
        base_freq = notes[note_idx % len(notes)]
        multiplier = 1 + (note_idx // len(notes)) * 0.1
        freq = base_freq * multiplier
        
        # Onda cuadrada suave
        val = math.sin(2 * math.pi * freq * t)
        if val > 0: sample = 0.3
        else: sample = -0.3
        
        # 1. Envolvente de cada nota (ataque y caída rápida)
        t_in_note = t % note_duration
        note_envelope = 1.0
        fade_time = 0.01
        if t_in_note < fade_time:
            note_envelope = t_in_note / fade_time
        elif t_in_note > note_duration - fade_time:
            note_envelope = (note_duration - t_in_note) / fade_time
            
        sample *= note_envelope
        
        # 2. Fade Out Global (últimos 500ms)
        if i > num_samples - fade_out_samples:
            global_fade = (num_samples - i) / fade_out_samples
            sample *= global_fade
        
        # Convertir a 16-bit
        samples.append(int(sample * 32767))

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for s in samples:
            f.writeframes(struct.pack('<h', s))

if __name__ == "__main__":
    create_jackpot_sound("sounds/golden_goal.wav")
    print("Sonido de Jackpot con Fade Out de 500ms creado en sounds/golden_goal.wav")
