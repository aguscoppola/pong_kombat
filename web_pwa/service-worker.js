const CACHE_NAME = 'pong-kombat-v2';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon_192.png',
  './icon_512.png',
  './browserfs.min.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting(); // Fuerza a que el nuevo service worker se active de inmediato
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Borrando cache antiguo:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim()) // Toma control de la pestaña inmediatamente
  );
});

self.addEventListener('fetch', (event) => {
  // Estrategia Network-First: Intentar siempre descargar la versión más fresca del servidor.
  // Si no hay red, recurre al caché. Garantiza que las actualizaciones se vean al instante.
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
