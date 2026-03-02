
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


def _get_db_uri():
    """
    Priority:
      1. DATABASE_URL env var (Neon, Supabase, any external Postgres)
      2. SQLite in /tmp  for Vercel (ephemeral fallback)
      3. Local SQLite file for development
    """
    url = os.environ.get('DATABASE_URL')
    if url:
        # Neon / Heroku give 'postgres://' — SQLAlchemy 1.4+ needs 'postgresql://'
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    if os.environ.get('VERCEL'):
        return 'sqlite:////tmp/schedule_v2.db'
    return 'sqlite:///' + os.path.join(basedir, 'schedule_v2.db')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Harden session cookies for HTTPS (Vercel) without breaking local dev
    SESSION_COOKIE_SECURE   = bool(os.environ.get('VERCEL'))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE   = bool(os.environ.get('VERCEL'))
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    SESSION_PERMANENT        = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    SQLALCHEMY_DATABASE_URI      = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # pool_pre_ping prevents dead-connection errors with Neon's 5-min idle timeout
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
