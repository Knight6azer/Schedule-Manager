
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
from app.models import User
from app.extensions import db

auth = Blueprint('auth', __name__)


def is_safe_url(target):
    """Ensure the redirect target is on the same host (prevents open redirects)
    and is NOT the login page itself (prevents the redirect loop)."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    # Must be same scheme + host, and must not loop back to login
    same_origin = (test_url.scheme in ('http', 'https') and
                   ref_url.netloc == test_url.netloc)
    not_login = '/auth/login' not in test_url.path
    return same_origin and not_login


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = User.query.filter_by(email=email).first()
        except Exception:
            # DB not ready (e.g. Vercel cold start with empty /tmp DB)
            flash('Database is initialising — please try again in a moment.', 'warning')
            return render_template('login.html')

        if user and user.check_password(password):
            login_user(user)
            # Validate 'next' to prevent open redirects AND redirect loops
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'danger')
                return redirect(url_for('auth.register'))

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Could not create account — database error. Please try again.', 'danger')
            return render_template('register.html')

        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
