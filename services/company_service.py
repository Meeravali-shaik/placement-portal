from app import supabase
from typing import List, Dict, Optional

def get_all_companies(search_query: str = None) -> List[Dict]:
    """Fetch all companies, optionally filtering by name."""
    query = supabase.table('companies').select('*')
    if search_query:
        query = query.ilike('company_name', f'%{search_query}%')
    
    response = query.order('created_at', desc=True).execute()
    return response.data

def get_company_by_id(company_id: str) -> Optional[Dict]:
    """Fetch a single company by ID."""
    response = supabase.table('companies').select('*').eq('id', company_id).execute()
    if response.data:
        return response.data[0]
    return None

def create_company(data: dict) -> Optional[Dict]:
    """Create a new company record."""
    try:
        response = supabase.table('companies').insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating company: {e}")
        return None

def update_company(company_id: str, data: dict) -> bool:
    """Update an existing company record."""
    try:
        response = supabase.table('companies').update(data).eq('id', company_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating company: {e}")
        return False

def delete_company(company_id: str) -> bool:
    """Delete a company."""
    try:
        response = supabase.table('companies').delete().eq('id', company_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error deleting company: {e}")
        return False
