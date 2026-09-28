import unittest
import os
from unittest.mock import patch

from app import create_app
from config import Config, _get_db_uri


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-only-secret-key-for-schedule-manager'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class DeploymentTests(unittest.TestCase):
    def test_healthz_route_returns_ok(self):
        app = create_app(TestConfig)

        with app.test_client() as client:
            response = client.get('/healthz')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['status'], 'ok')

    def test_runtime_security_defaults_are_configured(self):
        app = create_app(TestConfig)

        self.assertEqual(app.config['MAX_CONTENT_LENGTH'], 16 * 1024 * 1024)
        self.assertEqual(app.config['SESSION_COOKIE_NAME'], 'schedule_manager_session')
        self.assertIn(app.config['PREFERRED_URL_SCHEME'], {'http', 'https'})

    def test_security_headers_and_static_cache_are_present(self):
        app = create_app(TestConfig)
        with app.test_client() as client:
            response = client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')
        self.assertIn("script-src 'self'", response.headers['Content-Security-Policy'])
        self.assertIn('Permissions-Policy', response.headers)
        self.assertIn('max-age=300', response.headers['Cache-Control'])
        self.assertNotIn('immutable', response.headers['Cache-Control'])
        response.close()

    def test_non_development_startup_requires_environment_secret(self):
        class ProductionConfig(Config):
            TESTING = False
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

        with patch.dict(os.environ, {'APP_ENV': '', 'SECRET_KEY': ''}):
            with self.assertRaisesRegex(RuntimeError, 'SECRET_KEY'):
                create_app(ProductionConfig)

    def test_vercel_requires_persistent_database_url(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'DATABASE_URL': ''}):
            with self.assertRaisesRegex(RuntimeError, 'DATABASE_URL'):
                _get_db_uri()

    def test_csrf_rejects_mutation_without_token(self):
        class CsrfConfig(Config):
            TESTING = False
            SECRET_KEY = 'test-only-secret-key-for-schedule-manager'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

        with patch.dict(os.environ, {'APP_ENV': 'development'}):
            app = create_app(CsrfConfig)
        with app.test_client() as client:
            page = client.get('/auth/login')
            self.assertEqual(page.status_code, 200)
            rejected = client.post('/auth/login', data={'email': '', 'password': ''})
            self.assertEqual(rejected.status_code, 400)
            self.assertIn(b'form has expired', rejected.data)

    def test_server_error_response_does_not_expose_exception(self):
        class ErrorConfig(Config):
            TESTING = False
            SECRET_KEY = 'test-only-secret-key-for-schedule-manager'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

        with patch.dict(os.environ, {'APP_ENV': 'development'}):
            app = create_app(ErrorConfig)

        @app.get('/test-server-error')
        def raise_test_error():
            raise RuntimeError('database password must stay private')

        with app.test_client() as client:
            response = client.get('/test-server-error')
            self.assertEqual(response.status_code, 500)
            self.assertNotIn(b'database password', response.data)
            self.assertIn(b'Something went wrong', response.data)


if __name__ == '__main__':
    unittest.main()
