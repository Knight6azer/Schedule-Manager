# Schedule Manager

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.x-green.svg)

A robust, full-fledged web application for managing tasks and schedules. Built with Python (Flask) and SQLite, this project offers a modern user interface to help you stay organized.

## 🚀 Features

-   **Dashboard View**: Get a clear overview of upcoming tasks, sorted by priority and due date.
-   **Task Management**: Easily add, edit, delete, and mark tasks as complete.
-   **Priority Levels**: Categorize tasks by High, Medium, or Low priority.
-   **Data Persistence**: Uses a reliable SQLite database to store your schedule.
-   **Responsive Design**: A clean, modern UI that works on desktop and mobile.

## 🛠️ Tech Stack

-   **Backend**: Python, Flask, SQLAlchemy
-   **Database**: SQLite
-   **Frontend**: HTML5, CSS3 (Custom + Responsive), JavaScript
-   **Deployment**: Ready for Render/Heroku (Gunicorn support)

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Knight6azer/Schedule-Manager.git
    cd Schedule-Manager
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```

5.  **Access the app:**
    Open your browser and navigate to `http://127.0.0.1:5000`.

## ☁️ Deployment

This project includes a `Procfile` and is configured for easy deployment on platforms like Render or Heroku.

### Deploy on Render
1.  Connect your GitHub repository to Render.
2.  Select "Web Service".
3.  Set the **Start Command** to: `gunicorn app:app`.
4.  Deploy!

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements.

## 📄 License

This project is open-source and available under the MIT License.
