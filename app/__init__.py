
from flask import Flask
from config import Config
from app.extensions import db, login_manager, scheduler
from apscheduler.schedulers.base import SchedulerAlreadyRunningError

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    scheduler.init_app(app)
    
    try:
        scheduler.start()
    except SchedulerAlreadyRunningError:
        pass

    # Register Blueprints
    from app.main.routes import main
    from app.auth.routes import auth
    from app.api.routes import api

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app
