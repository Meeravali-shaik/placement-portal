from app import supabase
from typing import List, Dict, Optional

def apply_for_drive(student_id: str, drive_id: str) -> bool:
    """Apply for a placement drive."""
    try:
        data = {
            'student_id': student_id,
            'drive_id': drive_id,
            'status': 'Applied'
        }
        response = supabase.table('applications').insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error applying for drive: {e}")
        return False

def withdraw_application(student_id: str, drive_id: str) -> bool:
    """Withdraw an application."""
    try:
        response = supabase.table('applications').delete().eq('student_id', student_id).eq('drive_id', drive_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error withdrawing application: {e}")
        return False

def get_student_applications(student_id: str) -> List[Dict]:
    """Get all applications for a specific student."""
    response = supabase.table('applications') \
        .select('*, placement_drives(*, companies(company_name, logo_url))') \
        .eq('student_id', student_id) \
        .order('applied_at', desc=True) \
        .execute()
    return response.data

def get_drive_applicants(drive_id: str, status_filter: str = None) -> List[Dict]:
    """Get all students who applied for a specific drive."""
    query = supabase.table('applications') \
        .select('*, students(*, users(name, email))') \
        .eq('drive_id', drive_id)
        
    if status_filter:
        query = query.eq('status', status_filter)
        
    response = query.order('applied_at', desc=False).execute()
    return response.data

def update_application_status(application_id: str, new_status: str) -> bool:
    """Update the status of an application."""
    try:
        response = supabase.table('applications') \
            .update({'status': new_status}) \
            .eq('id', application_id) \
            .execute()
            
        # If status is Selected, we should ideally also update the student's placement status to 'Placed'
        if new_status == 'Selected' and response.data:
            student_id = response.data[0]['student_id']
            supabase.table('students').update({'placement_status': 'Placed'}).eq('id', student_id).execute()
            
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating application status: {e}")
        return False

def has_applied(student_id: str, drive_id: str) -> bool:
    """Check if a student has already applied for a drive."""
    response = supabase.table('applications') \
        .select('id') \
        .eq('student_id', student_id) \
        .eq('drive_id', drive_id) \
        .execute()
    return len(response.data) > 0
