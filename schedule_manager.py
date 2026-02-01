import json
import os
from datetime import datetime, timedelta

DATA_FILE = "schedule_data.json"

class Task:
    def __init__(self, title, description, priority, due_date, completed=False, created_at=None):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.created_at = created_at if created_at else datetime.now().isoformat()

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            description=data["description"],
            priority=data["priority"],
            due_date=data["due_date"],
            completed=data["completed"],
            created_at=data.get("created_at")
        )

    def __str__(self):
        status = "[x]" if self.completed else "[ ]"
        return f"{status} {self.title} (Due: {self.due_date}, Priority: {self.priority})"


class ScheduleManager:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.tasks = []
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            self.tasks = []
            return

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(t) for t in data]
            print(f"Loaded {len(self.tasks)} tasks.")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}. Starting with empty list.")
            self.tasks = []

    def save_data(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=4)
            print("Data saved successfully.")
        except IOError as e:
            print(f"Error saving data: {e}")

    def add_task(self, title, description, priority, due_date):
        new_task = Task(title, description, priority, due_date)
        self.tasks.append(new_task)
        self.save_data()
        print("Task added successfully.")

    def list_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return

        print("\n--- All Tasks ---")
        for index, task in enumerate(self.tasks):
            print(f"{index + 1}. {task}")
        print("-----------------")

    def update_task(self, index, title=None, description=None, priority=None, due_date=None):
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            if title: task.title = title
            if description: task.description = description
            if priority: task.priority = priority
            if due_date: task.due_date = due_date
            self.save_data()
            print("Task updated successfully.")
        else:
            print("Invalid task index.")

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            removed = self.tasks.pop(index)
            self.save_data()
            print(f"Deleted task: {removed.title}")
        else:
            print("Invalid task index.")

    def mark_completed(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = True
            self.save_data()
            print("Task marked as completed.")
        else:
            print("Invalid task index.")

    def get_upcoming_tasks(self, days=7):
        print(f"\n--- Tasks Due in Next {days} Days ---")
        today = datetime.now()
        upcoming_count = 0
        for task in self.tasks:
            try:
                # Assuming due_date format YYYY-MM-DD
                due_dt = datetime.strptime(task.due_date, "%Y-%m-%d")
                delta = due_dt - today
                if 0 <= delta.days <= days and not task.completed:
                    print(task)
                    upcoming_count += 1
            except ValueError:
                continue # Skip invalid dates
        
        if upcoming_count == 0:
            print("No upcoming tasks found.")
        print("---------------------------------")

def get_valid_date():
    while True:
        date_str = input("Enter due date (YYYY-MM-DD): ")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD.")

def main():
    manager = ScheduleManager()

    while True:
        print("\n=== Schedule Manager ===")
        print("1. Add Task")
        print("2. List All Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Task Completed")
        print("6. View Upcoming Tasks (7 Days)")
        print("7. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            title = input("Enter title: ")
            desc = input("Enter description: ")
            prio = input("Enter priority (High/Medium/Low): ")
            due = get_valid_date()
            manager.add_task(title, desc, prio, due)
        
        elif choice == '2':
            manager.list_tasks()

        elif choice == '3':
            manager.list_tasks()
            try:
                idx = int(input("Enter task number to update: ")) - 1
                print("Leave blank to keep current value.")
                title = input("New title: ")
                desc = input("New description: ")
                prio = input("New priority: ")
                due_in = input("New due date (YYYY-MM-DD) or enter to skip: ")
                due = None
                if due_in:
                    try:
                        datetime.strptime(due_in, "%Y-%m-%d")
                        due = due_in
                    except ValueError:
                         print("Invalid date format, keeping old date.")

                manager.update_task(idx, title if title else None, 
                                    desc if desc else None, 
                                    prio if prio else None, 
                                    due)
            except ValueError:
                print("Invalid input.")

        elif choice == '4':
            manager.list_tasks()
            try:
                idx = int(input("Enter task number to delete: ")) - 1
                manager.delete_task(idx)
            except ValueError:
                print("Invalid input.")

        elif choice == '5':
            manager.list_tasks()
            try:
                idx = int(input("Enter task number to mark complete: ")) - 1
                manager.mark_completed(idx)
            except ValueError:
                print("Invalid input.")

        elif choice == '6':
            manager.get_upcoming_tasks()

        elif choice == '7':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
