import os, re
path = 'build/web/index.html'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    btn = '<button id="infobox" style="position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); z-index:1000000; width:300px; height:150px; background-color:red; color:white; font-size:30px; font-weight:bold; border:5px solid white; border-radius:20px; cursor:pointer; pointer-events:all !important; display:block !important;" onclick="this.style.setProperty(\'display\', \'none\', \'important\');">INICIAR JUEGO</button>'
    content = re.sub(r'<div id="infobox".*?>.*?</div>', btn, content, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fix applied.")
else:
    print("File not found.")
