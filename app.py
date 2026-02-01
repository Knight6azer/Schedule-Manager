from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Task
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key' # Change for production

db.init_app(app)

# Database initialized in main block


def import_legacy_data():
    json_path = "schedule_data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                for item in data:
                    try:
                        # Handle date parsing
                        due_date = datetime.strptime(item.get("due_date"), "%Y-%m-%d").date() if item.get("due_date") else None
                        created_at = datetime.fromisoformat(item.get("created_at")) if item.get("created_at") else datetime.utcnow()
                        
                        task = Task(
                            title=item.get("title"),
                            description=item.get("description"),
                            priority=item.get("priority", "Medium"),
                            due_date=due_date,
                            completed=item.get("completed", False),
                            created_at=created_at
                        )
                        db.session.add(task)
                    except ValueError:
                        continue # Skip invalid items
                db.session.commit()
                print("Legacy data imported successfully.")
        except Exception as e:
            print(f"Error importing legacy data: {e}")

@app.route('/')
def index():
    tasks = Task.query.order_by(Task.due_date.asc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        due_date_str = request.form.get('due_date')
        
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else None
        
        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('task_form.html', task=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = request.form.get('priority')
        due_date_str = request.form.get('due_date')
        
        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        else:
            task.due_date = None
            
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('task_form.html', task=task)

@app.route('/complete/<int:id>')
def complete_task(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Import existing data if database is empty
        if not Task.query.first():
            import_legacy_data()
    app.run(debug=True)
