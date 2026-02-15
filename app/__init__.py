
from flask import Flask
from config import Config
from app.extensions import db, login_manager, scheduler
from apscheduler.schedulers.base import SchedulerAlreadyRunningError
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Scheduler fix for Vercel:
    # Vercel serverless functions have short lifecycles and may not support
    # persistent background threads well. We wrap this to be safe.
    try:
        scheduler.init_app(app)
        scheduler.start()
    except Exception as e:
        print(f"Scheduler failed to start (expected on serverless): {e}")
        pass

    # Register Blueprints
    from app.main.routes import main
    from app.auth.routes import auth
    from app.api.routes import api

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')

    with app.app_context():
        # Database Creation fix for Vercel:
        # On Vercel, we might not have permission to write to the file system everywhere.
        # We try to create the DB, but ensure it doesn't crash the app if it fails.
        try:
            db.create_all()
        except Exception as e:
            print(f"Database creation failed: {e}")
            # If DB creation fails, the app might still run but error on requests.
            # This is better than a 500 on startup.

    return app
