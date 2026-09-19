# ⚡ Django Issue Tracker

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django 5.0](https://img.shields.io/badge/Django-5.0+-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![HTMX 1.9.12](https://img.shields.io/badge/HTMX-1.9.12-3366CC?style=flat&logo=htmx&logoColor=white)](https://htmx.org/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker & Compose](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-8%2F8%20Passed-brightgreen?style=flat&logo=pytest&logoColor=white)](#-testing--quality-assurance)

> A modern, server-rendered Kanban issue tracking application built with **Django 5**, progressively enhanced with **HTMX**, and backed by **PostgreSQL**. Engineered to function completely without JavaScript while offering seamless, instant DOM updates when JavaScript is available.

---

## 📑 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [Key Features](#-key-features)
- [Progressive Enhancement Philosophy](#-progressive-enhancement-philosophy)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Option A: Docker & Docker Compose (Recommended)](#option-a-docker--docker-compose-recommended)
  - [Option B: Local Python Environment (Quick Start / SQLite)](#option-b-local-python-environment-quick-start--sqlite)
- [Environment Variables & Configuration](#-environment-variables--configuration)
- [URL Routing & Endpoints](#-url-routing--endpoints)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Database Management & Seed Data](#-database-management--seed-data)
- [Production & Deployment Notes](#-production--deployment-notes)

---

## 🚀 Overview & Architecture

This application delivers a production-grade issue tracking workflow organized around projects, Kanban status boards, and discussion threads.

```mermaid
flowchart TD
    subgraph Client ["Client Layer"]
        Browser["Modern Web Browser"]
        HTMX["HTMX Engine (hx-post, hx-swap)"]
        NoJS["Standard HTML Forms (JS Disabled)"]
    end

    subgraph AppLayer ["Django Web Application"]
        Gunicorn["Gunicorn / WSGI"]
        Router["Django URL Dispatcher"]
        Views["tracker.views (Header Detection)"]
        Templates["Django Templates & Partials"]
    end

    subgraph Storage ["Database Layer"]
        PG[("PostgreSQL 16 (Docker/Production)")]
        SQLite[("SQLite3 (Local Dev Fallback)")]
    end

    Browser --> HTMX
    Browser --> NoJS

    HTMX -- "HX-Request: true (POST)" --> Router
    NoJS -- "Standard Form POST" --> Router

    Router --> Views
    Views --> PG
    Views --> SQLite

    Views -- "HTMX: 200 OK + HTML Partial (_issue_card / _comment)" --> HTMX
    Views -- "Standard: 302 Redirect to Board / Detail" --> NoJS
    HTMX --> Browser
    NoJS --> Browser
```

---

## ✨ Key Features

- **Interactive Kanban Boards**:
  - Visualize workflow stages: `To Do`, `In Progress`, and `Done`.
  - Column issue counters and real-time state tracking.
- **Progressive Enhancement**:
  - **With JavaScript**: Zero full-page reloads. Issue status changes and comments update in-place using lightweight HTMX fragment swaps (`_issue_card.html`, `_comment.html`).
  - **Without JavaScript**: Works 100% reliably. Standard `<form>` POST submissions return HTTP 302 redirects back to the appropriate views.
- **Detailed Issue Pages & Discussion Threads**:
  - Dedicated issue detail page (`/issues/<id>/`) with status badges and timestamps.
  - Live discussion comments with instantaneous feedback (`hx-swap="beforeend"`).
- **Automated Seeding & Mock Data**:
  - Built-in `seed_db` management command populating realistic projects, issues, and comments.
  - Automated seeding in Docker entrypoint on first run.
- **Health Checks & Monitoring**:
  - Dedicated `/health/` HTTP endpoint returning `200 OK` for container orchestrators and load balancers.
  - PostgreSQL container health check using `pg_isready`.
- **Static Assets via WhiteNoise**:
  - Efficient, production-ready static file serving without requiring an external Nginx sidecar for small-to-medium deployments.
- **Custom Modern Design System**:
  - Handcrafted CSS design system with CSS custom properties, dark-mode inspired slate aesthetics, responsive grid, and clean card layouts.

---

## 🧠 Progressive Enhancement Philosophy

In this project, client-side interactivity is **an enhancement, not a requirement**.

| Interaction | With JavaScript (HTMX Enabled) | Without JavaScript (Fallback) |
| :--- | :--- | :--- |
| **Move Issue Status** | Sends `HX-Request: true`. Server returns only the `_issue_card.html` HTML fragment (`200 OK`). Swapped smoothly into the DOM. | Browser submits standard `POST`. Server updates database and returns `302 Found` redirecting back to `/projects/<id>/`. |
| **Post Comment** | Form submits asynchronously. Server renders `_comment.html` (`200 OK`). Fragment is appended to `#comments-list` and form resets. | Standard form `POST`. Server updates database and redirects `302 Found` back to `/issues/<id>/`. |
| **Create Issue** | Clean server-side form submission with instant redirect to the board. | Identical behavior; robust against client script blockers or network drops. |

### How the Server Differentiates Requests

Django inspects the incoming request headers to determine whether to render a complete page or a partial component:

```python
def is_htmx_request(request):
    return (
        request.headers.get('HX-Request') == 'true' or
        request.META.get('HTTP_HX_REQUEST') == 'true'
    )
```

---

## 🛠 Technology Stack

- **Backend Framework**: [Django 5.0](https://www.djangoproject.com/)
- **Frontend / Interactivity**: [HTMX 1.9.12](https://htmx.org/)
- **Database**: [PostgreSQL 16](https://www.postgresql.org/) (Production/Docker) / [SQLite3](https://www.sqlite.org/) (Local Dev)
- **Database Connection Pooling**: [dj-database-url](https://pypi.org/project/dj-database-url/)
- **Database Driver**: [psycopg2-binary](https://pypi.org/project/psycopg2-binary/)
- **WSGI HTTP Server**: [Gunicorn 21.2](https://gunicorn.org/)
- **Static File Serving**: [WhiteNoise 6.6](https://whitenoise.readthedocs.io/)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

---

## 📁 Project Structure

```text
django/
├── .dockerignore                 # Excluded build artifacts for Docker
├── .env.example                  # Template configuration file
├── .gitignore                    # Git ignore rules
├── Dockerfile                    # Multi-stage production-ready Python 3.12 container
├── docker-compose.yml            # Multi-service stack (Django web + PostgreSQL)
├── entrypoint.sh                 # Container entrypoint (DB wait, migrations, seed, static)
├── manage.py                     # Django CLI utility
├── requirements.txt              # Pinned Python package dependencies
│
├── issue_tracker/                # Django Project Configuration
│   ├── __init__.py
│   ├── settings.py               # Database, WhiteNoise, and app configurations
│   ├── urls.py                   # Root URL dispatcher & /health/ route
│   └── wsgi.py                   # WSGI entrypoint for Gunicorn
│
└── tracker/                      # Issue Tracker Application
    ├── management/
    │   └── commands/
    │       └── seed_db.py        # Management command: populates sample data
    ├── migrations/
    │   └── 0001_initial.py       # Database schema migrations
    ├── static/
    │   └── tracker/css/
    │       └── styles.css        # Responsive, custom UI stylesheet
    ├── templates/
    │   └── tracker/
    │       ├── base.html         # Base layout with HTMX and typography
    │       ├── project_list.html # Grid view of all projects
    │       ├── project_board.html# Kanban board (To Do, In Progress, Done)
    │       ├── issue_detail.html # Full issue page & discussion
    │       ├── _issue_card.html  # Reusable partial for an issue card
    │       └── _comment.html     # Reusable partial for comments
    ├── forms.py                  # ModelForms for issues and comments
    ├── models.py                 # Project, Issue, and Comment models
    ├── tests/
    │   └── test_tracker.py       # Comprehensive unit & integration tests
    ├── urls.py                   # Tracker route definitions
    └── views.py                  # SSR & HTMX view handlers
```

---

## 🏁 Getting Started

You can run this project using **Docker Compose** (recommended for a full production-like environment) or natively in a **Local Python Environment**.

### Option A: Docker & Docker Compose (Recommended)

Requires [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

1. **Clone the repository and enter directory**:
   ```bash
   git clone <repository-url>
   cd django
   ```

2. **Configure environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Start the containers**:
   ```bash
   docker compose up --build
   ```
   The `entrypoint.sh` script will automatically:
   - Poll PostgreSQL until the database is accepting connections.
   - Run database migrations (`python manage.py migrate`).
   - Seed sample projects and issues (`python manage.py seed_db`).
   - Collect static files (`python manage.py collectstatic`).
   - Launch Gunicorn on `http://0.0.0.0:8000`.

4. **Access the application**:
   Open [http://localhost:8000](http://localhost:8000) in your browser.

5. **Stop containers**:
   ```bash
   docker compose down
   # Or to also wipe database volume:
   docker compose down -v
   ```

---

### Option B: Local Python Environment (Quick Start / SQLite)

If you prefer to run locally without Docker using Python and SQLite:

1. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment (Optional for SQLite)**:
   By default, if `DATABASE_URL` is not set or `USE_SQLITE=True`, the project automatically falls back to a local `db.sqlite3` database.
   ```bash
   # Optional: copy example configuration
   cp .env.example .env
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Seed the database**:
   ```bash
   python manage.py seed_db
   ```

6. **Create an administrative user (optional)**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to view your projects and Kanban board.

---

## ⚙️ Environment Variables & Configuration

Configuration is managed via environment variables (loaded through `.env` or system environment):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `django-insecure-...` | Django cryptographic secret key (Must be changed in production). |
| `DEBUG` | `True` | Enables/disables debug mode (`True`/`False`). |
| `ALLOWED_HOSTS` | `*` or `localhost,127.0.0.1,web` | Comma-separated list of host/domain names Django can serve. |
| `DATABASE_URL` | `None` | Full database connection string (e.g., `postgres://user:pass@host:5432/dbname`). |
| `USE_SQLITE` | `False` | Forces SQLite fallback (`True`/`False`) even in environments with other settings. |
| `POSTGRES_DB` | `issue_tracker` | PostgreSQL database name used by Docker Compose. |
| `POSTGRES_USER` | `postgres` | PostgreSQL username used by Docker Compose. |
| `POSTGRES_PASSWORD`| `postgres` | PostgreSQL password used by Docker Compose. |
| `POSTGRES_HOST` | `db` | Host address of PostgreSQL server. |
| `POSTGRES_PORT` | `5432` | Port of PostgreSQL server. |

---

## 🌐 URL Routing & Endpoints

| Endpoint | Method | View Function | Description |
| :--- | :---: | :--- | :--- |
| `/` | `GET` | `tracker.views.project_list` | Root landing page; redirects/renders project overview. |
| `/projects/` | `GET` | `tracker.views.project_list` | Lists all active projects and their issue statistics. |
| `/projects/<id>/` | `GET` | `tracker.views.project_board` | Interactive Kanban board with columns (`To Do`, `In Progress`, `Done`). |
| `/projects/<id>/issues/create/` | `POST`| `tracker.views.issue_create` | Creates a new issue associated with the project. |
| `/issues/<id>/` | `GET` | `tracker.views.issue_detail` | Detailed view for an issue, its status, and comments. |
| `/issues/<id>/update-status/` | `POST`| `tracker.views.update_issue_status` | Updates issue status. Returns `_issue_card.html` (HTMX) or 302 redirect. |
| `/issues/<id>/comments/add/` | `POST`| `tracker.views.add_comment` | Adds a comment. Returns `_comment.html` (HTMX) or 302 redirect. |
| `/health/` | `GET` | `issue_tracker.urls.health_check` | Uptime health check returning `200 OK`. |
| `/admin/` | `*` | `admin.site.urls` | Django administrative interface. |

---

## 🧪 Testing & Quality Assurance

The repository includes a comprehensive automated test suite testing:
1. Database schema and table constraints (`tracker_project`, `tracker_issue`, `tracker_comment`).
2. Server-Side Rendering (SSR) HTML structure and content grouping.
3. Standard form submissions and HTTP 302 redirect flows.
4. HTMX headers (`HX-Request: true`) and isolated HTML fragment responses without `<html>` or `<body>` wrappers.
5. Content integrity across status changes and discussions.

### Running Tests

Execute the Django test runner:

```bash
python manage.py test tracker
```

#### In Docker:

```bash
docker compose exec web python manage.py test tracker
```

#### Test Suite Verification Output:

```text
Found 8 test(s).
Creating test database for alias 'default'...
........
----------------------------------------------------------------------
Ran 8 tests in 0.125s

OK
Destroying test database for alias 'default'...
```

---

## 📦 Database Management & Seed Data

### Seeding Initial Data
To populate the database with demonstration projects, issues, and comments:

```bash
python manage.py seed_db
```

This generates:
- **Project 1: Alpha Platform Core** — Platform backend tasks with various statuses.
- **Project 2: Mobile Companion App** — Offline storage, biometric login, and push notification issues.
- **Project 3: Cloud Infrastructure & SRE** — Backup automation and Prometheus alerts.

### Resetting the Database
```bash
# SQLite
rm db.sqlite3
python manage.py migrate
python manage.py seed_db

# Docker PostgreSQL
docker compose down -v
docker compose up --build
```

---

## 🔒 Production & Deployment Notes

When deploying this application to production:

1. **Security**:
   - Set `DEBUG=False` in your production environment variables.
   - Configure a strong, randomly generated `SECRET_KEY`.
   - Explicitly list your production domain names in `ALLOWED_HOSTS`.
2. **Static Files**:
   - `WhiteNoise` is configured to handle static assets automatically. Run `python manage.py collectstatic --noinput` during the build phase.
3. **Database**:
   - Supply a production managed PostgreSQL connection string via `DATABASE_URL`.
   - `dj-database-url` enables persistent connection pooling (`conn_max_age=600`) and connection health checks.
4. **Process Manager**:
   - The production container runs Gunicorn:
     ```bash
     gunicorn issue_tracker.wsgi:application --bind 0.0.0.0:8000 --workers 3
     ```
   - Adjust `--workers` based on your server's available CPU cores (`(2 x CPU) + 1`).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it as needed.
