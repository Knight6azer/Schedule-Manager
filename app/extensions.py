
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.login_message = ''
login_manager.login_message_category = 'info'

# 'basic' prevents session token regeneration on every request.
# 'strong' causes login loops on stateless/serverless platforms like Vercel.
login_manager.session_protection = 'basic'
