import wave
import struct
import math
import random

# Parámetros
SAMPLE_RATE = 44100
BPM = 72 # Muy lento, estilo lobby de hotel de lujo
BEAT_DURATION = 60 / BPM
TOTAL_BEATS = 32
DURATION = BEAT_DURATION * TOTAL_BEATS

def generate_piano_note(freq, duration, volume=0.5):
    """Simula un sonido de piano eléctrico (Rhodes) usando armónicos suaves."""
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        
        # Mezcla de armónicos (Senoidales)
        # Fundamental + 2do Armónico (octava) + 0.5 (sub-octava para cuerpo)
        val = (math.sin(2 * math.pi * freq * t) * 1.0 +
               math.sin(2 * math.pi * freq * 2 * t) * 0.3 +
               math.sin(2 * math.pi * freq * 0.5 * t) * 0.2)
        
        # Envolvente Piano (Ataque rápido, decaimiento largo y suave)
        # Exponencial es mejor para instrumentos de cuerda/tecla
        decay = math.exp(-3.0 * t / duration)
        
        # Pequeño fade out al final para evitar clicks
        if i > num_samples - 1000:
            decay *= (num_samples - i) / 1000
            
        samples.append(int(val * volume * decay * 32767))
    return samples

def generate_brush_snare(duration, volume=0.05):
    """Simula un cepillo (brush) de batería usando ruido blanco suave."""
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = random.uniform(-1, 1) # Ruido blanco
        
        # Envolvente de cepillo (Ataque lento, release largo)
        env = math.exp(-10.0 * t / duration)
        samples.append(int(val * volume * env * 32767))
    return samples

def mix(tracks):
    max_len = max(len(t) for t in tracks)
    final = [0] * max_len
    for track in tracks:
        for i, val in enumerate(track):
            final[i] += val
    
    max_val = max(abs(x) for x in final) if final else 1
    if max_val > 32767:
        final = [int(x * 32767 / max_val) for x in final]
    return final

# Notas de Piano (Frecuencias)
NOTES = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77
}

# Progresión de "Hotel de Lujo": Cmaj9 - Am9 - Dm9 - G13
# Acordes extendidos para esa sensación de riqueza armónica
CHORDS = [
    ['C3', 'E4', 'G4', 'B4', 'D5'], # Cmaj9
    ['A3', 'C4', 'E4', 'G4', 'B4'], # Am9
    ['D3', 'F4', 'A4', 'C5', 'E5'], # Dm9
    ['G3', 'B3', 'F4', 'A4', 'E5']  # G13 (Simulado)
]

track_harmony = []
track_drums = []
track_bass = []

for b in range(TOTAL_BEATS):
    chord_idx = (b // 4) % len(CHORDS)
    current_chord = CHORDS[chord_idx]
    
    # Bajo (Nota profunda y suave)
    if b % 4 == 0:
        track_bass.extend(generate_piano_note(NOTES[current_chord[0]], BEAT_DURATION * 4, volume=0.15))
    
    # Armonía (Acordes de piano Rhodes en el tiempo 1 de cada compás)
    if b % 4 == 0:
        chord_samples = [0] * int(BEAT_DURATION * 4 * SAMPLE_RATE)
        for note in current_chord[1:]:
            note_samples = generate_piano_note(NOTES[note], BEAT_DURATION * 4, volume=0.06)
            for i in range(len(note_samples)):
                if i < len(chord_samples): chord_samples[i] += note_samples[i]
        track_harmony.extend(chord_samples)
    
    # Batería (Cepillo suave en los tiempos 2 y 4)
    if b % 2 == 1:
        track_drums.extend(generate_brush_snare(BEAT_DURATION, volume=0.03))
    else:
        track_drums.extend([0] * int(BEAT_DURATION * SAMPLE_RATE))

length = int(DURATION * SAMPLE_RATE)
track_harmony = track_harmony[:length]
track_bass = track_bass[:length]
track_drums = track_drums[:length]

final_mix = mix([track_harmony, track_bass, track_drums])

# Guardar WAV
with wave.open('sounds/menu_music.wav', 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE)
    for val in final_mix:
        f.writeframes(struct.pack('<h', val))

print("Música 'LUXURY HOTEL LOBBY' generada exitosamente.")
