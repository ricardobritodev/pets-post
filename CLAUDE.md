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

Environment requires a `.env` file (copy from `.env.example`) with `FLASK_APP=run.py`, `FLASK_ENV=development`, `SECRET_KEY`, and `DATABASE_URL` (MySQL in dev/prod).

## Architecture

Flask app using the **Application Factory** pattern. `create_app(config_name)` in `app/__init__.py` wires together extensions and blueprints. Extensions (db, login_manager, migrate, csrf) are instantiated in `app/extensions.py` without being bound to an app, then initialized inside `create_app()`.

**Blueprints / route modules:**
- `auth_bp` (`/auth`) — login, register, logout
- `main_bp` (`/`) — home, about
- `posts_bp` (`/posts`) — full CRUD for lost/found pet posts
- `admin_bp` (`/admin`) — admin dashboard, user and post management
- `adoption_bp` (`/adocao`) — full CRUD for adoption listings; marks pets as adopted via POST `/adocao/<id>/adotado`
- `map_bp` (`/mapa`) — partner map page + `/api/parceiros` JSON endpoint (returns active partners with coordinates)

**Models:**
- `User`, `PetPost`, `Photo` — core models; relationships: User → PetPost (one-to-many), PetPost → Photo (one-to-many, cascade delete)
- `AdoptionPost`, `AdoptionPhoto` — adoption module; same photo pattern as PetPost; AdoptionPost has `location_lat`/`location_lng` populated via geocoding after save
- `Partner` — lares temporários, petshops, and vet clinics shown on the map; has `to_dict()` for the JSON API; `partner_type` enum: `foster_home`, `petshop`, `vet_clinic`

Admin access is checked via `current_user.is_admin()` (`role == 'admin'`); admin routes use a `@admin_required` decorator defined in `app/routes/admin.py`.

**Photo uploads:** Files are saved to `app/static/uploads/` with UUID-based filenames. `save_photo()` (duplicated in both `app/routes/posts.py` and `app/routes/adoption.py`) uses Pillow to resize images to max 800px width and convert RGBA/P mode images to RGB. Maximum 5 photos per post/listing; the first photo is marked `is_primary=True`.

**Geocoding:** `app/services/geocoding.py` calls Nominatim (OpenStreetMap) server-side to convert a free-text address into `(lat, lng)`. Returns `(None, None)` on any failure — posts save normally without coordinates. Restricted to Brazil (`countrycodes=br`), 5 s timeout, 1 req/s limit per Nominatim ToS.

**Testing config** (`TestingConfig`): uses SQLite in-memory (`sqlite:///:memory:`), sets `WTF_CSRF_ENABLED=False`. Each test file sets up fixtures that call `db.create_all()` / `db.drop_all()` — no migration runner needed for tests.

## Git conventions

Branch names follow `feat/`, `fix/`, `docs/` prefixes. Commit messages are written in Portuguese (e.g., `feat: adiciona modelo de adoção`). Never commit directly to `main`.
