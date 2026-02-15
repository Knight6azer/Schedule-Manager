
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Task
from app.extensions import db
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([task.to_dict() for task in tasks])

@api.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    
    if not data or not 'title' in data:
        return jsonify({'error': 'Title is required'}), 400
        
    due_date = None
    if 'due_date' in data:
        try:
            due_date = datetime.fromisoformat(data['due_date']).date()
        except ValueError:
            pass
            
    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        priority=data.get('priority', 'Medium'),
        category=data.get('category', 'General'),
        due_date=due_date,
        user_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@api.route('/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = data['priority']
    if 'category' in data:
        task.category = data['category']
    if 'status' in data:
        task.status = data['status']
    if 'due_date' in data:
        try:
            task.due_date = datetime.fromisoformat(data['due_date']).date()
        except ValueError:
            pass
            
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
