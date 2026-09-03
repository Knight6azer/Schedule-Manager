from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.models import Notification, Task
from app.extensions import db


class ProductivityService:
    @staticmethod
    def build_dashboard_analytics(tasks: list[Task]) -> dict[str, Any]:
        total = len(tasks)
        completed = sum(1 for task in tasks if task.status == 'Completed')
        pending = sum(1 for task in tasks if task.status == 'Pending')
        in_progress = sum(1 for task in tasks if task.status == 'In Progress')
        overdue = sum(
            1
            for task in tasks
            if task.due_date and task.due_date < datetime.now(timezone.utc).date() and task.status != 'Completed'
        )
        recurring = sum(1 for task in tasks if getattr(task, 'is_recurring', False))
        completion_rate = round((completed / total) * 100, 1) if total else 0.0
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'overdue': overdue,
            'recurring': recurring,
            'completion_rate': completion_rate,
        }

    @staticmethod
    def create_reminder_notification(user_id: int, task: Task) -> Notification:
        if not task.due_date:
            raise ValueError('Tasks without a due date cannot create a reminder.')

        message = f"Reminder: '{task.title}' is due on {task.due_date.isoformat()}."
        notification = Notification(
            user_id=user_id,
            task_id=task.id,
            title='Task Reminder',
            message=message,
            notification_type='info',
        )
        db.session.add(notification)
        return notification

    @staticmethod
    def generate_due_date_reminders(user_id: int):
        today = datetime.now(timezone.utc).date()
        tasks = Task.query.filter_by(user_id=user_id).all()
        created = []
        for task in tasks:
            if not task.due_date or task.status == 'Completed':
                continue
            days_until = (task.due_date - today).days
            if 0 <= days_until <= max(1, getattr(task, 'reminder_days_ahead', 1)):
                existing = Notification.query.filter_by(user_id=user_id, task_id=task.id, title='Task Reminder').first()
                if existing is None:
                    created.append(ProductivityService.create_reminder_notification(user_id, task))
        db.session.commit()
        return len(created)

    @staticmethod
    def create_recurring_task(task: Task):
        if not task.is_recurring:
            return None

        delta_map = {
            'day': timedelta(days=max(1, task.recurrence_interval or 1)),
            'week': timedelta(weeks=max(1, task.recurrence_interval or 1)),
            'month': timedelta(days=30 * max(1, task.recurrence_interval or 1)),
        }

        delta = delta_map.get(task.recurrence_unit or 'day', delta_map['day'])
        current_due = task.next_due_date or task.due_date
        if current_due is None:
            return None

        next_due = current_due + delta
        new_task = Task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            category=task.category,
            status='Pending',
            due_date=next_due,
            user_id=task.user_id,
            is_recurring=True,
            recurrence_interval=task.recurrence_interval or 1,
            recurrence_unit=task.recurrence_unit or 'day',
            next_due_date=next_due,
            reminder_days_ahead=task.reminder_days_ahead or 1,
        )
        db.session.add(new_task)
        task.status = 'Completed'
        task.next_due_date = next_due
        return new_task
