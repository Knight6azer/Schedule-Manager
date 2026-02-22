
# Schedule Manager V2 — Neon Edition

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.x-green.svg)
![Deployed on Vercel](https://img.shields.io/badge/deployed%20on-Vercel-black?logo=vercel)
![Status](https://img.shields.io/badge/status-active-success.svg)

A professional, full-featured task management web application built with **Python & Flask**. Features a stunning **Blue-Violet Neon** dark theme with glassmorphism effects, per-user task isolation via authentication, and a RESTful API.

---

## 🚀 Key Features

- **User Authentication** — Secure registration & login via `Flask-Login` and Werkzeug password hashing.
- **Per-User Task Isolation** — Every user sees only their own tasks.
- **Neon Dark Theme** — Futuristic Blue-Violet UI with neon glows, glassmorphism, and smooth transitions. Font: *Outfit* (Google Fonts).
- **Modular Blueprint Architecture** — Clean separation via `auth`, `main`, and `api` Blueprints.
- **Full Task CRUD**:
  - Create, Read, Update, Delete tasks.
  - **Priority**: High · Medium · Low (color-coded).
  - **Category**: Work · Personal · Study · Health.
  - **Status**: Pending · In Progress · Completed.
  - **Due Date** tracking.
  - **Reminder Time** field.
- **RESTful JSON API** — Available at `/api/tasks` for external integrations.
- **APScheduler Integration** — Background scheduler infrastructure (gracefully disabled on serverless).
- **Vercel-Ready** — Includes `vercel.json`, session-cookie hardening, and ephemeral `/tmp` DB fallback.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-APScheduler |
| Database | SQLite (local) · PostgreSQL (production via `DATABASE_URL`) |
| Frontend | HTML5, CSS3 (Custom Neon Theme), Jinja2 |
| Auth | Werkzeug password hashing, `flask-login`, `email-validator` |
| Deployment | Vercel (serverless), Gunicorn (traditional) |

---

## 📂 Project Structure

```
Schedule Manager (Py)/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── extensions.py        # Shared Flask extensions (db, login_manager, scheduler)
│   ├── models.py            # SQLAlchemy models: User, Task
│   ├── auth/
│   │   └── routes.py        # /auth/login, /auth/register, /auth/logout
│   ├── main/
│   │   └── routes.py        # / (dashboard), /add, /edit/<id>, /delete/<id>, ...
│   ├── api/
│   │   └── routes.py        # /api/tasks (CRUD JSON API)
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS (Neon theme), JS
├── config.py                # Config class (SECRET_KEY, DB URI, session cookies)
├── run.py                   # Entry point — calls create_app()
├── vercel.json              # Vercel serverless deployment config
├── Procfile                 # For Gunicorn / traditional hosting
├── requirements.txt         # Python dependencies
└── schedule_v2.db           # Local SQLite DB (auto-created, git-ignored)
```

---

## 📦 Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Knight6azer/Schedule-Manager.git
   cd Schedule-Manager
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

All API endpoints require an authenticated session. Responses are JSON.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks` | List all tasks for the logged-in user |
| `POST` | `/api/tasks` | Create a new task |
| `PUT` | `/api/tasks/<id>` | Update an existing task |
| `DELETE` | `/api/tasks/<id>` | Delete a task |

**Task JSON Schema:**
```json
{
  "id": 1,
  "title": "Finish report",
  "description": "Q4 summary",
  "priority": "High",
  "category": "Work",
  "status": "In Progress",
  "due_date": "2025-12-31",
  "reminder_time": null,
  "created_at": "2025-02-15T10:00:00",
  "updated_at": "2025-02-15T10:00:00",
  "user_id": 1
}
```

---

## 🚀 Deployment — Vercel

The project ships with a `vercel.json` configuration. Important notes:

- **Session Cookies** — `config.py` automatically sets `SESSION_COOKIE_SECURE=True` and `SESSION_COOKIE_SAMESITE='Lax'` when the `VERCEL` environment variable is detected, preventing the login-loop issue on HTTPS.
- **Database** — On Vercel, SQLite is stored at `/tmp/schedule_v2.db` (ephemeral). **Data is lost on cold-starts.** Set a `DATABASE_URL` environment variable (Vercel Postgres, Supabase, Neon, etc.) for persistence.
- **Scheduler** — `Flask-APScheduler` starts gracefully and silently fails on serverless environments where background threads aren't supported.

**Deploy steps:**
```bash
npm install -g vercel   # install Vercel CLI (one-time)
vercel                  # deploy from project root
```

**Required Vercel environment variables:**

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Session signing key (any long random string) |
| `DATABASE_URL` | (Optional) Hosted PostgreSQL URI for persistent data |

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a feature branch, and open a pull request.

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
