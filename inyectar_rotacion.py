import os

def inyectar_escudo():
    path = 'build/web/index.html'
    if not os.path.exists(path):
        print(f"Error: No se encontro {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Inyectar CSS para el aviso de rotación
    css_warning = """
    <style>
        /* Solo mostrar si está en vertical */
        @media screen and (orientation:portrait) {
            #portrait-warning { display: flex !important; }
        }
        #portrait-warning {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #0a0a0a; color: white; z-index: 9999999;
            display: none; flex-direction: column; align-items: center; justify-content: center;
            text-align: center; font-family: 'Arial', sans-serif;
        }
        .rotate-icon { font-size: 80px; margin-bottom: 20px; animation: rotate 2s infinite; }
        @keyframes rotate { 
            0% { transform: rotate(0deg); } 
            50% { transform: rotate(-90deg); } 
            100% { transform: rotate(0deg); } 
        }
        .warning-text { padding: 0 20px; }
    </style>
    """
    if '</head>' in content:
        content = content.replace('</head>', css_warning + '\n</head>')
    
    # 2. Añadir el DIV del aviso al principio del BODY
    html_warning = """
    <div id="portrait-warning">
        <div class="rotate-icon">🔄</div>
        <div class="warning-text">
            <h1 style="color: #ff3232; font-size: 2.5em;">GIRA TU CELULAR</h1>
            <p style="font-size: 1.5em; opacity: 0.8;">Pong Kombat requiere modo horizontal para jugar.</p>
        </div>
    </div>
    """
    if '<body>' in content:
        content = content.replace('<body>', '<body>\n' + html_warning)
    
    # 3. Intentar bloqueo de orientación por JS al hacer clic
    js_lock = """
    <script>
        // Intentar bloquear orientacion cuando el usuario toque la pantalla
        window.addEventListener("click", function() {
            if (screen.orientation && screen.orientation.lock) {
                screen.orientation.lock("landscape").catch(function(err) {
                    console.log("Orientacion automatica no disponible:", err);
                });
            }
        });
    </script>
    """
    if '</body>' in content:
        content = content.replace('</body>', js_lock + '\n</body>')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("¡Escudo de rotación inyectado con éxito!")

if __name__ == "__main__":
    inyectar_escudo()
