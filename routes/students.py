from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decorators import login_required, roles_required
from services.student_service import get_all_students, get_student_by_id, update_student_profile, create_student

students_bp = Blueprint('students', __name__)

@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def add_student():
    """Add a new student account and profile."""
    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'roll_number': request.form.get('roll_number'),
            'registration_number': request.form.get('registration_number'),
            'phone_number': request.form.get('phone_number'),
            'gender': request.form.get('gender'),
            'date_of_birth': request.form.get('date_of_birth'),
            'branch': request.form.get('branch'),
            'department': request.form.get('department'),
            'graduation_year': request.form.get('graduation_year', type=int) if request.form.get('graduation_year') else None,
            'cgpa': request.form.get('cgpa', type=float) if request.form.get('cgpa') else None,
            'active_backlogs': request.form.get('active_backlogs', type=int) if request.form.get('active_backlogs') else 0,
            'address': request.form.get('address'),
            'skills': request.form.get('skills'),
            'linkedin_url': request.form.get('linkedin_url'),
            'github_url': request.form.get('github_url'),
            'placement_status': request.form.get('placement_status') or 'Unplaced',
        }

        student = create_student(data)
        if student:
            flash('Student added successfully!', 'success')
            return redirect(url_for('students.view_student', student_id=student['id']))

        flash('Failed to add student. Check the details and try again.', 'danger')

    return render_template('students/form.html', action='Add', student=None)

@students_bp.route('/')
@login_required
@roles_required('super_admin', 'placement_officer', 'training_coordinator')
def list_students():
    """List all students for admins/officers."""
    # Handle filters
    filters = {
        'branch': request.args.get('branch'),
        'min_cgpa': request.args.get('min_cgpa'),
        'graduation_year': request.args.get('graduation_year'),
        'placement_status': request.args.get('placement_status')
    }
    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}
    
    students = get_all_students(filters)
    return render_template('students/list.html', students=students)

@students_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@roles_required('student')
def my_profile():
    """Student views or edits their own profile."""
    student_id = session.get('user_id')
    
    if request.method == 'POST':
        # Extract data from form
        data = {
            'roll_number': request.form.get('roll_number'),
            'registration_number': request.form.get('registration_number'),
            'full_name': request.form.get('full_name'),
            'phone_number': request.form.get('phone_number'),
            'gender': request.form.get('gender'),
            'date_of_birth': request.form.get('date_of_birth'),
            'branch': request.form.get('branch'),
            'department': request.form.get('department'),
            'graduation_year': request.form.get('graduation_year', type=int) if request.form.get('graduation_year') else None,
            'cgpa': request.form.get('cgpa', type=float) if request.form.get('cgpa') else None,
            'active_backlogs': request.form.get('active_backlogs', type=int) if request.form.get('active_backlogs') else 0,
            'address': request.form.get('address'),
            'skills': request.form.get('skills'),
            'linkedin_url': request.form.get('linkedin_url'),
            'github_url': request.form.get('github_url'),
            'email': session.get('user_name') # Just to keep email updated if needed, though usually fixed
        }
        
        if update_student_profile(student_id, data):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile. Please try again.', 'danger')
            
        return redirect(url_for('students.my_profile'))
        
    student = get_student_by_id(student_id)
    return render_template('students/profile.html', student=student)

@students_bp.route('/<uuid:student_id>')
@login_required
@roles_required('super_admin', 'placement_officer', 'training_coordinator')
def view_student(student_id):
    """Admin/Officer views a specific student."""
    student = get_student_by_id(str(student_id))
    if not student:
        flash('Student not found.', 'warning')
        return redirect(url_for('students.list_students'))
    return render_template('students/view.html', student=student)
