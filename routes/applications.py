from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decorators import login_required, roles_required
from services.application_service import (
    apply_for_drive, withdraw_application, get_student_applications,
    get_drive_applicants, update_application_status, has_applied
)
from services.drive_service import get_drive_by_id

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/apply/<uuid:drive_id>', methods=['POST'])
@login_required
@roles_required('student')
def apply(drive_id):
    """Student applies to a drive."""
    student_id = session.get('user_id')
    
    if has_applied(student_id, str(drive_id)):
        flash('You have already applied for this drive.', 'warning')
        return redirect(url_for('drives.view_drive', drive_id=drive_id))
        
    if apply_for_drive(student_id, str(drive_id)):
        flash('Successfully applied for the drive!', 'success')
    else:
        flash('Failed to apply. Please try again.', 'danger')
        
    return redirect(url_for('applications.my_applications'))

@applications_bp.route('/withdraw/<uuid:drive_id>', methods=['POST'])
@login_required
@roles_required('student')
def withdraw(drive_id):
    """Student withdraws application."""
    student_id = session.get('user_id')
    
    if withdraw_application(student_id, str(drive_id)):
        flash('Successfully withdrawn from the drive.', 'success')
    else:
        flash('Failed to withdraw. Please try again.', 'danger')
        
    return redirect(url_for('applications.my_applications'))

@applications_bp.route('/my-applications')
@login_required
@roles_required('student')
def my_applications():
    """Student views their applications."""
    student_id = session.get('user_id')
    applications = get_student_applications(student_id)
    return render_template('applications/student_list.html', applications=applications)

@applications_bp.route('/drive/<uuid:drive_id>')
@login_required
@roles_required('super_admin', 'placement_officer')
def drive_applicants(drive_id):
    """Admin/Officer views applicants for a specific drive."""
    drive = get_drive_by_id(str(drive_id))
    if not drive:
        flash('Drive not found.', 'warning')
        return redirect(url_for('drives.list_drives'))
        
    status_filter = request.args.get('status')
    applicants = get_drive_applicants(str(drive_id), status_filter)
    
    return render_template('applications/drive_applicants.html', drive=drive, applicants=applicants)

@applications_bp.route('/update-status/<uuid:application_id>', methods=['POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def update_status(application_id):
    """Admin/Officer updates an application's status."""
    new_status = request.form.get('status')
    drive_id = request.form.get('drive_id') # Pass this for redirect
    
    valid_statuses = ['Applied', 'Shortlisted', 'Aptitude Cleared', 'Technical Cleared', 'HR Cleared', 'Selected', 'Rejected', 'Withdrawn']
    if new_status not in valid_statuses:
        flash('Invalid status provided.', 'danger')
        return redirect(url_for('applications.drive_applicants', drive_id=drive_id))
        
    if update_application_status(str(application_id), new_status):
        flash(f'Application status updated to {new_status}.', 'success')
    else:
        flash('Error updating status.', 'danger')
        
    return redirect(url_for('applications.drive_applicants', drive_id=drive_id))
