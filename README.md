
# Schedule Manager V2 (Neon Edition)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.x-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A professional, industry-standard task management application built with Flask. Recently upgraded with a **stunning Blue-Violet Neon interface** featuring glassmorphism and modern design principles.

## 🚀 Key Features

*   **User Authentication**: Secure Login and Registration system using `Flask-Login` and password hashing.
*   **Neon Dark Theme**: A futuristic, high-contrast UI with neon glows and glassmorphism transparency effects.
*   **Modular Architecture**: Structured using Flask Blueprints (`auth`, `main`, `api`) for scalability.
*   **Task Management**:
    *   Create, Read, Update, Delete (CRUD) tasks.
    *   **Priorities**: High, Medium, Low (Color-coded).
    *   **Categories**: Work, Personal, Study, Health.
    *   **Status Tracking**: Pending, In Progress, Completed.
    *   **Due Dates**: Track deadlines efficiently.
*   **RESTful API**: Fully functional JSON API for external integrations.
*   **Background Scheduler**: Integrated `Flask-APScheduler` infrastructure.

## 🛠️ Tech Stack

*   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-APScheduler
*   **Database**: SQLite (Development), PostgreSQL (Production ready)
*   **Frontend**: HTML5, CSS3 (Custom Neon Theme), Jinja2 Templates
*   **Font**: Outfit (Google Fonts)

## 📂 Project Structure

```
project/
├── app/
│   ├── __init__.py      # Application Factory
│   ├── models.py        # Database Models (User, Task)
│   ├── extensions.py    # Flask Extensions
│   ├── auth/            # Authentication Blueprint
│   ├── main/            # Core Application Blueprint
│   ├── api/             # API Blueprint
│   ├── templates/       # HTML Templates
│   └── static/          # CSS (Neon Theme), JS
├── config.py            # Configuration settings
├── run.py               # Entry point
└── requirements.txt     # Dependencies
```

## 📦 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Knight6azer/Schedule-Manager.git
    cd Schedule-Manager
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python run.py
    ```

5.  **Access the app:**
    Open `http://127.0.0.1:5000` in your browser.

## 🔌 API Documentation

The application exposes a REST API at `/api/tasks`. Standard authentication is required.

*   `GET /api/tasks`: List all tasks.
*   `POST /api/tasks`: Create a new task.
*   `PUT /api/tasks/<id>`: Update a task.
*   `DELETE /api/tasks/<id>`: Delete a task.

## 🚀 Deployment (Vercel)
The project includes a `vercel.json` configuration for easy deployment on Vercel.

1.  **Install Vercel CLI**: `npm install -g vercel`
2.  **Deploy**: Run `vercel` in the project directory.

> **Note**: The background scheduler (`Flask-APScheduler`) may have limitations on serverless platforms like Vercel due to execution time limits.

> **Important**: On Vercel, the SQLite database is stored in `/tmp` (ephemeral storage). **Data will be lost** when the function restarts. For production, please configure a `DATABASE_URL` environment variable pointing to a PostgreSQL database (e.g., Vercel Postgres, Supabase, or Neon).

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
