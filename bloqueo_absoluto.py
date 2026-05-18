import os
import re

def aplicar_bloqueo_absoluto():
    path = 'build/web/index.html'
    if not os.path.exists(path):
        print("No se encontró index.html")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Limpiar intentos anteriores
    content = re.sub(r'<script>\s*// Fuerza Bruta:.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style>\s*/\* BLOQUEO ABSOLUTO.*?></style>', '', content, flags=re.DOTALL)
    
    # 2. Inyectar CSS agresivo de rotación (El "Truco del Espejo")
    css_agresivo = """
    <style>
        /* BLOQUEO ABSOLUTO: Rotar el juego si el celular está en vertical */
        @media screen and (orientation: portrait) {
            html, body {
                width: 100vw !important;
                height: 100vh !important;
                overflow: hidden !important;
                margin: 0 !important;
                padding: 0 !important;
                background-color: #000 !important;
            }
            
            /* Rotar el lienzo del juego (Canvas) 90 grados para que quede horizontal */
            canvas.emscripten {
                position: absolute !important;
                top: 50% !important;
                left: 50% !important;
                width: 100vh !important;  /* El ancho del juego ahora es el alto de la pantalla */
                height: 100vw !important; /* El alto del juego ahora es el ancho de la pantalla */
                transform: translate(-50%, -50%) rotate(90deg) !important;
                transform-origin: center center !important;
                max-width: none !important;
                max-height: none !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* También rotar las pantallas de carga para que no se vean raras */
            #transfer {
                position: absolute !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) rotate(90deg) !important;
                width: 100vh !important;
            }
            
            /* Rotar el infobox rojo gigante para que se pueda clickear */
            #infobox {
                transform: rotate(90deg) !important;
                transform-origin: center center !important;
            }
        }
    </style>
    """
    
    if '</head>' in content:
        content = content.replace('</head>', css_agresivo + '\n</head>')
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Bloqueo Absoluto (Rotación CSS) Aplicado con éxito.")

if __name__ == "__main__":
    aplicar_bloqueo_absoluto()
