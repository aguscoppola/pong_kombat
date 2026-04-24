import wave
import struct
import random

def crear_fuego(nombre_archivo, duracion):
    tasa_muestreo = 44100
    archivo = wave.open(nombre_archivo, 'w')
    archivo.setnchannels(1)
    archivo.setsampwidth(2)
    archivo.setframerate(tasa_muestreo)
    
    # Para simular fuego, no usamos tonos puros (como en el pop o pitido),
    # usamos "Ruido Blanco" (números al azar) y lo hacemos sonar más grave.
    ultimo_valor = 0.0
    for i in range(int(tasa_muestreo * duracion)):
        # Generamos ruido aleatorio
        ruido = random.uniform(-1.0, 1.0)
        
        # Lo filtramos para cortarle los brillos (suena más a fuego/viento)
        fuego = ultimo_valor + (ruido - ultimo_valor) * 0.1
        ultimo_valor = fuego
        
        valor = int(32767.0 * fuego * 3.0) # Lo amplificamos
        
        if valor > 32767: valor = 32767
        if valor < -32768: valor = -32768
        
        archivo.writeframesraw(struct.pack('<h', valor))
    archivo.close()

# Creamos 1 segundo de fuego (luego en el juego lo ponemos en repetición infinita)
crear_fuego('fire.wav', 1.0)
