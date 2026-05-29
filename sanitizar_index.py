import os
import re

def sanitizar_index():
    path = 'build/web/index.html'
    if not os.path.exists(path):
        print(f"Error: No se encontró {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Corrección de bug de plantilla Pygbag (true minúscula en bloque Python)
    content = content.replace('platform.window.transfer.hidden = true', 'platform.window.transfer.hidden = True')

    # 1. Saneamiento de BrowserFS
    content = re.sub(r'<script.*browserfs\.min\.js.*script>', '', content)
    injection = '''
    <script type="text/javascript">
        console.log("LOG: Iniciando Inyección Final de BrowserFS...");
    </script>
    <script src="browserfs.min.js"></script>
    <script type="text/javascript">
        if (window.BrowserFS) {
            console.log("LOG: BrowserFS CONFIRMADO en window.");
            window.Module = window.Module || {};
            window.Module.BrowserFS = window.BrowserFS;
        }
    </script>
    '''
    content = content.replace('</head>', injection + '\n</head>')
    content = content.replace('gui_debug : 2', 'gui_debug : 3')

    # 2. Añadir meta tag para PWA (Orientación)
    content = content.replace('</head>', '    <link rel="manifest" href="manifest.json">\n</head>')

    # 3. Robustecimiento de custom_site() de Python contra crashes de carpetas y tarfile
    # Reemplazar mkdir() por mkdir(exist_ok=True)
    content = content.replace('appdir.mkdir()', 'appdir.mkdir(exist_ok=True)')

    # Reemplazar tar.extractall con try/except
    old_tar = '''            tar = tarfile.open(fileobj=archive, mode="r:gz")
            tar.extractall(path=appdir.as_posix(), filter='tar')
            tar.close()'''
    new_tar = '''            tar = tarfile.open(fileobj=archive, mode="r:gz")
            try:
                tar.extractall(path=appdir.as_posix(), filter='tar')
            except TypeError:
                tar.extractall(path=appdir.as_posix())
            tar.close()'''
    content = content.replace(old_tar, new_tar)

    # 4. Inyectar Interceptor de Fetch Global para mapear la descarga de pygame_ce de forma local en cualquier red (móviles)
    fetch_interceptor = '''
    <script type="text/javascript">
        (function() {
            const originalFetch = window.fetch;
            window.fetch = function(input, init) {
                let url = typeof input === 'string' ? input : (input && input.url ? input.url : "");
                if (url && url.includes('pygame-web.github.io/cdn/') && url.includes('pygame_ce')) {
                    const parts = url.split('/cdn/');
                    const localUrl = window.location.origin + '/cdn/' + parts[parts.length - 1];
                    console.log('LOG [INTERCEPTOR]: Redirigiendo descarga de Pygame a servidor local:', localUrl);
                    return originalFetch(localUrl, init);
                }
                return originalFetch(input, init);
            };
            console.log("LOG: Interceptor de Fetch de Pygame cargado correctamente.");
        })();
    </script>
    '''
    content = content.replace('<head>', '<head>\n' + fetch_interceptor)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saneamiento base y robustecimiento de carga completado con éxito.")

if __name__ == "__main__":
    sanitizar_index()








