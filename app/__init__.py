
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

    with app.app_context():
        try:
            db.create_all()
        except Exception:
            print("CRITICAL: Database creation failed — load_user will return None for all sessions!")
            traceback.print_exc()

    return app
