from app import supabase
from typing import Dict
from collections import Counter
from datetime import datetime


def _safe_student_rows() -> list[dict]:
    response = supabase.table('students').select('branch, placement_status, created_at').execute()
    return response.data or []


def _month_labels(count: int = 6) -> list[str]:
    labels = []
    now = datetime.utcnow()
    for offset in range(count - 1, -1, -1):
        month_index = now.month - offset
        year = now.year
        while month_index <= 0:
            month_index += 12
            year -= 1
        labels.append(f"{datetime(year, month_index, 1).strftime('%b %Y')}")
    return labels


def _monthly_registration_counts(rows: list[dict], count: int = 6) -> tuple[list[str], list[int]]:
    buckets = Counter()
    for row in rows:
        created_at = row.get('created_at')
        if not created_at:
            continue
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            buckets[dt.strftime('%b %Y')] += 1
        except Exception:
            continue

    labels = _month_labels(count)
    values = [buckets.get(label, 0) for label in labels]
    return labels, values


def _branch_distribution(rows: list[dict]) -> tuple[list[str], list[int], list[int]]:
    branch_totals = Counter()
    branch_placed = Counter()

    for row in rows:
        branch = row.get('branch') or 'Unknown'
        branch_totals[branch] += 1
        if row.get('placement_status') == 'Placed':
            branch_placed[branch] += 1

    ordered_branches = [branch for branch, _ in branch_totals.most_common()]
    total_values = [branch_totals[branch] for branch in ordered_branches]
    placed_values = [branch_placed.get(branch, 0) for branch in ordered_branches]
    return ordered_branches, total_values, placed_values

def get_super_admin_stats() -> Dict:
    """Aggregates data for the Super Admin Dashboard."""
    # Note: For MVP we do simple counts. In a real large-scale app, we might use Supabase RPCs.
    try:
        print("Fetching student count …")
        students = supabase.table('students').select('id', count='exact').execute()
        print("Fetching company count …")
        companies = supabase.table('companies').select('id', count='exact').execute()
        print("Fetching drive count …")
        drives = supabase.table('placement_drives').select('id', count='exact').execute()
        print("Fetching placed‑student count …")
        placed_students = (
            supabase
            .table('students')
            .select('id', count='exact')
            .eq('placement_status', 'Placed')
            .execute()
        )
        
        # Calculate max and avg CTC from companies offering jobs
        ctc_data = supabase.table('companies').select('ctc').execute()
        ctc_values = [float(row['ctc']) for row in (ctc_data.data or []) if row.get('ctc') is not None]
        
        highest_package = f"{max(ctc_values):.2f} LPA" if ctc_values else "N/A"
        avg_package = f"{(sum(ctc_values) / len(ctc_values)):.2f} LPA" if ctc_values else "N/A"
        
        student_rows = _safe_student_rows()
        total_students = students.count or 0
        total_placed = placed_students.count or 0
        placement_percentage = round((total_placed / total_students * 100), 2) if total_students > 0 else 0
        branch_labels, branch_total_values, branch_placed_values = _branch_distribution(student_rows)
        registration_labels, registration_values = _monthly_registration_counts(student_rows)

        return {
            'total_students': total_students,
            'total_companies': companies.count or 0,
            'total_drives': drives.count or 0,
            'total_offers': total_placed, # Assuming 1 offer per placed student for MVP
            'placement_percentage': placement_percentage,
            'highest_package': highest_package,
            'average_package': avg_package,
            'branch_labels': branch_labels,
            'branch_total_values': branch_total_values,
            'branch_placed_values': branch_placed_values,
            'registration_labels': registration_labels,
            'registration_values': registration_values,
        }
    except Exception as e:
        print(f"Error fetching super admin stats: {e}")
        return {
            'total_students': 0, 'total_companies': 0, 'total_drives': 0, 
            'total_offers': 0, 'placement_percentage': 0, 
            'highest_package': 'N/A', 'average_package': 'N/A',
            'branch_labels': [], 'branch_total_values': [], 'branch_placed_values': [],
            'registration_labels': [], 'registration_values': [],
        }

def get_placement_officer_stats() -> Dict:
    try:
        students = supabase.table('students').select('id', count='exact').execute()
        ongoing_drives = supabase.table('placement_drives').select('id', count='exact').eq('drive_status', 'Ongoing').execute()
        companies = supabase.table('companies').select('id', count='exact').execute()
        
        return {
            'students_registered': students.count or 0,
            'drives_running': ongoing_drives.count or 0,
            'companies_visiting': companies.count or 0,
            'upcoming_interviews': 0 # Placeholder
        }
    except Exception:
        return {'students_registered': 0, 'drives_running': 0, 'companies_visiting': 0, 'upcoming_interviews': 0}

def get_student_stats(student_id: str) -> Dict:
    try:
        student = supabase.table('students').select('*').eq('id', student_id).execute()
        applied = supabase.table('applications').select('id', count='exact').eq('student_id', student_id).execute()
        
        # Calculate profile completion (simplified)
        s_data = student.data[0] if student.data else {}
        fields_to_check = ['full_name', 'phone_number', 'branch', 'cgpa', 'skills', 'resume_url', 'date_of_birth', 'address']
        filled = sum(1 for field in fields_to_check if s_data.get(field))
        completion = int((filled / len(fields_to_check)) * 100)
        
        return {
            'profile_completion': completion,
            'eligible_drives': 0, # Could compute based on eligibility engine
            'applied_drives': applied.count or 0,
            'placement_status': s_data.get('placement_status', 'Unplaced')
        }
    except Exception:
        return {'profile_completion': 0, 'eligible_drives': 0, 'applied_drives': 0, 'placement_status': 'Unplaced'}


def get_analytics_breakdown() -> Dict:
    """Return chart-ready analytics data derived from students."""
    rows = _safe_student_rows()
    branch_labels, branch_total_values, branch_placed_values = _branch_distribution(rows)
    registration_labels, registration_values = _monthly_registration_counts(rows)
    unplaced_values = [total - placed for total, placed in zip(branch_total_values, branch_placed_values)]

    return {
        'branch_labels': branch_labels,
        'branch_total_values': branch_total_values,
        'branch_placed_values': branch_placed_values,
        'branch_unplaced_values': unplaced_values,
        'registration_labels': registration_labels,
        'registration_values': registration_values,
    }
