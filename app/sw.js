// Guarda o app para abrir sem internet; os dados vêm da rede quando possível.
// Os dados (api/dados) exigem telefone liberado: só são guardados depois de uma resposta boa do servidor.
const CACHE = "radar-pl-v20";
const ARQUIVOS = ["./", "index.html", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "icons/favicon.png", "icons/qrcode.png",
  "icons/logo.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ARQUIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Resposta guardada no celular, marcada para o app saber que não foi conferida agora no servidor.
async function doCelular(req) {
  const r = await caches.match(req, { ignoreSearch: true });
  if (!r) return r;
  const h = new Headers(r.headers);
  h.set("X-Do-Celular", "1");
  return new Response(await r.blob(), { status: r.status, statusText: r.statusText, headers: h });
}

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  // Rede primeiro (dados sempre frescos), cache se estiver offline.
  e.respondWith(
    fetch(e.request)
      .then(resp => {
        if (resp.ok) {
          const copia = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, copia));
        }
        return resp;
      })
      .catch(() => doCelular(e.request))
  );
});
