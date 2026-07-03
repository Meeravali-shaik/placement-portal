from flask import Blueprint, render_template
from utils.decorators import login_required, roles_required
from services.analytics_service import get_super_admin_stats, get_analytics_breakdown

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/analytics')
@login_required
@roles_required('super_admin', 'placement_officer', 'training_coordinator')
def analytics_dashboard():
    """View analytics dashboard with charts."""
    stats = get_super_admin_stats()
    charts = get_analytics_breakdown()
    return render_template('reports/analytics.html', stats=stats, charts=charts)
