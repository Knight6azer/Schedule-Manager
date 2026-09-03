
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Task, Notification
from app.extensions import db
from app.services.task_service import TaskService
from app.services.productivity_service import ProductivityService

main = Blueprint('main', __name__)


@main.route('/healthz')
def healthz():
    """Lightweight endpoint for hosting checks and deployment monitors."""
    return {'status': 'ok'}, 200


@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date.asc()).all()
    stats = TaskService.build_task_statistics(tasks)
    analytics = ProductivityService.build_dashboard_analytics(tasks)
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
    return render_template('index.html', tasks=tasks, stats=stats, analytics=analytics, notifications=notifications)


@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        payload = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'priority': request.form.get('priority'),
            'category': request.form.get('category'),
            'status': request.form.get('status', 'Pending'),
            'due_date': request.form.get('due_date'),
            'is_recurring': request.form.get('is_recurring'),
            'recurrence_interval': request.form.get('recurrence_interval'),
            'recurrence_unit': request.form.get('recurrence_unit'),
            'reminder_days_ahead': request.form.get('reminder_days_ahead'),
        }

        try:
            sanitized = TaskService.validate_task_payload(payload)
        except ValueError as exc:
            flash(str(exc), 'warning')
            return render_template('task_form.html', task=None)

        task = Task(
            title=sanitized['title'],
            description=sanitized['description'] or None,
            priority=sanitized['priority'],
            category=sanitized['category'],
            status=sanitized['status'],
            due_date=sanitized['due_date'],
            is_recurring=sanitized['is_recurring'],
            recurrence_interval=sanitized['recurrence_interval'],
            recurrence_unit=sanitized['recurrence_unit'],
            reminder_days_ahead=sanitized['reminder_days_ahead'],
            user_id=current_user.id,
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('task_form.html', task=None)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    if task.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        payload = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'priority': request.form.get('priority'),
            'category': request.form.get('category'),
            'status': request.form.get('status'),
            'due_date': request.form.get('due_date'),
            'is_recurring': request.form.get('is_recurring'),
            'recurrence_interval': request.form.get('recurrence_interval'),
            'recurrence_unit': request.form.get('recurrence_unit'),
            'reminder_days_ahead': request.form.get('reminder_days_ahead'),
        }

        try:
            sanitized = TaskService.validate_task_payload(payload)
        except ValueError as exc:
            flash(str(exc), 'warning')
            return render_template('task_form.html', task=task)

        task.title = sanitized['title']
        task.description = sanitized['description'] or None
        task.priority = sanitized['priority']
        task.category = sanitized['category']
        task.status = sanitized['status']
        task.due_date = sanitized['due_date']
        task.is_recurring = sanitized['is_recurring']
        task.recurrence_interval = sanitized['recurrence_interval']
        task.recurrence_unit = sanitized['recurrence_unit']
        task.reminder_days_ahead = sanitized['reminder_days_ahead']
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('main.index'))
    return render_template('task_form.html', task=task)


@main.route('/complete/<int:id>', methods=['POST'])
@login_required
def complete_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    if task.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))
    task.status = 'Completed' if task.status != 'Completed' else 'Pending'
    if task.is_recurring and task.status == 'Completed':
        ProductivityService.create_recurring_task(task)
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    if task.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.index'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('main.index'))
