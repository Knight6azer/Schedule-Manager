
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
from app.models import User
from app.extensions import db

auth = Blueprint('auth', __name__)


def is_safe_url(target):
    """Prevent open redirects and login-loop redirects."""
    if not target:
        return False
    ref_url  = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    same_origin = (test_url.scheme in ('http', 'https') and
                   ref_url.netloc == test_url.netloc)
    not_login   = '/auth/login' not in test_url.path
    return same_origin and not_login


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email    = (request.form.get('email')    or '').strip()
        password =  request.form.get('password') or ''

        if not email or not password:
            flash('Please fill in all fields.', 'warning')
            return render_template('login.html')

        try:
            user = User.query.filter_by(email=email).first()
        except Exception:
            flash('Database unavailable — please try again in a moment.', 'warning')
            return render_template('login.html')

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.index'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email    = (request.form.get('email')    or '').strip()
        password =  request.form.get('password') or ''

        # ── Input validation (before any DB access) ──────────────────────
        if not username or not email or not password:
            flash('All fields are required.', 'warning')
            return render_template('register.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'warning')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'warning')
            return render_template('register.html')

        # ── Uniqueness checks (give friendly messages, not a generic DB error) ──
        try:
            if User.query.filter_by(email=email).first():
                flash('That email is already registered. Try logging in instead.', 'danger')
                return render_template('register.html')

            if User.query.filter_by(username=username).first():
                flash('That username is already taken. Please choose another.', 'danger')
                return render_template('register.html')
        except Exception as e:
            print(f"[REGISTER] DB query error: {e}")
            flash('Database unavailable — please try again in a moment.', 'warning')
            return render_template('register.html')

        # ── Create the user ───────────────────────────────────────────────
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[REGISTER] Commit error: {e}")
            import traceback; traceback.print_exc()
            flash('Could not create account — please try again.', 'danger')
            return render_template('register.html')

        flash('Account created! You can now sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
