# BrandLaunch

BrandLaunch is a business-focused landing page and admin panel foundation for
small businesses that need a credible online presence, lead capture, and simple
content management.

## Current Scope

This repository currently ships a presentation-first foundation slice: a runnable
Flask app, safe local configuration, SQLite schema initialization, shared Jinja
templates, a public premium landing for Nova Studio Digital, static assets,
tests, linting, and contributor setup documentation.

Admin auth, dashboard, CRUD, CSV export, analytics, email, deployment, and
backend lead capture workflows are deferred.

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

Secrets are optional for local development because the app uses safe defaults
when no `.env` file exists.

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

- `/` — public premium landing for Nova Studio Digital with a WhatsApp-first CTA
- `/admin` — admin placeholder explaining deferred auth, dashboard, and CRUD

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
- No POST handling or backend lead capture workflow
- No admin auth or dashboard implementation
- No CSV export, analytics, or email automation

## Demo Content Note

Future testimonials, leads, screenshots, and business examples must be clearly
marked as demo content. BrandLaunch must never claim real client results.
