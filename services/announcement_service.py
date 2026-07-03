from app import supabase
from typing import List, Dict, Optional

def get_all_announcements() -> List[Dict]:
    """Fetch all announcements, ordered by pinned first, then newest."""
    response = supabase.table('announcements') \
        .select('*, users(name)') \
        .order('is_pinned', desc=True) \
        .order('created_at', desc=True) \
        .execute()
    return response.data

def get_announcement_by_id(announcement_id: str) -> Optional[Dict]:
    """Fetch a single announcement."""
    response = supabase.table('announcements').select('*').eq('id', announcement_id).execute()
    if response.data:
        return response.data[0]
    return None

def create_announcement(data: dict) -> bool:
    """Create a new announcement."""
    try:
        response = supabase.table('announcements').insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error creating announcement: {e}")
        return False

def update_announcement(announcement_id: str, data: dict) -> bool:
    """Update an existing announcement."""
    try:
        response = supabase.table('announcements').update(data).eq('id', announcement_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating announcement: {e}")
        return False

def delete_announcement(announcement_id: str) -> bool:
    """Delete an announcement."""
    try:
        response = supabase.table('announcements').delete().eq('id', announcement_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error deleting announcement: {e}")
        return False
