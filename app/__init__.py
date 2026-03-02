
from flask import Flask
from config import Config
from app.extensions import db, login_manager
import traceback


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

    # ------------------------------------------------------------------ #
    # Ensure DB tables exist on EVERY request.                            #
    # This is critical for Vercel serverless: the GET (register page) and #
    # the POST (form submit) can land on DIFFERENT container instances,   #
    # each with a fresh /tmp — so we cannot rely on tables created during #
    # app factory startup alone.                                          #
    # ------------------------------------------------------------------ #
    @app.before_request
    def ensure_db():
        try:
            db.create_all()
        except Exception:
            # Log so Vercel function logs show the root cause if something
            # is genuinely wrong with the DB connection.
            traceback.print_exc()

    return app
