import urllib.request
import time

DOMINIO = "pongkombat"
TOKEN = "abf66dd6-6780-48ad-9988-f578415357d6" # Reemplazalo por tu código secreto de DuckDNS

print(f"Iniciando enlace con DuckDNS para el dominio: {DOMINIO}...")

while True:
    try:
        # Le pegamos a la API oficial de DuckDNS
        url = f"https://www.duckdns.org/update?domains={DOMINIO}&token={TOKEN}&ip="
        respuesta = urllib.request.urlopen(url)
        resultado = respuesta.read().decode('utf-8')
        
        if resultado == "OK":
            print("Conexión exitosa: Internet ya sabe dónde está tu servidor.")
        else:
            print("Error reportado por DuckDNS:", resultado)
            
    except Exception as e:
        print("Problema de red local:", e)
    
    # El script duerme 5 minutos (300 segundos) y vuelve a chequear
    time.sleep(300)