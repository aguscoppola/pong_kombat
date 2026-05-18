import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = 'build/web'

class SmartHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # 1. Redirigir peticiones de CDN local al CDN online real de Pygbag para evitar 404s
        clean_path = self.path.split('?')[0]
        if '/cdn/' in clean_path:
            local_file = os.path.join(DIRECTORY, clean_path.lstrip('/'))
            if os.path.exists(local_file):
                print(f'Radar CDN: Sirviendo {clean_path} de forma estática local')
                return super().do_GET()

            cdn_part = clean_path.split('/cdn/')[1]
            proxy_url = f'https://pygame-web.github.io/cdn/{cdn_part}'
            print(f'Radar CDN: Proxying {self.path} -> {proxy_url}')
            try:
                import urllib.request
                req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    content = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
            except Exception as e:
                print(f"Error en Proxy CDN: {e}")
                self.send_error(404, f"Proxy error: {e}")
            return

        # 2. El Radar original: Si el archivo es uno de los criticos, ignoramos la ruta loca y servimos el local
        filename = os.path.basename(clean_path)
        if filename in ['browserfs.min.js', 'pythons.js', 'vtx.js', 'vt.js']:
            print(f'Radar capturado: Sirviendo {filename} desde la raiz')
            self.path = f'/{filename}'
        return super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

WasmHandler = SmartHandler
WasmHandler.extensions_map.update({
    '.wasm': 'application/wasm',
    '.apk': 'application/octet-stream',
    '.js': 'application/javascript',
})

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f'SERVIDOR RADAR ACTIVADO EN PUERTO {PORT}')

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('', PORT), WasmHandler) as httpd:
    httpd.serve_forever()
