// Bump CACHE_NAME on every deploy so clients pick up the new version.
var CACHE_NAME = 'log-v1';
var STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  'https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.9/babel.min.js'
];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE_NAME).then(function(c){ return c.addAll(STATIC_ASSETS).catch(function(){}); }));
  self.skipWaiting();
});

self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(names){
    return Promise.all(names.filter(function(n){ return n!==CACHE_NAME; }).map(function(n){ return caches.delete(n); }));
  }));
  self.clients.claim();
});

self.addEventListener('fetch', function(e){
  var url = e.request.url;

  // Never cache Firebase / Google APIs — always go to network.
  if(url.indexOf('firebase')>=0 || url.indexOf('googleapis.com')>=0 ||
     url.indexOf('firestore')>=0 || url.indexOf('identitytoolkit')>=0 ||
     url.indexOf('gstatic.com')>=0){
    e.respondWith(fetch(e.request).catch(function(){ return caches.match(e.request); }));
    return;
  }

  // Network-first for the app shell (HTML) so new deploys propagate.
  if(e.request.mode==='navigate' || url.indexOf('index.html')>=0 || url.endsWith('/')){
    e.respondWith(
      fetch(e.request).then(function(resp){
        var clone = resp.clone();
        caches.open(CACHE_NAME).then(function(c){ c.put(e.request, clone); });
        return resp;
      }).catch(function(){ return caches.match(e.request).then(function(r){ return r || caches.match('./index.html'); }); })
    );
    return;
  }

  // Cache-first for everything else (static assets, fonts, libs).
  e.respondWith(
    caches.match(e.request).then(function(resp){
      return resp || fetch(e.request).then(function(r){
        if(r && r.status===200){ var cl=r.clone(); caches.open(CACHE_NAME).then(function(c){ c.put(e.request, cl); }); }
        return r;
      });
    })
  );
});
