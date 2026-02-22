
import os

basedir = os.path.abspath(os.path.dirname(__file__))

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

    # -------------------------------------------------------------------
    # Database
    # Vercel's filesystem is read-only except /tmp, which is ephemeral.
    # For production persistence, set DATABASE_URL to a hosted DB.
    # -------------------------------------------------------------------
    if os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/schedule_v2.db'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'schedule_v2.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
