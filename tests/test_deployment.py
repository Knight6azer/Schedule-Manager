import unittest

from app import create_app


class DeploymentTests(unittest.TestCase):
    def test_healthz_route_returns_ok(self):
        app = create_app()
        app.config['TESTING'] = True

        with app.test_client() as client:
            response = client.get('/healthz')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['status'], 'ok')

    def test_runtime_security_defaults_are_configured(self):
        app = create_app()
        app.config['TESTING'] = True

        self.assertEqual(app.config['MAX_CONTENT_LENGTH'], 16 * 1024 * 1024)
        self.assertEqual(app.config['SESSION_COOKIE_NAME'], 'schedule_manager_session')
        self.assertIn(app.config['PREFERRED_URL_SCHEME'], {'http', 'https'})


if __name__ == '__main__':
    unittest.main()
