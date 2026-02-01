# Schedule Manager 📅

A lightweight, Command-Line Interface (CLI) productivity tool built with **Python** to manage daily tasks efficiently with persistent **JSON storage**.

## 📌 Project Overview

The **Schedule Manager** is designed to streamline personal task organization. It provides a robust framework for tracking activities, setting due dates, and managing task priorities through a terminal-based interface.

### **Key Features**

* **Full CRUD Operations**: Create, Read, Update, and Delete tasks seamlessly.
* **Data Persistence**: All tasks are automatically saved to a `schedule_data.json` file, ensuring no data is lost between sessions.
* **Upcoming Task Alerts**: Filter and view tasks due within a specific time window (e.g., the next 7 days).
* **Status Tracking**: Mark tasks as completed with visual indicators.
* **Error Handling**: Built-in validation for date formats and user input to prevent application crashes.

## 🛠️ Tech Stack

* **Language**: Python 3.6+
* **Storage**: JSON Serialization
* **Libraries**: `datetime` (time tracking), `os` (file handling), `json` (data storage).

## 📐 System Architecture

The project follows a **Modular OOP (Object-Oriented Programming)** approach:

* **Task Class**: Handles individual task objects, including title, description, priority, and timestamps.
* **ScheduleManager Class**: The engine of the app, containing the logic for task manipulation and JSON I/O.
* **Main Loop**: A continuous interface loop that processes user commands.

## 🚀 Getting Started

1. **Clone the repo:**
```bash
git clone https://github.com/your-username/Schedule-Manager-Python.git
```

2. **Run the application:**
```bash
python schedule_manager.py
```

---

## 💼 Portfolio / LinkedIn Profile Showcase

*(Use this text for your "Projects" section on LinkedIn or your personal website)*

### **Schedule Manager | Python Developer**

**Electronics & Computer Science Engineering Project (Sem IV)**

**Project Summary:**
Developed a command-line productivity application to automate task scheduling and tracking. The tool allows users to manage a dynamic list of tasks with specified deadlines and priorities, stored locally in a structured JSON format.

**Impact & Learnings:**

* **Data Management**: Implemented serialization and deserialization using the JSON library to maintain persistent state.
* **Algorithm Logic**: Built logic to filter and retrieve "Upcoming Tasks" based on time deltas, enhancing user time management.
* **Software Design**: Applied modular programming principles to ensure the code is extensible for future GUI (PyQt/Tkinter) integration.

**Core Competencies**: Python Programming, JSON Data Handling, Object-Oriented Design (OOD), CRUD Logic.

---

## 📝 Future Enhancement Ideas

* **GUI Integration**: Upgrading the interface to a graphical window using **Tkinter** or **PyQt**.
* **Cloud Sync**: Integrating with **Google Calendar API** to sync tasks across platforms.
* **Notifications**: Adding desktop reminder alerts for tasks reaching their due date.
