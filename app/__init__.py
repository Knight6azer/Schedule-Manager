
import os
import secrets
from hmac import compare_digest

from flask import Flask, abort, g, jsonify, render_template, request, session
from sqlalchemy import inspect, text
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    is_test = app.config.get('TESTING', False)
    is_development = os.environ.get('APP_ENV', '').lower() == 'development'
    secret_key = os.environ.get('SECRET_KEY', '')
    if not is_test and not is_development and (
        len(secret_key) < 32
        or secret_key == 'dev-secret-key-change-in-production'
    ):
        raise RuntimeError(
            'Set SECRET_KEY to a random value of at least 32 characters for non-development deployments.'
        )

    db.init_app(app)
    login_manager.init_app(app)

    from app.main.routes import main
    from app.auth.routes import auth
    from app.api.routes import api

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')

    @app.context_processor
    def inject_csrf_token():
        token = session.get('_csrf_token')
        if token is None:
            token = secrets.token_urlsafe(32)
            session['_csrf_token'] = token
        return {'csrf_token': token}

    @app.before_request
    def validate_csrf_token():
        if app.testing:
            return None
        if request.method not in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            return None
        expected = session.get('_csrf_token')
        supplied = request.headers.get('X-CSRFToken') or request.form.get('_csrf_token')
        if expected and supplied and compare_digest(expected, supplied):
            return None
        if request.path.startswith('/api/'):
            return jsonify({'error': 'CSRF validation failed'}), 400
        return render_template(
            'error.html',
            status_code=400,
            message='This form has expired. Reload the page and try again.',
        ), 400

    @app.after_request
    def add_security_and_cache_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
            "form-action 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self'; connect-src 'self'"
        )

        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'
        else:
            response.headers['Cache-Control'] = 'no-store'

        return response

    # ------------------------------------------------------------------ #
    # Ensure DB tables exist once per container instance.                 #
    # Critical for Vercel serverless where each instance has fresh /tmp.  #
    # Optimized with flask.g to avoid per-request overhead.              #
    # ------------------------------------------------------------------ #
    @app.before_request
    def ensure_db():
        # Skip if already checked in this request context
        if getattr(g, '_db_created', False):
            return
        # Skip if already initialized for this app instance
        if getattr(app, '_db_initialized', False):
            g._db_created = True
            return
        try:
            db.create_all()
            _migrate_task_columns()
            app._db_initialized = True
            g._db_created = True
        except Exception as e:
            db.session.rollback()
            app.logger.exception('Database initialization failed')
            abort(503)

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('error.html', status_code=404,
                               message='That page could not be found.'), 404

    @app.errorhandler(500)
    def internal_server_error(_error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Something went wrong. Please try again.'}), 500
        return render_template(
            'error.html',
            status_code=500,
            message='Something went wrong. Please try again.',
        ), 500

    @app.errorhandler(503)
    def service_unavailable(_error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Schedule Manager is temporarily unavailable.'}), 503
        return render_template(
            'error.html',
            status_code=503,
            message='Schedule Manager is temporarily unavailable. Please try again shortly.',
        ), 503

    return app


def _migrate_task_columns():
    """Add model columns to databases created by an earlier app version."""
    boolean_default = 'FALSE' if db.engine.dialect.name == 'postgresql' else '0'
    required_columns = {
        'is_recurring': f'BOOLEAN DEFAULT {boolean_default}',
        'recurrence_interval': 'INTEGER DEFAULT 1',
        'recurrence_unit': "VARCHAR(20) DEFAULT 'day'",
        'next_due_date': 'DATE',
        'reminder_days_ahead': 'INTEGER DEFAULT 1',
    }
    inspector = inspect(db.engine)
    if 'task' not in inspector.get_table_names():
        return

    existing_columns = {column['name'] for column in inspector.get_columns('task')}
    for column_name, definition in required_columns.items():
        if column_name not in existing_columns:
            db.session.execute(text(
                f'ALTER TABLE task ADD COLUMN {column_name} {definition}'
            ))
    db.session.commit()
