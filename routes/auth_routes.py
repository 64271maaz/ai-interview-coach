from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import db, User

# Blueprint = routes ka ek chota "module", jo baad mein app.py mein register hoga
auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.')
            return redirect(url_for('auth.login'))

        # Naya user banao
        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)   # password hash hoke save hoga

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!')
            return redirect(url_for('dashboard.dashboard_view'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))