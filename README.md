# BrandLaunch

BrandLaunch is a business-focused landing page and admin panel foundation for
small businesses that need a credible online presence, lead capture, and simple
content management.

## Current Scope

This repository currently ships a public lead-capture foundation slice plus a
single-admin protected internal lead review surface: a runnable Flask app, safe
local configuration, SQLite schema initialization, shared Jinja templates, a
public premium landing for Nova Studio Digital, same-page fallback lead capture
on `/`, an admin auth entry on `/admin/login`, a protected internal lead inbox
on `/admin`, lead detail pages on `/admin/leads/<id>`, static assets, tests,
linting, and contributor setup documentation.

Dashboard, multi-user auth, CRUD, CSV export, analytics, email, deployment,
spam protection, and broader lead operations are deferred.

## Stack

- Python + Flask
- SQLite
- Jinja2 templates
- HTML, CSS, and progressive JavaScript
- pytest for behavior checks
- ruff for linting

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

## Configuration

`.env.example` documents the local keys:

- `FLASK_ENV`
- `SECRET_KEY`
- `DATABASE_PATH`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

Secrets are optional for local development because the app uses safe defaults
when no `.env` file exists, but `/admin/login` only becomes usable after both
admin auth credentials are configured.

## Database Initialization

```bash
.venv/bin/flask --app app init-db
```

The command creates the MVP-ready SQLite tables for leads, services,
testimonials, and site settings. It is safe to run more than once.

## Run

```bash
.venv/bin/flask --app app run
```

Available routes:

- `/` — public premium landing for Nova Studio Digital with a WhatsApp-first CTA and secondary same-page contact form
- `/admin/login` — public auth surface for the single admin
- `/admin` — protected read-only internal lead inbox with summary metadata and short message excerpts
- `/admin/leads/<id>` — protected read-only lead detail page for a stored submission

## Test

```bash
.venv/bin/pytest
```

## Lint

```bash
.venv/bin/ruff check .
```

## Current Landing Boundaries

- Nova Studio Digital demo content only
- WhatsApp-first primary CTA
- Secondary same-page `POST /` fallback stores leads in SQLite after validation
- Run `.venv/bin/flask --app app init-db` before accepting submissions
- Single-admin auth protects the read-only admin review surface
- Missing credentials keep `/admin/login` in an explicit setup-needed state
- Logout uses `POST /admin/logout` and clears the current admin session
- No multi-user roles, password recovery, or audit logging
- No CSV export, analytics, or email automation
- No spam protection or export workflows

## Demo Content Note

Future testimonials, leads, screenshots, and business examples must be clearly
marked as demo content. BrandLaunch must never claim real client results.
