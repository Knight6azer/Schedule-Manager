
# Schedule Manager V2

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.x-green.svg)
Schedule Manager is a Flask web application for organizing personal tasks. It supports account registration, task priorities, categories, due dates, status changes, search, and filtering, with task data stored through SQLAlchemy.

---

## 🚀 Key Features

- **Account access** — Registration and login with password hashing, server-side validation, and session-based access.
- **Per-User Task Isolation** — Every user sees only their own tasks.
- **Task management** — Create, edit, complete, and delete tasks with a title, optional description, priority, category, status, and due date.
- **Task overview** — Due dates, overdue state, task status, and priority are visible in the dashboard; task summaries update after AJAX actions.
- **Search and filters** — Filter by status, category, and priority; search task titles.
- **Responsive interface** — Mobile navigation, task list, filters, and forms adapt to narrow viewports.
- **Session security** — Unsafe form/API requests require a session CSRF token; production session cookies are HTTPS-only.
- **JSON API** — Session-authenticated task and statistics endpoints under `/api`.
- **SQLAlchemy 2.0 compatible** — Uses `db.session.get()` throughout; timezone-aware timestamps via `datetime.now(timezone.utc)`.

The database contains recurrence and notification-related fields and service methods. Recurrence creation is tied to task completion; reminder generation has no scheduler wired into this application and should not be treated as an active delivery feature.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask, Flask-SQLAlchemy 3.x (SQLAlchemy 2.0), Flask-Login |
| Database | SQLite (local) · PostgreSQL (production via `DATABASE_URL`) |
| Frontend | HTML5, Vanilla CSS (custom design system), Vanilla JS (AJAX + live filter), Jinja2 |
| Auth | Werkzeug password hashing, Flask-Login |
| Deployment | Gunicorn; Vercel configuration requires an external persistent database |

---

## 📂 Project Structure

```
Schedule Manager (Py)/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── extensions.py        # Shared extensions: db, login_manager
│   ├── models.py            # SQLAlchemy models: User, Task
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py        # /auth/login  /auth/register  /auth/logout
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py        # / (dashboard)  /add  /edit/<id>  /complete/<id>  /delete/<id>
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # JSON API: CRUD + toggle + stats + filtered list
│   ├── templates/
│   │   ├── base.html        # Sidebar app shell (auth pages use auth_content block)
│   │   ├── index.html       # Task dashboard, summary, filters, and task list
│   │   ├── login.html       # Split-panel login page
│   │   ├── register.html    # Split-panel register page
│   │   ├── task_form.html   # Create / Edit task form
│   │   └── error.html       # Safe 4xx/5xx feedback
│   └── static/
│       ├── css/style.css    # Responsive design tokens and components
│       └── js/script.js     # AJAX task actions, filters, feedback, mobile navigation
├── config.py                # Config: SECRET_KEY, DB URI, session cookie hardening
├── run.py                   # Entry point — calls create_app()
├── vercel.json              # Vercel serverless deployment config (with static asset serving)
├── Procfile                 # For Gunicorn / traditional hosting
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignores DBs, pycache, node_modules, env files
└── LICENSE                  # MIT License
```

> **Note:** `schedule_v2.db` (SQLite database) is auto-created at runtime and git-ignored.

---

## 📦 Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Knight6azer/Schedule-Manager.git
   cd "Schedule Manager (Py)"
   ```

2. **Create & activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally:**
   ```bash
   python run.py
   ```

5. **Open in browser:** `http://127.0.0.1:5000`

Direct `python run.py` startup selects development mode and binds to localhost. Production WSGI startup fails closed unless `SECRET_KEY` is set to a random value of at least 32 characters.

### Tests

Run the focused unit/integration suite and the comprehensive feature checks:

```bash
python -m unittest discover -s tests -v
python comprehensive_test.py
```

The tests use in-memory SQLite databases and do not require production credentials.

---

## 🔌 API Reference

