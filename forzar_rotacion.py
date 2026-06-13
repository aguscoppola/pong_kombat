import os
import re

def fuerza_bruta_orientacion():
    path = 'build/web/index.html'
    if not os.path.exists(path):
        print("No se encontró index.html")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Limpiar por completo cualquier residuo previo (CSS, JS, getters, metatags, advertencias)
    content = re.sub(r'<style>\s*/\* AVISO PREMIUM.*?></style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style>\s*/\* BLOQUEO ABSOLUTO.*?></style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<div id="portrait-warning">.*?</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*// --- FUERZA BRUTA.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*// Fuerza Bruta:.*?</script>', '', content, flags=re.DOTALL)
    
    # 2. Unificar el viewport para deshabilitar el zoom del usuario
    content = re.sub(r'<meta name="viewport" content="width=device-width, initial-scale=1.0">', '', content)
    content = re.sub(r'<meta name="viewport" content="height=device-height, initial-scale=1.0">', '', content)
    viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">'
    if '</head>' in content and viewport_meta not in content:
        content = content.replace('</head>', viewport_meta + '\n</head>')

    # 3. CSS y parches de re-orientación dinámicos
    # Se inyectan únicamente a través de JS si el usuario está en móvil.
    
    # 4. Inyectar el script de JS de Intercepción Matemática de Coordenadas 90° Rotadas,
    # el bloqueo físico de pantalla automático y el enmascaramiento ambiental absoluto 4:3
    js_lock = """
    <script>
        (function() {
            // Omitir por completo parches de movil en computadoras de escritorio
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            if (!isMobile) {
                console.log("LOG: Modo Escritorio detectado. Parches de movil desactivados.");
                return;
            }

            // Inyectar el CSS de BLOQUEO HORIZONTAL Y CENTRADO DE ASPECTO Clásico 4:3 (800x600) solo en móvil
            const style = document.createElement('style');
            style.innerHTML = `
                /* ESTILOS DE REDIMENSIONAMIENTO PREMIUM 4:3 PARA PONG KOMBAT */
                @media screen and (orientation: portrait) {
                    html, body {
                        width: 100vw !important;
                        height: 100vh !important;
                        overflow: hidden !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        background-color: #000 !important;
                    }
                    
                    /* Rotar físicamente el canvas 90 grados manteniendo relación de aspecto 4:3 perfecta */
                    canvas.emscripten {
                        position: absolute !important;
                        top: 50% !important;
                        left: 50% !important;
                        width: 100vh !important;
                        height: 75vh !important; /* 100vh * (600 / 800) = 75vh */
                        max-width: 133.33vw !important; /* 100vw * 1.333 */
                        max-height: 100vw !important;
                        transform: translate(-50%, -50%) rotate(90deg) !important;
                        transform-origin: center center !important;
                        border: 1px solid #fff !important; /* Borde sutil para delimitar el canvas */
                    }
                    
                    #transfer {
                        position: absolute !important;
                        top: 50% !important;
                        left: 50% !important;
                        transform: translate(-50%, -50%) rotate(90deg) !important;
                        width: 100vh !important;
                    }
                    
                    #infobox {
                        transform: translate(-50%, -50%) rotate(90deg) !important;
                        transform-origin: center center !important;
                        top: 50% !important;
                        left: 50% !important;
                    }
                }

                @media screen and (orientation: landscape) {
                    html, body {
                        width: 100vw !important;
                        height: 100vh !important;
                        overflow: hidden !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        background-color: #000 !important;
                    }
                    
                    /* Asegurar centrado absoluto y relación de aspecto 4:3 impecable en landscape normal */
                    canvas.emscripten {
                        width: 100vw !important;
                        height: 100vh !important;
                        max-width: 133.33vh !important; /* 100vh * 1.333 */
                        max-height: 75vw !important; /* 100vw * 0.75 */
                        object-fit: contain !important;
                        
                        position: absolute !important;
                        top: 0 !important;
                        bottom: 0 !important;
                        left: 0 !important;
                        right: 0 !important;
                        margin: auto !important;
                        padding: 0 !important;
                        transform: none !important; /* Anula transformaciones de escalado manuales de Pygbag */
                        border: 1px solid #fff !important; /* Borde sutil para delimitar el canvas */
                    }
                }

                /* PARCHE DE CONTROL DE MÁRGENES DE FULLSCREEN */
                :fullscreen, ::backdrop {
                    background-color: #000000 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }

                html:fullscreen, body:fullscreen, canvas.emscripten:fullscreen {
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                }
            `;
            document.head.appendChild(style);

        // --- 1. ENMASCARAMIENTO AMBIENTAL COMPLETO (AISLAMIENTO ABSOLUTO DEL MOTOR EN 800x600) ---
        (function() {
            // A. Buscar los descriptores nativos originales de innerWidth e innerHeight en la cadena de prototipos de window
            let proto = window;
            let descInnerWidth = null;
            let descInnerHeight = null;
            
            while (proto) {
                descInnerWidth = Object.getOwnPropertyDescriptor(proto, 'innerWidth');
                descInnerHeight = Object.getOwnPropertyDescriptor(proto, 'innerHeight');
                if (descInnerWidth && descInnerHeight) break;
                proto = Object.getPrototypeOf(proto);
            }

            if (!descInnerWidth || !descInnerHeight) {
                descInnerWidth = { get: function() { return window.visualViewport ? window.visualViewport.width : 800; } };
                descInnerHeight = { get: function() { return window.visualViewport ? window.visualViewport.height : 600; } };
            }

            // B. Virtualizar window.innerWidth e innerHeight para reportar SIEMPRE 800x600 de forma absoluta
            Object.defineProperty(window, 'innerWidth', {
                get: function() { return 800; },
                configurable: true
            });

            Object.defineProperty(window, 'innerHeight', {
                get: function() { return 600; },
                configurable: true
            });

            // C. CANDADO DE RESOLUCIÓN INTERNA DEL CANVAS (SIEMPRE 800x600 COINCIDENTE CON PYTHON)
            const originalWidth = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'width') || {
                get: function() { return this.getAttribute('width'); },
                set: function(val) { this.setAttribute('width', val); }
            };
            const originalHeight = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'height') || {
                get: function() { return this.getAttribute('height'); },
                set: function(val) { this.setAttribute('height', val); }
            };

            Object.defineProperty(HTMLCanvasElement.prototype, 'width', {
                get: function() { return 800; },
                set: function(val) { originalWidth.set.call(this, 800); },
                configurable: true
            });

            Object.defineProperty(HTMLCanvasElement.prototype, 'height', {
                get: function() { return 600; },
                set: function(val) { originalHeight.set.call(this, 600); },
                configurable: true
            });



            console.log("LOG: Aislamiento virtual absoluto 800x600 de Canvas calibrado con éxito.");
        })();

        // --- 2. BLOQUEO GLOBAL DE EVENTOS DE RESIZE PARA EL MOTOR ---
        // Evitamos que SDL2 se entere de los cambios de tamaño de ventana y recalcule la Viewport
        window.addEventListener('resize', function(e) {
            console.log("LOG: Evento resize bloqueado globalmente para el motor.");
            e.stopImmediatePropagation();
        }, true);

        // --- 3. INTERCEPCIÓN MATEMÁTICA DE COORDENADAS PARA ROTACIÓN DE 90° ---
        (function() {
            let proto = window;
            let descInnerWidth = null;
            let descInnerHeight = null;
            while (proto) {
                descInnerWidth = Object.getOwnPropertyDescriptor(proto, 'innerWidth');
                descInnerHeight = Object.getOwnPropertyDescriptor(proto, 'innerHeight');
                if (descInnerWidth && descInnerHeight) break;
                proto = Object.getPrototypeOf(proto);
            }

            // Sobrescribir getBoundingClientRect en HTMLCanvasElement
            const originalGetBoundingClientRect = HTMLCanvasElement.prototype.getBoundingClientRect;
            HTMLCanvasElement.prototype.getBoundingClientRect = function() {
                const rect = originalGetBoundingClientRect.call(this);
                // Usar visualViewport o screen para obtener dimensiones REALES, saltando el innerWidth falseado
                const realW = window.visualViewport ? window.visualViewport.width : window.screen.width;
                const realH = window.visualViewport ? window.visualViewport.height : window.screen.height;
                const isPortrait = realH > realW;
                
                if (isPortrait) {
                    const gameW = Math.min(realH, realW * 1.33333);
                    const gameH = gameW / 1.33333;
                    const left = (realH - gameW) / 2;
                    const top = (realW - gameH) / 2;
                    
                    return {
                        left: left,
                        top: top,
                        right: left + gameW,
                        bottom: top + gameH,
                        width: gameW,
                        height: gameH,
                        x: left,
                        y: top
                    };
                }
                return rect;
            };

            // Sobrescribir clientX/clientY en MouseEvent de forma ultra-segura
            const descX = Object.getOwnPropertyDescriptor(MouseEvent.prototype, 'clientX');
            const descY = Object.getOwnPropertyDescriptor(MouseEvent.prototype, 'clientY');

            if (descX && descY) {
                Object.defineProperty(MouseEvent.prototype, 'clientX', {
                    get: function() {
                        const realW = window.visualViewport ? window.visualViewport.width : window.screen.width;
                        const realH = window.visualViewport ? window.visualViewport.height : window.screen.height;
                        const isPortrait = realH > realW;
                        if (isPortrait) {
                            return descY.get.call(this);
                        }
                        return descX.get.call(this);
                    },
                    configurable: true
                });

                Object.defineProperty(MouseEvent.prototype, 'clientY', {
                    get: function() {
                        const realW = window.visualViewport ? window.visualViewport.width : window.screen.width;
                        const realH = window.visualViewport ? window.visualViewport.height : window.screen.height;
                        const isPortrait = realH > realW;
                        if (isPortrait) {
                            const realX = descX.get.call(this);
                            return realW - realX;
                        }
                        return descY.get.call(this);
                    },
                    configurable: true
                });
            }

            // Sobrescribir clientX/clientY en Touch de forma ultra-segura (solo si existe Touch en el navegador)
            if (typeof window.Touch !== 'undefined') {
                const descTouchX = Object.getOwnPropertyDescriptor(Touch.prototype, 'clientX');
                const descTouchY = Object.getOwnPropertyDescriptor(Touch.prototype, 'clientY');

                if (descTouchX && descTouchY) {
                    Object.defineProperty(Touch.prototype, 'clientX', {
                        get: function() {
                            const realW = window.visualViewport ? window.visualViewport.width : window.screen.width;
                            const realH = window.visualViewport ? window.visualViewport.height : window.screen.height;
                            const isPortrait = realH > realW;
                            if (isPortrait) {
                                return descTouchY.get.call(this);
                            }
                            return descTouchX.get.call(this);
                        },
                        configurable: true
                    });

                    Object.defineProperty(Touch.prototype, 'clientY', {
                        get: function() {
                            const realW = window.visualViewport ? window.visualViewport.width : window.screen.width;
                            const realH = window.visualViewport ? window.visualViewport.height : window.screen.height;
                            const isPortrait = realH > realW;
                            if (isPortrait) {
                                const realX = descTouchX.get.call(this);
                                return realW - realX;
                            }
                            return descTouchY.get.call(this);
                        },
                        configurable: true
                    });
                }
            }
            
            console.log("LOG: Sistema de coordenadas rotadas 90° calibrado con éxito.");
        })();

        // --- 4. FUERZA BRUTA DE BLOQUEO DE ORIENTACIÓN FÍSICA ---
        let lockAttempted = false;

        function forceLandscape() {
            // Omitir bloqueo en computadoras de escritorio para evitar conflictos de gestos
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            if (!isMobile) {
                return;
            }

            if (screen.orientation && screen.orientation.lock) {
                screen.orientation.lock("landscape").then(() => {
                    console.log("LOG: Orientación bloqueada de forma directa con éxito.");
                }).catch(e => {
                    console.log("LOG: Falló el bloqueo directo (se requiere Fullscreen):", e);
                });
            }

            let isFS = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
            if (isFS) return;

            if (lockAttempted) return;
            
            let elem = document.documentElement;
            let reqFS = elem.requestFullscreen || elem.webkitRequestFullscreen || elem.msRequestFullscreen;
            
            if (reqFS) {
                lockAttempted = true;
                reqFS.call(elem).then(() => {
                    setTimeout(() => {
                        if (screen.orientation && screen.orientation.lock) {
                            screen.orientation.lock("landscape")
                                .then(() => {
                                    console.log("LOG: Pantalla físicamente bloqueada en horizontal!");
                                    
                                    // Remover escuchadores para evitar duplicación y zooms
                                    window.removeEventListener("mousedown", forceLandscape, true);
                                    window.removeEventListener("touchstart", forceLandscape, true);
                                    
                                    triggerSizingReset();
                                })
                                .catch(e => {
                                    console.log("LOG: Falló lock de orientación, re-intentando con mayor tiempo...", e);
                                    setTimeout(() => {
                                        if (screen.orientation && screen.orientation.lock) {
                                            screen.orientation.lock("landscape").catch(err => console.log("Final lock fail:", err));
                                        }
                                    }, 200);
                                    lockAttempted = false;
                                });
                        }
                    }, 150);
                }).catch(err => {
                    console.log("LOG: Falló Fullscreen:", err);
                    lockAttempted = false;
                });
            }
        }

        // --- 5. SISTEMA DE RE-SINCRONIZACIÓN DE PANTALLA ---
        function triggerSizingReset() {
            console.log("LOG: Re-calculando dimensiones...");
            setTimeout(() => {
                if (window.window_resize) window.window_resize();
                window.dispatchEvent(new Event('resize'));
            }, 50);
            setTimeout(() => {
                if (window.window_resize) window.window_resize();
                window.dispatchEvent(new Event('resize'));
            }, 250);
        }

        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === 'visible') {
                lockAttempted = false;
                window.addEventListener("mousedown", forceLandscape, true);
                window.addEventListener("touchstart", forceLandscape, true);
                triggerSizingReset();
            }
        });

        window.addEventListener("blur", () => {
            lockAttempted = false;
        });

        window.addEventListener("focus", () => {
            lockAttempted = false;
            window.addEventListener("mousedown", forceLandscape, true);
            window.addEventListener("touchstart", forceLandscape, true);
            triggerSizingReset();
        });

        const fsEvents = ["fullscreenchange", "webkitfullscreenchange", "mozfullscreenchange", "MSFullscreenChange"];
        fsEvents.forEach(evt => {
            document.addEventListener(evt, () => {
                let isFS = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
                if (!isFS) {
                    lockAttempted = false;
                    window.addEventListener("mousedown", forceLandscape, true);
                    window.addEventListener("touchstart", forceLandscape, true);
                    triggerSizingReset();
                }
            });
        });

        window.addEventListener("orientationchange", () => {
            lockAttempted = false;
            triggerSizingReset();
        });

        window.addEventListener("mousedown", forceLandscape, true);
        window.addEventListener("touchstart", forceLandscape, true);
        
        window.addEventListener("load", () => {
            triggerSizingReset();
            
            // Anular completamente la función manual de redimensionamiento de Pygbag tras carga inicial
            setTimeout(() => {
                window.window_resize = function() {
                    console.log("LOG: window_resize manual anulado con éxito.");
                };
            }, 1000);
        });
        })();
    </script>
    """
    
    if '</body>' in content:
        content = content.replace('</body>', js_lock + '\n</body>')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fuerza Bruta de Rotacion e Intercepcion de Canvas 16:9 Aplicada con éxito.")

if __name__ == "__main__":
    fuerza_bruta_orientacion()
