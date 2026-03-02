
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Task
from app.extensions import db
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date.asc()).all()
    stats = {
        'total'      : len(tasks),
        'pending'    : sum(1 for t in tasks if t.status == 'Pending'),
        'in_progress': sum(1 for t in tasks if t.status == 'In Progress'),
        'completed'  : sum(1 for t in tasks if t.status == 'Completed'),
    }
    return render_template('index.html', tasks=tasks, stats=stats)


@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title       = request.form.get('title')
        description = request.form.get('description')
        priority    = request.form.get('priority')
        category    = request.form.get('category')
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

        task = Task(
            title=title, description=description,
            priority=priority, category=category,
            due_date=due_date, user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('task_form.html', task=None)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        task.title       = request.form.get('title')
        task.description = request.form.get('description')
        task.priority    = request.form.get('priority')
        task.category    = request.form.get('category')
        task.status      = request.form.get('status')
        due_date_str     = request.form.get('due_date')
        task.due_date    = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('main.index'))
    return render_template('task_form.html', task=task)


@main.route('/complete/<int:id>')
@login_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))
    task.status = 'Completed' if task.status != 'Completed' else 'Pending'
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/delete/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('main.index'))
