const CACHE_NAME = 'nba-v1';
const SHELL_ASSETS = ['index.html', 'manifest.json', 'pwa-manifest.json', 'icon-192.png'];

// Install: cache the app shell
self.addEventListener('install', e => {
    e.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(SHELL_ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Activate: clean old caches
self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

// Fetch: cache-first for images/videos, network-first for HTML/JSON
self.addEventListener('fetch', e => {
    const url = new URL(e.request.url);

    // Images and videos: cache-first (immutable content)
    if (url.pathname.match(/\.(webp|mp4|png|jpg)$/)) {
        e.respondWith(
            caches.match(e.request).then(cached => {
                if (cached) return cached;
                return fetch(e.request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // Everything else: network-first with cache fallback
    e.respondWith(
        fetch(e.request)
            .then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
                }
                return response;
            })
            .catch(() => caches.match(e.request))
    );
});

// Message handler for bulk offline download
self.addEventListener('message', e => {
    if (e.data && e.data.type === 'CACHE_ALL') {
        const urls = e.data.urls || [];
        caches.open(CACHE_NAME).then(async cache => {
            let done = 0;
            for (const url of urls) {
                try {
                    const existing = await cache.match(url);
                    if (!existing) {
                        await cache.add(url);
                    }
                    done++;
                    if (done % 50 === 0) {
                        e.source.postMessage({ type: 'CACHE_PROGRESS', done, total: urls.length });
                    }
                } catch (err) {
                    // Skip failed URLs silently
                }
            }
            e.source.postMessage({ type: 'CACHE_COMPLETE', done, total: urls.length });
        });
    }
});
