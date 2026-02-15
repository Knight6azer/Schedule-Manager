
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler

db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
