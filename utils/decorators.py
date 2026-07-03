from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            # Normalize role for flexible matching (case-insensitive, hyphen/underscore agnostic)
            user_role = session.get('user_role') or ''
            normalized_user_role = user_role.replace('-', '_').lower()
            normalized_roles = [r.replace('-', '_').lower() for r in roles]
            if normalized_user_role not in normalized_roles:
                flash('You do not have permission to access this page.', 'danger')
                # Redirect to their specific dashboard based on role
                # Use normalized role for redirect decisions
                user_role = session.get('user_role') or ''
                nr = user_role.replace('-', '_').lower()
                if nr == 'super_admin':
                    return redirect(url_for('dashboard.super_admin'))
                elif nr == 'placement_officer':
                    return redirect(url_for('dashboard.placement_officer'))
                elif nr == 'training_coordinator':
                    return redirect(url_for('dashboard.training_coordinator'))
                elif nr == 'student':
                    return redirect(url_for('dashboard.student'))
                else:
                    return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
