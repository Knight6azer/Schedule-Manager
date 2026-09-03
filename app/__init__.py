
from flask import Flask, g, request
from sqlalchemy import inspect, text
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.main.routes import main
    from app.auth.routes import auth
    from app.api.routes import api

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')

    @app.after_request
    def add_security_and_cache_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
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
            app.logger.error(f'Database initialization failed: {e}')

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
