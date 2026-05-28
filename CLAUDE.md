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
- `posts_bp` (`/posts`) — full CRUD for pet posts
- `admin_bp` (`/admin`) — admin dashboard, user and post management

**Models:** `User`, `PetPost`, `Photo`. Relationships: User → PetPost (one-to-many), PetPost → Photo (one-to-many, cascade delete). Admin access is checked via `current_user.is_admin()` (`role == 'admin'`); admin routes use a `@admin_required` decorator defined in `app/routes/admin.py`.

**Photo uploads:** Files are saved to `app/static/uploads/` with UUID-based filenames. `save_photo()` in `app/routes/posts.py` uses Pillow to resize images to max 800px width and convert RGBA/P mode images to RGB. Maximum 5 photos per post; the first photo is marked `is_primary=True`.

**Testing config** (`TestingConfig`): uses SQLite in-memory (`sqlite:///:memory:`), sets `WTF_CSRF_ENABLED=False`. Each test file sets up fixtures that call `db.create_all()` / `db.drop_all()` — no migration runner needed for tests.

## Git conventions

Branch names follow `feat/`, `fix/`, `docs/` prefixes. Commit messages are written in Portuguese (e.g., `feat: adiciona modelo de adoção`). Never commit directly to `main`.
