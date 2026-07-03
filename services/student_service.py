from app import supabase
from typing import List, Dict, Optional
from services.auth_service import create_user

def get_all_students(filters: dict = None) -> List[Dict]:
    """Fetch all students, optionally with filters."""
    query = supabase.table('students').select('*, users(name, email)')
    
    if filters:
        if filters.get('branch'):
            query = query.eq('branch', filters['branch'])
        if filters.get('min_cgpa'):
            query = query.gte('cgpa', filters['min_cgpa'])
        if filters.get('graduation_year'):
            query = query.eq('graduation_year', filters['graduation_year'])
        if filters.get('placement_status'):
            query = query.eq('placement_status', filters['placement_status'])
            
    response = query.execute()
    return response.data

def get_student_by_id(student_id: str) -> Optional[Dict]:
    """Fetch a single student by their user ID."""
    response = supabase.table('students').select('*, users(name, email)').eq('id', student_id).execute()
    if response.data:
        return response.data[0]
    return None

def update_student_profile(student_id: str, data: dict) -> bool:
    """Update a student's profile."""
    try:
        response = supabase.table('students').update(data).eq('id', student_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating student: {e}")
        return False

def create_student(data: dict) -> Optional[Dict]:
    """Create a new student user and profile record."""
    try:
        full_name = data.get('full_name') or data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not (full_name and email and password):
            return None

        user = create_user(full_name, email, password, 'student')
        if not user:
            return None

        student_payload = {
            'id': user['id'],
            'roll_number': data.get('roll_number'),
            'registration_number': data.get('registration_number'),
            'full_name': full_name,
            'email': email,
            'phone_number': data.get('phone_number'),
            'gender': data.get('gender'),
            'date_of_birth': data.get('date_of_birth'),
            'branch': data.get('branch'),
            'department': data.get('department'),
            'graduation_year': data.get('graduation_year'),
            'cgpa': data.get('cgpa'),
            'active_backlogs': data.get('active_backlogs', 0),
            'address': data.get('address'),
            'skills': data.get('skills'),
            'linkedin_url': data.get('linkedin_url'),
            'github_url': data.get('github_url'),
            'placement_status': data.get('placement_status') or 'Unplaced',
        }

        response = supabase.table('students').insert(student_payload).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating student: {e}")
        return None

def get_eligible_students(drive_criteria: dict) -> List[Dict]:
    """Fetch students eligible for a specific drive based on criteria."""
    query = supabase.table('students').select('*')
    
    if drive_criteria.get('min_cgpa'):
        query = query.gte('cgpa', drive_criteria['min_cgpa'])
    if drive_criteria.get('allowed_branches') and len(drive_criteria['allowed_branches']) > 0:
        query = query.in_('branch', drive_criteria['allowed_branches'])
    if drive_criteria.get('max_backlogs') is not None:
        query = query.lte('active_backlogs', drive_criteria['max_backlogs'])
    if drive_criteria.get('graduation_year'):
        query = query.eq('graduation_year', drive_criteria['graduation_year'])
        
    query = query.eq('placement_status', 'Unplaced')
        
    response = query.execute()
    return response.data
