// Network-first for everything, so new versions reach the phone on the next open; cached copies serve offline.
const CACHE = "trips-v5";
const SHELL_FILES = ["./", "index.html", "manifest.webmanifest", "apple-touch-icon.png", "icon-192.png", "icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE && k !== "trips-data").map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin || e.request.method !== "GET") return;
  const isData = url.pathname.endsWith("/data.enc");
  const key = isData ? "data.enc" : e.request;
  const store = isData ? "trips-data" : CACHE;
  e.respondWith(
    fetch(e.request.url, { cache: "no-store" })
      .then((res) => {
        if (res.ok) { const copy = res.clone(); caches.open(store).then((c) => c.put(key, copy)); }
        return res;
      })
      .catch(() => caches.open(store).then((c) => c.match(key, { ignoreSearch: true })).then((hit) => hit || caches.match(e.request, { ignoreSearch: true })))
  );
});
