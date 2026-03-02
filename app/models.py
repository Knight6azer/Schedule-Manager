
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    # Guard against DB errors (e.g. Vercel cold starts where tables may not exist yet).
    # db.session.get() is the SQLAlchemy 2.0-compatible replacement for Query.get().
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(20), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    tasks         = db.relationship('Task', backref='author', lazy=True,
                                    cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Task(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    priority      = db.Column(db.String(20), default='Medium')   # High · Medium · Low
    category      = db.Column(db.String(50), default='General')  # Work · Personal · Study · Health
    status        = db.Column(db.String(20), default='Pending')  # Pending · In Progress · Completed
    due_date      = db.Column(db.Date, nullable=True)
    reminder_time = db.Column(db.DateTime, nullable=True)
    # Use timezone-aware UTC timestamps (datetime.utcnow is deprecated in Python 3.12)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id'           : self.id,
            'title'        : self.title,
            'description'  : self.description,
            'priority'     : self.priority,
            'category'     : self.category,
            'status'       : self.status,
            'due_date'     : self.due_date.isoformat() if self.due_date else None,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None,
            'created_at'   : self.created_at.isoformat() if self.created_at else None,
            'updated_at'   : self.updated_at.isoformat() if self.updated_at else None,
            'user_id'      : self.user_id,
        }

    def __repr__(self):
        return f"Task('{self.title}', '{self.due_date}')"
