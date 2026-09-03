from __future__ import annotations

from datetime import datetime
from typing import Any


class TaskService:
    VALID_PRIORITIES = ['High', 'Medium', 'Low']
    VALID_CATEGORIES = ['General', 'Work', 'Personal', 'Study', 'Health']
    VALID_STATUSES = ['Pending', 'In Progress', 'Completed']
    VALID_RECURRENCE_UNITS = ['day', 'week', 'month']

    @staticmethod
    def normalize_choice(value: Any, valid_values: list[str], default: str) -> str:
        if value is None:
            return default
        text = str(value).strip()
        if not text:
            return default
        for allowed in valid_values:
            if text.lower() == allowed.lower():
                return allowed
        return default

    @staticmethod
    def normalize_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}

    @staticmethod
    def parse_due_date(value: Any):
        if value in (None, ''):
            return None
        if isinstance(value, datetime):
            return value.date()
        if hasattr(value, 'date'):
            try:
                return value.date()
            except Exception:
                return None
        try:
            return datetime.fromisoformat(str(value)).date()
        except (TypeError, ValueError):
            return None

    @staticmethod
    def validate_task_payload(data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError('Task payload must be a dictionary.')

        title = (data.get('title') or '').strip()
        if not title:
            raise ValueError('Task title is required.')

        description = (data.get('description') or '').strip()
        priority = TaskService.normalize_choice(data.get('priority'), TaskService.VALID_PRIORITIES, 'Medium')
        category = TaskService.normalize_choice(data.get('category'), TaskService.VALID_CATEGORIES, 'General')
        status = TaskService.normalize_choice(data.get('status'), TaskService.VALID_STATUSES, 'Pending')
        due_date = TaskService.parse_due_date(data.get('due_date'))

        try:
            recurrence_interval = int(data.get('recurrence_interval') or 1)
        except (TypeError, ValueError):
            recurrence_interval = 1
        recurrence_interval = max(1, recurrence_interval)

        recurrence_unit = TaskService.normalize_choice(
            data.get('recurrence_unit'),
            TaskService.VALID_RECURRENCE_UNITS,
            'day',
        )

        try:
            reminder_days_ahead = int(data.get('reminder_days_ahead') or 1)
        except (TypeError, ValueError):
            reminder_days_ahead = 1
        reminder_days_ahead = max(1, reminder_days_ahead)

        is_recurring = TaskService.normalize_bool(data.get('is_recurring'))

        return {
            'title': title,
            'description': description,
            'priority': priority,
            'category': category,
            'status': status,
            'due_date': due_date,
            'is_recurring': is_recurring,
            'recurrence_interval': recurrence_interval,
            'recurrence_unit': recurrence_unit,
            'reminder_days_ahead': reminder_days_ahead,
        }

    @staticmethod
    def build_task_statistics(tasks: list[Any]) -> dict[str, int]:
        stats = {'total': 0, 'pending': 0, 'in_progress': 0, 'completed': 0}
        for task in tasks or []:
            stats['total'] += 1
            status = getattr(task, 'status', 'Pending')
            if status == 'Pending':
                stats['pending'] += 1
            elif status == 'In Progress':
                stats['in_progress'] += 1
            elif status == 'Completed':
                stats['completed'] += 1
        return stats
