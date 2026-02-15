
# Schedule Manager V2

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.x-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A professional, industry-standard task management application built with Flask. This project demonstrates a full-stack web application architecture with user authentication, database management, and a RESTful API.

## 🚀 Key Features

*   **User Authentication**: Secure Login and Registration system using `Flask-Login` and password hashing. Data is private to each user.
*   **Modular Architecture**: Structured using Flask Blueprints (`auth`, `main`, `api`) for scalability and maintainability.
*   **Task Management**:
    *   Create, Read, Update, Delete (CRUD) tasks.
    *   **Priorities**: High, Medium, Low.
    *   **Categories**: Work, Personal, Study, Health.
    *   **Status Tracking**: Pending, In Progress, Completed.
    *   **Due Dates**: Track deadlines efficiently.
*   **RESTful API**: Fully functional JSON API for external integrations (e.g., mobile apps).
*   **Background Scheduler**: Integrated `Flask-APScheduler` infrastructure for future automated tasks (reminders, cleanup).
*   **Responsive UI**: Modern, clean interface adapted for all devices.

## 🛠️ Tech Stack

*   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-APScheduler
*   **Database**: SQLite (Development), PostgreSQL (Production ready)
*   **Frontend**: HTML5, CSS3, Jinja2 Templates
*   **API**: REST with JSON responses

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
│   └── static/          # CSS, JS, Images
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
    *The database will be automatically created on the first run.*

5.  **Access the app:**
    Open `http://127.0.0.1:5000` in your browser.

## 🔌 API Documentation

The application exposes a REST API at `/api/tasks`. Standard authentication is required (currently session-based for browser).

*   `GET /api/tasks`: List all tasks.
*   `POST /api/tasks`: Create a new task.
*   `PUT /api/tasks/<id>`: Update a task.
*   `DELETE /api/tasks/<id>`: Delete a task.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
