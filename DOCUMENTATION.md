# lupi-fy.com — Project Documentation

## Project Overview
- Django-based web application with real-time features (Channels) and a recommendation component.
- Key apps: `recommend` (recommendation system & ML), `games` (game views/models), `marketplace`, `core`, `communities`, plus the Django project in `mysite`.

## Quick Start
1. Create and activate a virtual environment (Python 3.11+ recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Run development server:

```bash
python manage.py runserver
```

- Alternate scripts: use `run_server.bat` or `run_server.ps1` for platform-specific helpers.

## Requirements
- See [requirements.txt](requirements.txt) for pinned and minimum dependencies. Important packages: `Django`, `channels`, `gunicorn`, and ML tooling under `recommend/`.

## Architecture (high level)
- Django project located in `mysite/` (settings, ASGI/WSGI, routing).
- Uses ASGI/Channels for websockets and real-time features (`mysite/asgi.py`, `mysite/routing.py`).
- Recommendation ML code in `recommend/ml/` (PyTorch-based recommender implementations).
- Frontend templates and static assets are in the repo root and app templates; some specialized HTML files exist (e.g., `dashboard.html`, `dash_live.html`).

## Key Files and Entry Points
- [manage.py](manage.py) — Django CLI entry point.
- [mysite/settings.py](mysite/settings.py) — main configuration.
- [mysite/asgi.py](mysite/asgi.py) — ASGI app for Channels/websockets.
- [requirements.txt](requirements.txt) — dependencies.
- [generate_essential_docs.py](generate_essential_docs.py) and [generate_complete_docs.py](generate_complete_docs.py) — repo doc generators.

## Notable Scripts
- `recommend/management/commands/` — contains recommendation training and seeding commands (e.g., `train_torch_recs`, `compute_recommendations`).
- `scripts/` — various maintenance and verification helpers (route checks, fetchers, reporters).

## Tests
- Tests are present under `tests/` and many top-level `test_*.py` files. Run with `pytest` or Django's `manage.py test` where configured.

## Existing Documentation and Guides
The repository includes many focused docs. Start with these:
- [LUPI_FY_QUICK_START.md](LUPI_FY_QUICK_START.md)
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
- [BACKEND_INTEGRATION_GUIDE.md](BACKEND_INTEGRATION_GUIDE.md)
- [CHATBOT_QUICK_START.md](CHATBOT_QUICK_START.md)
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## How I generated this file
- I scanned the repository structure, `README.md`, `requirements.txt`, and `manage.py`, and collected key locations and scripts. This is an initial top-level doc to orient contributors.

## Next steps (recommended)
1. Run `python generate_essential_docs.py` to auto-generate module-level docs (if intended by the project).
2. Add or expand docstrings in public modules to improve automatic API extraction.
3. Decide on a documentation style (MkDocs / Sphinx / plain markdown) and generate site docs from the many existing `*.md` files.

---
Generated: automatic initial documentation. For a deeper API reference, I can extract docstrings and produce per-module markdown pages next.
