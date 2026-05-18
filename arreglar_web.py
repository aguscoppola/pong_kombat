import os, re, urllib.request

build_path = 'build/web'
index_path = os.path.join(build_path, 'index.html')
bfs_path = os.path.join(build_path, 'browserfs.min.js')

# 1. Asegurar que BrowserFS esté físicamente presente
if not os.path.exists(bfs_path):
    print("Descargando BrowserFS...")
    urllib.request.urlretrieve('https://cdn.jsdelivr.net/npm/browserfs@1.4.3/dist/browserfs.min.js', bfs_path)

if os.path.exists(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Aplicando saneamiento de rutas relativas...")
    # Eliminar cualquier referencia hardcodeada a 0.0.0.0, localhost o IPs específicas
    content = re.sub(r'http://0\.0\.0\.0:8000/', './', content)
    content = re.sub(r'http://127\.0\.0\.1:8000/', './', content)
    content = re.sub(r'http://localhost:8000/', './', content)
    content = re.sub(r'http://192\.168\.\d+\.\d+:8000/', './', content)
    
    # Forzar el uso del BrowserFS local que descargamos
    content = re.sub(r'<script src=".*?browserfs\.min\.js"></script>', '<script src="browserfs.min.js"></script>', content)
    
    # 3. Copiar recursos PWA para que estén disponibles y se sirvan sin 404
    import shutil
    pwa_src = 'web_pwa'
    if os.path.exists(pwa_src):
        print("Copiando recursos PWA a build/web...")
        for item in os.listdir(pwa_src):
            s = os.path.join(pwa_src, item)
            d = os.path.join(build_path, item)
            if os.path.isfile(s) and item != 'index.html': # No sobreescribir nuestro index.html saneado
                shutil.copy2(s, d)
                print(f"  Copiado: {item}")
                
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("¡SISTEMA SANEADO! El juego ahora es independiente de la IP.")
else:
    print("Error: No se encontró index.html. Ejecuta primero 'python -m pygbag --build .'")
