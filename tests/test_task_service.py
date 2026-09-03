import unittest
from types import SimpleNamespace

from app.services.task_service import TaskService


class TaskServiceTests(unittest.TestCase):
    def test_parse_due_date_accepts_iso_strings(self):
        parsed = TaskService.parse_due_date('2026-09-15')
        self.assertEqual(str(parsed), '2026-09-15')

    def test_parse_due_date_rejects_invalid_values(self):
        self.assertIsNone(TaskService.parse_due_date('not-a-date'))

    def test_validate_task_payload_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            TaskService.validate_task_payload({'title': '   '})

    def test_validate_task_payload_normalizes_values(self):
        payload = TaskService.validate_task_payload({
            'title': '   Follow up on launch   ',
            'description': '  Need the final QA notes  ',
            'priority': 'low',
            'category': 'work',
            'status': 'in progress',
            'due_date': '2026-10-01'
        })

        self.assertEqual(payload['title'], 'Follow up on launch')
        self.assertEqual(payload['description'], 'Need the final QA notes')
        self.assertEqual(payload['priority'], 'Low')
        self.assertEqual(payload['category'], 'Work')
        self.assertEqual(payload['status'], 'In Progress')
        self.assertEqual(str(payload['due_date']), '2026-10-01')

    def test_build_task_statistics_counts_all_statuses(self):
        tasks = [
            SimpleNamespace(status='Pending'),
            SimpleNamespace(status='Pending'),
            SimpleNamespace(status='In Progress'),
            SimpleNamespace(status='Completed'),
            SimpleNamespace(status='Completed'),
            SimpleNamespace(status='Completed'),
        ]

        stats = TaskService.build_task_statistics(tasks)

        self.assertEqual(stats, {
            'total': 6,
            'pending': 2,
            'in_progress': 1,
            'completed': 3,
        })


if __name__ == '__main__':
    unittest.main()
