
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler

db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Use 'basic' instead of the default 'strong'.
# 'strong' regenerates session tokens on every request, which on Vercel's
# serverless/stateless architecture causes sessions to be invalidated
# mid-flight, producing the login redirect loop.
login_manager.session_protection = 'basic'
