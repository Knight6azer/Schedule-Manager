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


if __name__ == '__main__':
    unittest.main()
