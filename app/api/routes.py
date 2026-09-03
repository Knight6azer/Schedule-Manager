
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from app.models import Task, Notification
from app.extensions import db
from app.services.task_service import TaskService
from app.services.productivity_service import ProductivityService

api = Blueprint('api', __name__)


@api.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    q          = request.args.get('q', '').strip()
    status     = request.args.get('status', '')
    priority   = request.args.get('priority', '')
    category   = request.args.get('category', '')

    query = Task.query.filter_by(user_id=current_user.id)
    if q:
        query = query.filter(Task.title.ilike(f'%{q}%'))
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)

    tasks = query.order_by(Task.due_date.asc()).all()
    return jsonify([t.to_dict() for t in tasks])


@api.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json(silent=True) or {}
    try:
        sanitized = TaskService.validate_task_payload(data)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

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
    return jsonify(task.to_dict()), 201


@api.route('/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json(silent=True) or {}
    try:
        sanitized = TaskService.validate_task_payload({
            'title': data.get('title', task.title),
            'description': data.get('description', task.description),
            'priority': data.get('priority', task.priority),
            'category': data.get('category', task.category),
            'status': data.get('status', task.status),
            'due_date': data.get('due_date', task.due_date),
            'is_recurring': data.get('is_recurring', task.is_recurring),
            'recurrence_interval': data.get('recurrence_interval', task.recurrence_interval),
            'recurrence_unit': data.get('recurrence_unit', task.recurrence_unit),
            'reminder_days_ahead': data.get('reminder_days_ahead', task.reminder_days_ahead),
        })
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

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
    return jsonify(task.to_dict())


@api.route('/tasks/<int:id>/toggle', methods=['PATCH'])
@login_required
def toggle_task(id):
    """Toggle a task between Pending and Completed without a full page reload."""
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    task.status = 'Completed' if task.status != 'Completed' else 'Pending'
    if task.is_recurring and task.status == 'Completed':
        ProductivityService.create_recurring_task(task)
    db.session.commit()
    return jsonify(task.to_dict())


@api.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})


@api.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Return task counts grouped by status for the dashboard stats bar."""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        **TaskService.build_task_statistics(tasks),
        'analytics': ProductivityService.build_dashboard_analytics(tasks),
    })


@api.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifications])


@api.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_notification_read(id):
    notification = db.session.get(Notification, id)
    if notification is None or notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'})
