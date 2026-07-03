from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, roles_required
from services.auth_service import authenticate_user, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        # Redirect based on role if already logged in
        role = session.get('user_role')
        if role == 'super_admin': return redirect(url_for('dashboard.super_admin'))
        if role == 'placement_officer': return redirect(url_for('dashboard.placement_officer'))
        if role == 'training_coordinator': return redirect(url_for('dashboard.training_coordinator'))
        if role == 'student': return redirect(url_for('dashboard.student'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')

        user = authenticate_user(email, password)

        if user:
            session.permanent = True if remember else False
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['user_name'] = user['name']

            flash('Logged in successfully.', 'success')
            
            # Redirect to their specific dashboard based on role
            role = user['role']
            if role == 'super_admin': return redirect(url_for('dashboard.super_admin'))
            if role == 'placement_officer': return redirect(url_for('dashboard.placement_officer'))
            if role == 'training_coordinator': return redirect(url_for('dashboard.training_coordinator'))
            if role == 'student': return redirect(url_for('dashboard.student'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        # Basic validation
        if not (name and email and password):
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        role = 'student'
        # Create user via service
        user = create_user(name, email, password, role)
        if user:
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Failed to create account. Email may already be registered.', 'danger')
    return render_template('register.html')

@auth_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin')
def create_user_account():
    allowed_roles = ('super_admin', 'placement_officer', 'training_coordinator', 'student')

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') or 'student'

        if not (name and email and password):
            flash('All fields are required.', 'danger')
            return render_template('auth/create_user.html', allowed_roles=allowed_roles)

        if role not in allowed_roles:
            flash('Invalid role selected.', 'danger')
            return render_template('auth/create_user.html', allowed_roles=allowed_roles)

        user = create_user(name, email, password, role)
        if user:
            flash('User account created successfully.', 'success')
            return redirect(url_for('dashboard.super_admin'))

        flash('Failed to create user. Email may already be registered.', 'danger')

    return render_template('auth/create_user.html', allowed_roles=allowed_roles)

