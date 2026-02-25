
import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))


def _get_db_uri():
    """
    Resolve the database URI at app startup (not at module import time).

    Priority:
      1. DATABASE_URL env var (Neon, Supabase, any external Postgres)
         — SQLAlchemy 1.4+ requires 'postgresql://', but Neon gives 'postgres://'.
           We fix that automatically here.
      2. SQLite in /tmp if running on Vercel (ephemeral — for fallback only)
      3. Local SQLite file for development
    """
    url = os.environ.get('DATABASE_URL')
    if url:
        # Neon (and Heroku) give 'postgres://' — SQLAlchemy 1.4+ needs 'postgresql://'
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    if os.environ.get('VERCEL'):
        return 'sqlite:////tmp/schedule_v2.db'
    return 'sqlite:///' + os.path.join(basedir, 'schedule_v2.db')


class Config:
    # -------------------------------------------------------------------
    # Security: SECRET_KEY must be set as a Vercel env var for sessions
    # to survive across serverless cold-starts. Falls back to a fixed
    # dev key locally (never change this fallback to something random,
    # or local sessions will break on every restart).
    # -------------------------------------------------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # -------------------------------------------------------------------
    # Session cookie hardening — required for Vercel (HTTPS).
    # Without Secure=True + SameSite=Lax, browsers reject the cookie on
    # HTTPS redirects, which causes the login loop.
    # -------------------------------------------------------------------
    SESSION_COOKIE_SECURE = bool(os.environ.get('VERCEL'))   # True on Vercel, False locally
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = bool(os.environ.get('VERCEL'))
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # SESSION_PERMANENT pins cookies to an explicit expiry date.
    # Without this, cookies are 'browser-session' cookies which browsers
    # discard on Vercel's serverless redirects, causing the login loop.
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # -------------------------------------------------------------------
    # Database — resolved at startup via helper to avoid class-level
    # env-var evaluation timing issues.
    # -------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLAlchemy connection pool settings — required for Neon PostgreSQL.
    # Neon closes idle connections after 5 minutes; without pool_pre_ping
    # SQLAlchemy will try to reuse a dead connection and throw an error.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,   # recycle before Neon's 5-min idle timeout
    }

    SCHEDULER_API_ENABLED = True
