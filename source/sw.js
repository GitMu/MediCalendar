/* MediCalendar — service worker : hors ligne, clic sur notification, réception push */
const CACHE = "medicalendar-v1";
const ASSETS = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icons/icon-192.png", "./icons/icon-512.png", "./icons/apple-touch-icon.png", "./icons/badge-96.png", "./icons/icon.svg"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put("./index.html", copy));
        return res;
      }).catch(() => caches.match("./index.html"))
    );
    return;
  }
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok && (req.url.startsWith(self.location.origin) || req.url.includes("fonts."))) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }))
  );
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  e.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      for (const c of list) if ("focus" in c) return c.focus();
      return self.clients.openWindow("./");
    })
  );
});

/* Prêt pour un serveur d'envoi Web Push : charge utile JSON { title, body, count } */
self.addEventListener("push", (e) => {
  let data = {};
  try { data = e.data ? e.data.json() : {}; } catch (err) { data = { body: e.data && e.data.text() }; }
  const title = data.title || "MediCalendar";
  const jobs = [self.registration.showNotification(title, {
    body: data.body || "Vous avez des médicaments à prendre.",
    icon: "icons/icon-192.png",
    badge: "icons/badge-96.png",
    tag: data.tag || "medicalendar"
  })];
  if (typeof data.count === "number" && self.navigator.setAppBadge) {
    jobs.push(data.count ? self.navigator.setAppBadge(data.count) : self.navigator.clearAppBadge());
  }
  e.waitUntil(Promise.all(jobs));
});
