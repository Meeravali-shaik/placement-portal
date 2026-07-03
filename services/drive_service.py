from app import supabase
from typing import List, Dict, Optional
from datetime import datetime

def get_all_drives(status_filter: str = None) -> List[Dict]:
    """Fetch all placement drives, optionally filtering by status."""
    query = supabase.table('placement_drives').select('*, companies(company_name, logo_url)')
    if status_filter:
        query = query.eq('drive_status', status_filter)
    
    response = query.order('created_at', desc=True).execute()
    return response.data

def get_drive_by_id(drive_id: str) -> Optional[Dict]:
    """Fetch a single drive by ID."""
    response = supabase.table('placement_drives').select('*, companies(*)').eq('id', drive_id).execute()
    if response.data:
        return response.data[0]
    return None

def create_drive(data: dict) -> Optional[Dict]:
    """Create a new placement drive."""
    try:
        response = supabase.table('placement_drives').insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating drive: {e}")
        return None

def update_drive(drive_id: str, data: dict) -> bool:
    """Update an existing placement drive."""
    try:
        response = supabase.table('placement_drives').update(data).eq('id', drive_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating drive: {e}")
        return False

def delete_drive(drive_id: str) -> bool:
    """Delete a placement drive."""
    try:
        response = supabase.table('placement_drives').delete().eq('id', drive_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error deleting drive: {e}")
        return False

def get_eligible_students_for_drive(drive_id: str) -> List[Dict]:
    """
    Core Eligibility Engine.
    Fetches students who meet the criteria for a specific drive.
    """
    drive = get_drive_by_id(drive_id)
    if not drive:
        return []

    query = supabase.table('students').select('*, users(name, email)')
    
    # Apply eligibility filters
    if drive.get('min_cgpa'):
        query = query.gte('cgpa', drive['min_cgpa'])
        
    if drive.get('allowed_branches') and len(drive['allowed_branches']) > 0:
        query = query.in_('branch', drive['allowed_branches'])
        
    if drive.get('max_backlogs') is not None:
        query = query.lte('active_backlogs', drive['max_backlogs'])
        
    if drive.get('graduation_year'):
        query = query.eq('graduation_year', drive['graduation_year'])
        
    # Only consider students who are currently unplaced
    query = query.eq('placement_status', 'Unplaced')
    
    response = query.execute()
    return response.data