All endpoints require an authenticated session. Mutation requests also require the session CSRF token in an `X-CSRFToken` header. Server-rendered pages expose it through a `csrf-token` meta element.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks` | List tasks (supports `?q=`, `?status=`, `?priority=`, `?category=` filters) |
| `POST` | `/api/tasks` | Create a new task |
| `PUT` | `/api/tasks/<id>` | Update an existing task (all fields) |
| `PATCH` | `/api/tasks/<id>/toggle` | Toggle status: Pending ↔ Completed |
| `DELETE` | `/api/tasks/<id>` | Delete a task |
| `GET` | `/api/stats` | Task counts grouped by status (`total`, `pending`, `in_progress`, `completed`) |

**Task JSON schema:**
```json
{
  "id": 1,
  "title": "Finish report",
  "description": "Q4 summary",
  "priority": "High",
  "category": "Work",
  "status": "In Progress",
  "due_date": "2026-03-10",
  "reminder_time": null,
  "created_at": "2026-03-02T14:00:00",
  "updated_at": "2026-03-02T14:00:00",
  "user_id": 1
}
```

**Stats JSON schema:**
```json
{
  "total": 12,
  "pending": 5,
  "in_progress": 3,
  "completed": 4
}
```

---

## Production deployment

Run behind an HTTPS-terminating reverse proxy using Gunicorn. The provided `Procfile` sets `APP_ENV=production`. Production WSGI startup requires:

| Variable | Requirement | Purpose |
|----------|-------------|---------|
| `APP_ENV` | `production` | Enables production secret validation and secure cookies |
| `SECRET_KEY` | Required; random, at least 32 characters | Signs Flask sessions |
| `DATABASE_URL` | Required on Vercel; recommended for hosted production | Points to persistent storage |

Generate a key with `python -c "import secrets; print(secrets.token_urlsafe(48))"` and store it in the hosting provider's secret/environment settings. Never commit it. Vercel's writable `/tmp` storage is ephemeral, so the app refuses to use it as permanent task storage; configure `DATABASE_URL` to a managed PostgreSQL database. Local development uses a SQLite file.

The WSGI command is:

```bash
APP_ENV=production gunicorn run:app
```

Set `APP_ENV=production`, `SECRET_KEY`, and `DATABASE_URL` in the hosting provider's environment configuration before startup. Schema setup currently uses `db.create_all()` and a small in-app compatibility migration; this is not a versioned migration system. Back up hosted data and plan a migration strategy before schema changes.

### Known limitations

- Reminder fields and notification endpoints exist, but no background scheduler is wired into this app to generate or deliver reminders automatically.
- Recurring task instances are created when a recurring task is completed. Monthly recurrence currently advances in fixed 30-day intervals.
- No automated browser/viewport test runner is configured; responsive behavior still requires manual browser checks at target widths.
- The project does not include a formal, versioned database migration tool.

---

## 📋 Changelog

### v2.1 — Bug Fix & Cleanup Release

**Critical fixes:**
- Added missing `__init__.py` to all three blueprint packages (`auth/`, `main/`, `api/`) — prevents import failures on Gunicorn / Vercel
- Optimised `@before_request` DB init guard to run once per process instead of on every HTTP request
- Made `SQLALCHEMY_ENGINE_OPTIONS` conditional — pool settings only apply when using PostgreSQL (`DATABASE_URL` set), avoiding SQLite warnings

**Security & correctness:**
- Changed `/delete/<id>` and `/complete/<id>` routes from `GET` to `POST` — prevents accidental mutations from crawlers, prefetch, or browser navigation
- Set a meaningful `login_message` so users see feedback when redirected to login

**Cleanup:**
- Removed legacy files (`app.py`, root-level `models.py`, `schedule_manager.py`) that conflicted with the current `app/` package structure
- Fixed CSS `--bg-surface` variable which had a fully transparent alpha (`#13172200` → `#131722`)
- Removed dead Jinja `namespace` variable from dashboard template
- Added static asset route to `vercel.json` for faster CSS/JS delivery via Vercel CDN
- Expanded `.gitignore` to cover agent tooling directories and additional IDE/system patterns
- Cleaned up git tracking of files that should have been ignored

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a feature branch, and open a pull request.

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
