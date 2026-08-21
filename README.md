# Spook

A self-contained Django + SQLite app for saving MAC addresses and sending
Wake-on-LAN "magic packets" to them from a web UI.

Tested locally: add device -> MAC validation/normalization -> duplicate
detection -> send WOL packet -> delete, all confirmed working end-to-end,
plus a production-mode run (gunicorn + whitenoise + collectstatic).

## Quick start (Docker, recommended)

```bash
cp .env.example .env   # then edit .env - at minimum set DJANGO_SECRET_KEY
docker compose up --build
```

All configurable settings (secret key, debug mode, allowed hosts, time
zone, gunicorn worker count, optional admin auto-creation) live in `.env`,
which `docker-compose.yml` reads automatically. `.env` is gitignored so
your real secret key never gets committed - `.env.example` is the
template that's safe to commit. See the "Environment variables" table
below for what each one does.

Then visit **http://localhost:4321** (on Linux, this works because of the
host networking described below; see the note if you're on Mac/Windows).

**Networking note:** Wake-on-LAN packets are sent as UDP broadcasts.
`docker-compose.yml` uses `network_mode: host` by default, which gives the
container direct access to your host's network stack so those broadcasts
reliably reach devices on your real LAN. This only works on Linux hosts —
it's not supported by Docker Desktop on Mac/Windows. If you're on Mac or
Windows, open `docker-compose.yml`, comment out `network_mode: host`, and
uncomment the `ports: - "4321:4321"` block instead; the web UI will work
normally, but Wake-on-LAN broadcasts may not reliably reach your physical
LAN in that mode.

Data (the SQLite file) persists in a named Docker volume, so it survives
`docker compose down` / `up` cycles. Use `docker compose down -v` if you
want to wipe it.

### Optional: auto-create an admin user

Uncomment and set these in `docker-compose.yml` (or pass as env vars) to get
a Django admin login (`/admin/`) created automatically on first boot:

```yaml
DJANGO_SUPERUSER_USERNAME: admin
DJANGO_SUPERUSER_PASSWORD: change-me
DJANGO_SUPERUSER_EMAIL: admin@example.com
```

## Quick start (without Docker)

```bash
python3 -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 4321
```

Then visit http://127.0.0.1:4321.

By default `DEBUG` is off; set `DJANGO_DEBUG=true` while developing locally
if you want Django's debug error pages.

## How it works

- **`devices/models.py`** — the `Device` model (name, MAC, optional IP,
  broadcast address, port, notes, last-woken timestamp/count). MAC addresses
  are normalized (e.g. `AA-BB-CC-DD-EE-FF` -> `aa:bb:cc:dd:ee:ff`) and
  validated on save, with a uniqueness constraint.
- **`devices/wol.py`** — builds and sends the WOL "magic packet" using only
  the Python standard library (`socket`), no third-party WOL package.
- **`devices/views.py`** — one page listing all devices plus an add-device
  form; POST-only "Wake" and "Remove" actions per device.
- Django admin is enabled at `/admin/` if you want an alternate way to
  manage devices.
- All fonts and styling are bundled in the image (`devices/static/`) —
  the app makes no outbound requests to any CDN at runtime.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | (dev key) | Set a real secret in production |
| `DJANGO_DEBUG` | `false` | Set `true` for Django debug pages |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated allowed hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | (empty) | Comma-separated origins, e.g. `https://wake.example.com` |
| `DJANGO_DATA_DIR` | project root | Where `db.sqlite3` is stored (Docker sets `/app/data` - not meant to be changed via `.env` since it must match the volume mount) |
| `TZ` | `UTC` | IANA time zone, e.g. `America/Indiana/Indianapolis`. Also feeds `DJANGO_TIME_ZONE` for displayed timestamps. |
| `GUNICORN_WORKERS` | `3` | Worker process count for gunicorn |
| `DJANGO_SUPERUSER_USERNAME` / `_PASSWORD` / `_EMAIL` | (empty) | Set all three (username + password required) to auto-create a Django admin user on first boot |
