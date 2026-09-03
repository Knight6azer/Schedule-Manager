import unittest
from types import SimpleNamespace

from app.services.productivity_service import ProductivityService


class ProductivityServiceTests(unittest.TestCase):
    def test_build_dashboard_analytics_handles_zero_tasks(self):
        analytics = ProductivityService.build_dashboard_analytics([])
        self.assertEqual(analytics['total'], 0)
        self.assertEqual(analytics['completion_rate'], 0.0)

    def test_build_dashboard_analytics_counts_overdue_and_recurring(self):
        from datetime import date
        tasks = [
            SimpleNamespace(status='Completed', due_date=date(2026, 9, 1), is_recurring=False),
            SimpleNamespace(status='Pending', due_date=date(2026, 8, 20), is_recurring=True),
            SimpleNamespace(status='Pending', due_date=date(2026, 9, 10), is_recurring=False),
            SimpleNamespace(status='In Progress', due_date=date(2026, 9, 11), is_recurring=True),
        ]

        analytics = ProductivityService.build_dashboard_analytics(tasks)

        self.assertEqual(analytics['total'], 4)
        self.assertEqual(analytics['pending'], 2)
        self.assertEqual(analytics['in_progress'], 1)
        self.assertEqual(analytics['completed'], 1)
        self.assertEqual(analytics['recurring'], 2)
        self.assertEqual(analytics['completion_rate'], 25.0)


if __name__ == '__main__':
    unittest.main()
