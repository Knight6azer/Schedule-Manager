
from flask import Flask, g, request
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
            app._db_initialized = True
            g._db_created = True
        except Exception as e:
            app.logger.error(f'Database initialization failed: {e}')

    return app
