from __future__ import annotations

from datetime import date, datetime
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
        raise ValueError(f'Choose one of: {", ".join(valid_values)}.')

    @staticmethod
    def normalize_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        normalized = str(value).strip().lower()
        if normalized in {'1', 'true', 'yes', 'on'}:
            return True
        if normalized in {'0', 'false', 'no', 'off', ''}:
            return False
        raise ValueError('Choose whether the task repeats.')

    @staticmethod
    def parse_due_date(value: Any):
        if value in (None, ''):
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            raise ValueError('Due date must use YYYY-MM-DD format.')
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError('Due date must use YYYY-MM-DD format.') from exc
        if parsed.isoformat() != value:
            raise ValueError('Due date must use YYYY-MM-DD format.')
        return parsed

    @staticmethod
    def normalize_interval(value: Any, field_name: str) -> int:
        if value in (None, ''):
            return 1
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise ValueError(f'{field_name} must be a whole number from 1 to 30.')
        try:
            interval = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f'{field_name} must be a whole number from 1 to 30.') from exc
        if not 1 <= interval <= 30:
            raise ValueError(f'{field_name} must be a whole number from 1 to 30.')
        return interval

    @staticmethod
    def validate_task_payload(data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError('Task payload must be a dictionary.')

        raw_title = data.get('title')
        if not isinstance(raw_title, str):
            raise ValueError('Task title is required.')
        title = raw_title.strip()
        if not title:
            raise ValueError('Task title is required.')
        if len(title) > 100:
            raise ValueError('Task title must be 100 characters or fewer.')

        raw_description = data.get('description')
        if raw_description is not None and not isinstance(raw_description, str):
            raise ValueError('Task description must be text.')
        description = (raw_description or '').strip()
        priority = TaskService.normalize_choice(data.get('priority'), TaskService.VALID_PRIORITIES, 'Medium')
        category = TaskService.normalize_choice(data.get('category'), TaskService.VALID_CATEGORIES, 'General')
        status = TaskService.normalize_choice(data.get('status'), TaskService.VALID_STATUSES, 'Pending')
        due_date = TaskService.parse_due_date(data.get('due_date'))

        recurrence_interval = TaskService.normalize_interval(
            data.get('recurrence_interval'),
            'Repeat interval',
        )

        recurrence_unit = TaskService.normalize_choice(
            data.get('recurrence_unit'),
            TaskService.VALID_RECURRENCE_UNITS,
            'day',
        )

        reminder_days_ahead = TaskService.normalize_interval(
            data.get('reminder_days_ahead'),
            'Reminder window',
        )

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
