from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decorators import login_required, roles_required
from services.drive_service import (
    get_all_drives, get_drive_by_id, create_drive, 
    update_drive, delete_drive, get_eligible_students_for_drive
)
from services.company_service import get_all_companies

drives_bp = Blueprint('drives', __name__)

@drives_bp.route('/')
@login_required
def list_drives():
    """List all placement drives."""
    status_filter = request.args.get('status')
    drives = get_all_drives(status_filter)
    return render_template('drives/list.html', drives=drives)

@drives_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def add_drive():
    """Create a new placement drive."""
    if request.method == 'POST':
        # Convert list of selected branches to array
        allowed_branches = request.form.getlist('allowed_branches')
        
        data = {
            'drive_name': request.form.get('drive_name'),
            'company_id': request.form.get('company_id'),
            'drive_date': request.form.get('drive_date') or None,
            'registration_start': request.form.get('registration_start') or None,
            'registration_end': request.form.get('registration_end') or None,
            'aptitude_test_date': request.form.get('aptitude_test_date') or None,
            'technical_interview_date': request.form.get('technical_interview_date') or None,
            'hr_interview_date': request.form.get('hr_interview_date') or None,
            'venue': request.form.get('venue'),
            'drive_status': request.form.get('drive_status', 'Upcoming'),
            'min_cgpa': request.form.get('min_cgpa', type=float) if request.form.get('min_cgpa') else None,
            'allowed_branches': allowed_branches if allowed_branches else None,
            'max_backlogs': request.form.get('max_backlogs', type=int) if request.form.get('max_backlogs') else None,
            'graduation_year': request.form.get('graduation_year', type=int) if request.form.get('graduation_year') else None,
            'required_skills': request.form.get('required_skills')
        }
        
        drive = create_drive(data)
        if drive:
            flash('Drive created successfully!', 'success')
            return redirect(url_for('drives.view_drive', drive_id=drive['id']))
        else:
            flash('Error creating drive.', 'danger')
            
    companies = get_all_companies()
    return render_template('drives/form.html', action='Create', companies=companies)

@drives_bp.route('/edit/<uuid:drive_id>', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def edit_drive(drive_id):
    """Edit an existing placement drive."""
    drive = get_drive_by_id(str(drive_id))
    if not drive:
        flash('Drive not found.', 'warning')
        return redirect(url_for('drives.list_drives'))
        
    if request.method == 'POST':
        allowed_branches = request.form.getlist('allowed_branches')
        
        data = {
            'drive_name': request.form.get('drive_name'),
            'company_id': request.form.get('company_id'),
            'drive_date': request.form.get('drive_date') or None,
            'registration_start': request.form.get('registration_start') or None,
            'registration_end': request.form.get('registration_end') or None,
            'aptitude_test_date': request.form.get('aptitude_test_date') or None,
            'technical_interview_date': request.form.get('technical_interview_date') or None,
            'hr_interview_date': request.form.get('hr_interview_date') or None,
            'venue': request.form.get('venue'),
            'drive_status': request.form.get('drive_status', 'Upcoming'),
            'min_cgpa': request.form.get('min_cgpa', type=float) if request.form.get('min_cgpa') else None,
            'allowed_branches': allowed_branches if allowed_branches else None,
            'max_backlogs': request.form.get('max_backlogs', type=int) if request.form.get('max_backlogs') else None,
            'graduation_year': request.form.get('graduation_year', type=int) if request.form.get('graduation_year') else None,
            'required_skills': request.form.get('required_skills')
        }
        
        if update_drive(str(drive_id), data):
            flash('Drive updated successfully!', 'success')
            return redirect(url_for('drives.view_drive', drive_id=drive_id))
        else:
            flash('Error updating drive.', 'danger')
            
    companies = get_all_companies()
    return render_template('drives/form.html', action='Edit', drive=drive, companies=companies)

@drives_bp.route('/<uuid:drive_id>')
@login_required
def view_drive(drive_id):
    """View details of a specific drive."""
    drive = get_drive_by_id(str(drive_id))
    if not drive:
        flash('Drive not found.', 'warning')
        return redirect(url_for('drives.list_drives'))
    return render_template('drives/view.html', drive=drive)

@drives_bp.route('/delete/<uuid:drive_id>', methods=['POST'])
@login_required
@roles_required('super_admin')
def do_delete_drive(drive_id):
    """Delete a drive."""
    if delete_drive(str(drive_id)):
        flash('Drive deleted successfully!', 'success')
    else:
        flash('Error deleting drive.', 'danger')
    return redirect(url_for('drives.list_drives'))

@drives_bp.route('/<uuid:drive_id>/eligible-students')
@login_required
@roles_required('super_admin', 'placement_officer', 'training_coordinator')
def eligible_students(drive_id):
    """View students eligible for a specific drive."""
    drive = get_drive_by_id(str(drive_id))
    if not drive:
        flash('Drive not found.', 'warning')
        return redirect(url_for('drives.list_drives'))
        
    students = get_eligible_students_for_drive(str(drive_id))
    return render_template('drives/eligible_students.html', drive=drive, students=students)
