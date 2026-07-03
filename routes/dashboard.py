from flask import Blueprint, render_template, session
from utils.decorators import login_required, roles_required
from services.analytics_service import get_super_admin_stats, get_placement_officer_stats, get_student_stats

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/super-admin')
@login_required
@roles_required('super_admin')
def super_admin():
    stats = get_super_admin_stats()
    return render_template('dashboard/super_admin.html', stats=stats)

@dashboard_bp.route('/placement-officer')
@login_required
@roles_required('placement_officer')
def placement_officer():
    stats = get_placement_officer_stats()
    return render_template('dashboard/placement_officer.html', stats=stats)

@dashboard_bp.route('/training-coordinator')
@login_required
@roles_required('training_coordinator')
def training_coordinator():
    stats = {
        'students_ready': 1200,
        'students_not_eligible': 220,
        'training_progress': 80
    }
    return render_template('dashboard/training_coordinator.html', stats=stats)

@dashboard_bp.route('/student')
@login_required
@roles_required('student')
def student():
    student_id = session.get('user_id')
    stats = get_student_stats(student_id)
    return render_template('dashboard/student.html', stats=stats)
