import unittest
from datetime import date

from app import create_app
from app.extensions import db
from app.models import Task, User
from config import Config


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-only-secret-key-for-schedule-manager'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ApiIsolationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        with self.app.app_context():
            db.create_all()
            owner = User(username='owner', email='owner@example.com')
            owner.set_password('test-password')
            other = User(username='other', email='other@example.com')
            other.set_password('test-password')
            db.session.add_all((owner, other))
            db.session.flush()

            self.owner_task = Task(title='Owner task', user_id=owner.id)
            self.other_task = Task(title='Other task', user_id=other.id)
            db.session.add_all((self.owner_task, self.other_task))
            db.session.commit()
            self.owner_task_id = self.owner_task.id
            self.other_task_id = self.other_task.id
            self.owner_id = owner.id

        self.client = self.app.test_client()
        response = self.client.post('/auth/login', data={
            'email': 'owner@example.com',
            'password': 'test-password',
        })
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_task_list_contains_only_authenticated_users_records(self):
        response = self.client.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        tasks = response.get_json()
        self.assertEqual([task['id'] for task in tasks], [self.owner_task_id])

    def test_user_cannot_update_toggle_or_delete_another_users_task(self):
        response = self.client.put(
            f'/api/tasks/{self.other_task_id}',
            json={'title': 'Changed by owner'},
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.patch(f'/api/tasks/{self.other_task_id}/toggle')
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(f'/api/tasks/{self.other_task_id}')
        self.assertEqual(response.status_code, 403)

        with self.app.app_context():
            task = db.session.get(Task, self.other_task_id)
            self.assertEqual(task.title, 'Other task')
            self.assertEqual(task.status, 'Pending')

    def test_invalid_api_fields_are_rejected_without_creating_a_task(self):
        response = self.client.post('/api/tasks', json={
            'title': 'Needs a real priority',
            'priority': 'Urgent',
        })
        self.assertEqual(response.status_code, 400)

        with self.app.app_context():
            created = Task.query.filter_by(title='Needs a real priority').first()
            self.assertIsNone(created)

    def test_completing_a_recurring_task_creates_its_next_due_instance(self):
        response = self.client.post('/api/tasks', json={
            'title': 'Weekly review',
            'due_date': '2026-10-01',
            'is_recurring': True,
            'recurrence_interval': 1,
            'recurrence_unit': 'week',
        })
        self.assertEqual(response.status_code, 201)
        recurring_id = response.get_json()['id']

        response = self.client.patch(f'/api/tasks/{recurring_id}/toggle')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'Completed')

        with self.app.app_context():
            next_instance = Task.query.filter_by(
                user_id=self.owner_id,
                title='Weekly review',
                status='Pending',
            ).one()
            self.assertEqual(next_instance.due_date.isoformat(), '2026-10-08')

    def test_api_orders_due_tasks_before_undated_tasks(self):
        with self.app.app_context():
            due_later = Task(
                title='Later due',
                due_date=date(2026, 10, 2),
                priority='High',
                user_id=self.owner_id,
            )
            due_earlier_low = Task(
                title='Earlier low',
                due_date=date(2026, 10, 1),
                priority='Low',
                user_id=self.owner_id,
            )
            due_earlier_high = Task(
                title='Earlier high',
                due_date=date(2026, 10, 1),
                priority='High',
                user_id=self.owner_id,
            )
            db.session.add_all((due_later, due_earlier_low, due_earlier_high))
            db.session.commit()
            expected_ids = [
                due_earlier_high.id,
                due_earlier_low.id,
                due_later.id,
                self.owner_task_id,
            ]

        response = self.client.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([task['id'] for task in response.get_json()], expected_ids)


if __name__ == '__main__':
    unittest.main()
