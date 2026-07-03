from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decorators import login_required, roles_required
from services.announcement_service import (
    get_all_announcements, get_announcement_by_id, 
    create_announcement, update_announcement, delete_announcement
)

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('/')
@login_required
def list_announcements():
    """List all announcements."""
    announcements = get_all_announcements()
    return render_template('announcements/list.html', announcements=announcements)

@announcements_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def add_announcement():
    """Create a new announcement."""
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'content': request.form.get('content'),
            'is_pinned': request.form.get('is_pinned') == 'on',
            'created_by': session.get('user_id')
        }
        
        if create_announcement(data):
            flash('Announcement published successfully!', 'success')
            return redirect(url_for('announcements.list_announcements'))
        else:
            flash('Error creating announcement.', 'danger')
            
    return render_template('announcements/form.html', action='Create')

@announcements_bp.route('/edit/<uuid:announcement_id>', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def edit_announcement(announcement_id):
    """Edit an existing announcement."""
    announcement = get_announcement_by_id(str(announcement_id))
    if not announcement:
        flash('Announcement not found.', 'warning')
        return redirect(url_for('announcements.list_announcements'))
        
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'content': request.form.get('content'),
            'is_pinned': request.form.get('is_pinned') == 'on'
        }
        
        if update_announcement(str(announcement_id), data):
            flash('Announcement updated successfully!', 'success')
            return redirect(url_for('announcements.list_announcements'))
        else:
            flash('Error updating announcement.', 'danger')
            
    return render_template('announcements/form.html', action='Edit', announcement=announcement)

@announcements_bp.route('/delete/<uuid:announcement_id>', methods=['POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def do_delete_announcement(announcement_id):
    """Delete an announcement."""
    if delete_announcement(str(announcement_id)):
        flash('Announcement deleted.', 'success')
    else:
        flash('Error deleting announcement.', 'danger')
    return redirect(url_for('announcements.list_announcements'))
