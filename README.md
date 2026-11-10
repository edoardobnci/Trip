# Trips

Edo's travel app (installable on iPhone via Safari → Share → Add to Home Screen).

- `index.html`, `sw.js`, `manifest.webmanifest`, icons: the app (works offline after first open).
- `data.enc`: trip data, encrypted with AES-256-GCM (key from PBKDF2-SHA256 over a passphrase). Without the passphrase it is unreadable.
- `encrypt.py`: produces `data.enc`. Updated daily by a scheduled task.
