# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run dev server
flask run
# or
python run.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_auth.py -v

# Database migrations
flask db migrate -m "descrição da mudança"
flask db upgrade

# If flask db upgrade fails, use the fallback
flask create-db

# Populate dev database with sample data
python seeds.py
```

Environment requires a `.env` file (copy from `.env.example`) with `FLASK_APP=run.py`, `FLASK_CONFIG=development`, `SECRET_KEY`, and `DATABASE_URL` (MySQL in dev/prod). Use `FLASK_CONFIG` (not `FLASK_ENV`, removed in Flask 2.3).

Production deployment uses `gunicorn` (in requirements.txt). Set `RATELIMIT_STORAGE_URI=redis://...` to enable Redis-backed rate limiting in production; omitting it uses in-memory storage (per-process, resets on restart).

## Architecture

Flask app using the **Application Factory** pattern. `create_app(config_name)` in `app/__init__.py` wires together extensions and blueprints. Extensions (db, login_manager, migrate, csrf) are instantiated in `app/extensions.py` without being bound to an app, then initialized inside `create_app()`.

**Blueprints / route modules:**
- `auth_bp` (`/auth`) — login, register, logout
- `main_bp` (`/`) — home, about
- `posts_bp` (`/posts`) — full CRUD for lost/found pet posts
- `admin_bp` (`/admin`) — admin dashboard, user and post management
- `adoption_bp` (`/adocao`) — full CRUD for adoption listings; marks pets as adopted via POST `/adocao/<id>/adotado`
- `map_bp` (`/mapa`) — partner map page + `/api/parceiros` JSON endpoint (returns active partners with coordinates)
- `api_bp` (`/api`) — thin REST helpers; currently only `/api/cep/<cep>` which proxies ViaCEP and returns a whitelisted subset (`logradouro`, `bairro`, `localidade`, `uf`)

**Models:**
- `User`, `PetPost`, `Photo` — core models; relationships: User → PetPost (one-to-many), PetPost → Photo (one-to-many, cascade delete)
- `AdoptionPost`, `AdoptionPhoto` — adoption module; same photo pattern as PetPost; AdoptionPost has `location_lat`/`location_lng` populated via geocoding after save
- `Partner` — lares temporários, petshops, and vet clinics shown on the map; has `to_dict()` for the JSON API; `partner_type` enum: `foster_home`, `petshop`, `vet_clinic`

Admin access is checked via `current_user.is_admin()` (`role == 'admin'`); admin routes use a `@admin_required` decorator defined in `app/routes/admin.py`.

**Photo uploads:** Files are saved to `app/static/uploads/` with UUID-based filenames. `save_photo()` in `app/utils/upload.py` (imported by both `posts.py` and `adoption.py`) uses Pillow to resize images to max 800px width and convert RGBA/P mode images to RGB. Maximum 5 photos per post/listing; the first photo is marked `is_primary=True`. Upload limit: 8 MB (`MAX_CONTENT_LENGTH`); allowed extensions: `png`, `jpg`, `jpeg`, `gif`, `webp`.

**Geocoding:** `app/services/geocoding.py` calls Nominatim (OpenStreetMap) server-side to convert a free-text address into `(lat, lng)`. Returns `(None, None)` on any failure — posts save normally without coordinates. Restricted to Brazil (`countrycodes=br`), 5 s timeout, 1 req/s limit per Nominatim ToS.

**Testing config** (`TestingConfig`): uses SQLite in-memory (`sqlite:///:memory:`), sets `WTF_CSRF_ENABLED=False`. Each test file sets up fixtures that call `db.create_all()` / `db.drop_all()` — no migration runner needed for tests. Tests that hit external services (e.g. ViaCEP in `test_api.py`) mock `urllib.request.urlopen` directly.

**Seeds default credentials** (after running `python seeds.py`): `admin@petpost.com` / `Admin@123`.

**Photo upload utility:** `app/utils/upload.py` — `save_photo()` runs `Image.verify()` before processing (detects non-images), enforces a 20 MP pixel limit (decompression bomb guard), and always saves a Pillow-regenerated file — the original bytes never touch disk.

**Jinja2 utilities registered in `create_app()`:**
- `{{ icon('name') }}` — inline SVG from `app/utils/icons.py` (Heroicons 2.0 outline). Accepts `size=`, `cls=`, `aria_hidden=` kwargs. Falls back to `'info'` icon if name not found.
- `{{ phone | whatsapp_url }}` — `app/utils/phone.py`; converts Brazilian phone number to `https://wa.me/...` URL. Returns `None` for 0800/invalid numbers.

**Rate limiting:** Flask-Limiter is initialized in `app/extensions.py` (in-memory storage for dev; swap `storage_uri` to `'redis://...'` in production). Limits: login 10/min · 50/hr, register 5/min · 20/hr, `/api/cep` 30/min.

**Security headers:** Flask-Talisman is activated only when `config_name == 'production'` inside `create_app()`. The CSP whitelist covers Leaflet (unpkg.com), Google Fonts, and OSM tiles. Do not enable Talisman in dev/testing — it interferes with test client redirects.

**Production config (`FLASK_CONFIG=production`):** `ProductionConfig.init_app()` raises `RuntimeError` at startup if `SECRET_KEY` or `DATABASE_URL` are missing. Cookies gain `Secure=True`. Never run production without setting these env vars.

**Security logging:** `logging.getLogger('petpost.security')` in `auth.py` records login success/failure, blocked accounts, registrations, and logouts with `user_id` + `ip`. Wire it to a file handler or syslog in production.

**Logout is POST-only** (`/auth/logout`). Templates use a `<form>` with `csrf_token()`. The test suite uses `client.post('/auth/logout', ...)`.

## Git conventions

Branch names follow `feat/`, `fix/`, `docs/` prefixes. Commit messages are written in Portuguese (e.g., `feat: adiciona modelo de adoção`). Never commit directly to `main`.
