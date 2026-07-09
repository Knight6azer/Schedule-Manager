
# Schedule Manager V2

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.x-green.svg)
![Deployed on Vercel](https://img.shields.io/badge/deployed%20on-Vercel-black?logo=vercel)
![Status](https://img.shields.io/badge/status-active-success.svg)

A professional, full-featured task management web application built with **Python & Flask**. Features a dark glassmorphism UI, sidebar navigation, AJAX-driven interactions, live filtering, and a real-time stats dashboard — all with per-user task isolation and secure authentication.

---

## 🚀 Key Features

- **User Authentication** — Secure registration & login with full input validation (empty-field checks, min-length rules, friendly duplicate-email/username messages).
- **Per-User Task Isolation** — Every user sees only their own tasks.
- **Professional Dark UI** — Glassmorphism design system with a fixed sidebar, Google Inter font, smooth transitions, and CSS custom properties.
- **Real-Time Dashboard** — Stats bar (Total / Pending / In Progress / Completed) that refreshes after every AJAX action.
- **AJAX Interactions** — Toggle task status and delete tasks without any page reload; animated card removal.
- **Live Filtering** — Filter tasks by status tab, free-text search, category, and priority — all client-side, instant.
- **Toast Notifications** — Animated top-right toast system for all feedback (success, danger, info).
- **Full Task CRUD**:
  - **Priority**: High · Medium · Low (colour-coded card border)
  - **Category**: General · Work · Personal · Study · Health
  - **Status**: Pending · In Progress · Completed
  - **Due Date** tracking
- **RESTful JSON API** — Available at `/api/tasks` for external integrations.
- **Vercel-Ready** — `vercel.json` with static asset serving, session-cookie hardening, optimised DB init guard, and ephemeral `/tmp` DB fallback included.
- **Responsive** — Sidebar collapses to a hamburger menu on mobile.
- **SQLAlchemy 2.0 compatible** — Uses `db.session.get()` throughout; timezone-aware timestamps via `datetime.now(timezone.utc)`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask, Flask-SQLAlchemy 3.x (SQLAlchemy 2.0), Flask-Login |
| Database | SQLite (local) · PostgreSQL (production via `DATABASE_URL`) |
| Frontend | HTML5, Vanilla CSS (custom design system), Vanilla JS (AJAX + live filter), Jinja2 |
| Auth | Werkzeug password hashing, Flask-Login |
| Deployment | Vercel (serverless), Gunicorn (traditional) |

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
│   │   ├── index.html       # Dashboard: stats bar + filter bar + task grid
│   │   ├── login.html       # Split-panel login page
│   │   ├── register.html    # Split-panel register page
│   │   └── task_form.html   # Create / Edit task form
│   └── static/
│       ├── css/style.css    # Full design system (CSS custom properties, glassmorphism)
│       └── js/script.js     # AJAX toggle/delete, live filter, toasts, sidebar toggle
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

---

## 🔌 API Reference

All endpoints require an authenticated session. Responses are JSON.

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

## 🚀 Deployment — Vercel

The project ships with a `vercel.json` configuration. Key notes:

- **Static Assets** — CSS and JS files are served directly by Vercel's CDN via a dedicated static route, avoiding Python cold-start latency for asset requests.
- **Session Cookies** — `config.py` sets `SESSION_COOKIE_SECURE=True` and `SESSION_COOKIE_SAMESITE='Lax'` automatically when the `VERCEL` env var is detected, preventing login-loop issues over HTTPS.
- **Session Protection** — Uses `'basic'` mode in Flask-Login to prevent session token regeneration that causes redirect loops on stateless serverless deployments.
- **Database Init Guard** — `@app.before_request` calls `db.create_all()` once per container process (not on every request) using a per-process flag. This handles Vercel's ephemeral container model while avoiding per-request overhead.
- **Database** — On Vercel, SQLite is stored at `/tmp/schedule_v2.db` (ephemeral — data lost on cold starts). Set a `DATABASE_URL` env var (Neon, Supabase, etc.) for persistence.
- **Connection Pooling** — `pool_pre_ping=True` and `pool_recycle=280` are automatically enabled when `DATABASE_URL` is set, guarding against Neon's 5-minute idle connection timeout. These options are skipped for SQLite (which uses `NullPool`).

**Deploy steps:**
```bash
npm install -g vercel   # install Vercel CLI (one-time)
vercel                  # deploy from project root
```

**Required Vercel environment variables:**

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Session signing key (any long random string) |
| `DATABASE_URL` | Hosted PostgreSQL URI for persistent data (recommended) |

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
