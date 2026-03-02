
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Task
from app.extensions import db
from datetime import datetime

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
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date']).date()
        except ValueError:
            pass

    task = Task(
        title       = data['title'],
        description = data.get('description'),
        priority    = data.get('priority', 'Medium'),
        category    = data.get('category', 'General'),
        due_date    = due_date,
        user_id     = current_user.id
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@api.route('/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    for field in ('title', 'description', 'priority', 'category', 'status'):
        if field in data:
            setattr(task, field, data[field])
    if 'due_date' in data:
        try:
            task.due_date = datetime.fromisoformat(data['due_date']).date()
        except (ValueError, TypeError):
            task.due_date = None

    db.session.commit()
    return jsonify(task.to_dict())


@api.route('/tasks/<int:id>/toggle', methods=['PATCH'])
@login_required
def toggle_task(id):
    """Toggle a task between Pending and Completed without a full page reload."""
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    task.status = 'Completed' if task.status != 'Completed' else 'Pending'
    db.session.commit()
    return jsonify(task.to_dict())


@api.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
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
    stats = {
        'total'      : len(tasks),
        'pending'    : sum(1 for t in tasks if t.status == 'Pending'),
        'in_progress': sum(1 for t in tasks if t.status == 'In Progress'),
        'completed'  : sum(1 for t in tasks if t.status == 'Completed'),
    }
    return jsonify(stats)
