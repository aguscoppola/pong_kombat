import os
import subprocess
import sys

def main():
    # Asegurar salida UTF-8 en Windows si está disponible
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    print("=====================================================================")
    print(">>> INICIANDO COMPILACION DE LA VERSION WEB / CELULAR (PWA) <<<")
    print("=====================================================================\n")

    # Paso 1: pygbag --build .
    print("[1/4] Compilando Pygame a WebAssembly (Pygbag)...")
    cmd_pygbag = [sys.executable, "-m", "pygbag", "--disable-sound-format-error", "--build", "."]
    res = subprocess.run(cmd_pygbag, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if res.returncode != 0:
        print("X Error en Pygbag --build:")
        print(res.stderr)
        return
    print("-> Pygbag compilado exitosamente.\n")

    # Paso 2: arreglar_web.py
    print("[2/4] Saneando rutas relativas y recursos PWA...")
    res = subprocess.run([sys.executable, "arreglar_web.py"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(res.stdout.strip())
    if res.returncode != 0:
        print("X Error al ejecutar arreglar_web.py")
        return
    print("-> Saneamiento de rutas completado.\n")

    # Paso 3: sanitizar_index.py
    print("[3/4] Robusteciendo carga y BrowserFS...")
    res = subprocess.run([sys.executable, "sanitizar_index.py"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(res.stdout.strip())
    if res.returncode != 0:
        print("X Error al ejecutar sanitizar_index.py")
        return
    print("-> Carga y BrowserFS robustecidos.\n")

    # Paso 4: forzar_rotacion.py
    print("[4/4] Inyectando Fuerza Bruta de Rotación y Zoom-Lock...")
    res = subprocess.run([sys.executable, "forzar_rotacion.py"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(res.stdout.strip())
    if res.returncode != 0:
        print("X Error al ejecutar forzar_rotacion.py")
        return
    print("-> Fuerza bruta de rotación y mapeo de coordenadas inyectados.\n")

    print("=====================================================================")
    print(">>> PROCESO FINALIZADO CON EXITO <<<")
    print("=====================================================================")
    print(" Los archivos de la version celular estan listos en: build/web/")
    print(" Para probarla localmente en tu celular corre: python servidor_final.py")
    print("=====================================================================")

if __name__ == "__main__":
    main()
