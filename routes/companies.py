from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decorators import login_required, roles_required
from services.company_service import get_all_companies, get_company_by_id, create_company, update_company, delete_company

companies_bp = Blueprint('companies', __name__)

@companies_bp.route('/')
@login_required
def list_companies():
    """List all companies (accessible by all roles, but actions differ)."""
    search = request.args.get('search')
    companies = get_all_companies(search)
    return render_template('companies/list.html', companies=companies)

@companies_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def add_company():
    """Add a new company."""
    if request.method == 'POST':
        data = {
            'company_name': request.form.get('company_name'),
            'website': request.form.get('website'),
            'industry': request.form.get('industry'),
            'location': request.form.get('location'),
            'job_role': request.form.get('job_role'),
            'package': request.form.get('package'),
            'ctc': request.form.get('ctc', type=float) if request.form.get('ctc') else None,
            'bond_details': request.form.get('bond_details'),
            'job_description': request.form.get('job_description'),
            'required_skills': request.form.get('required_skills'),
            'contact_person': request.form.get('contact_person'),
            'hr_email': request.form.get('hr_email'),
            'hr_phone': request.form.get('hr_phone')
        }
        
        company = create_company(data)
        if company:
            flash('Company added successfully!', 'success')
            return redirect(url_for('companies.view_company', company_id=company['id']))
        else:
            flash('Error adding company.', 'danger')
            
    return render_template('companies/form.html', action='Add')

@companies_bp.route('/edit/<uuid:company_id>', methods=['GET', 'POST'])
@login_required
@roles_required('super_admin', 'placement_officer')
def edit_company(company_id):
    """Edit an existing company."""
    company = get_company_by_id(str(company_id))
    if not company:
        flash('Company not found.', 'warning')
        return redirect(url_for('companies.list_companies'))
        
    if request.method == 'POST':
        data = {
            'company_name': request.form.get('company_name'),
            'website': request.form.get('website'),
            'industry': request.form.get('industry'),
            'location': request.form.get('location'),
            'job_role': request.form.get('job_role'),
            'package': request.form.get('package'),
            'ctc': request.form.get('ctc', type=float) if request.form.get('ctc') else None,
            'bond_details': request.form.get('bond_details'),
            'job_description': request.form.get('job_description'),
            'required_skills': request.form.get('required_skills'),
            'contact_person': request.form.get('contact_person'),
            'hr_email': request.form.get('hr_email'),
            'hr_phone': request.form.get('hr_phone')
        }
        
        if update_company(str(company_id), data):
            flash('Company updated successfully!', 'success')
            return redirect(url_for('companies.view_company', company_id=company_id))
        else:
            flash('Error updating company.', 'danger')
            
    return render_template('companies/form.html', action='Edit', company=company)

@companies_bp.route('/<uuid:company_id>')
@login_required
def view_company(company_id):
    """View details of a specific company."""
    company = get_company_by_id(str(company_id))
    if not company:
        flash('Company not found.', 'warning')
        return redirect(url_for('companies.list_companies'))
    return render_template('companies/view.html', company=company)

@companies_bp.route('/delete/<uuid:company_id>', methods=['POST'])
@login_required
@roles_required('super_admin')
def do_delete_company(company_id):
    """Delete a company."""
    if delete_company(str(company_id)):
        flash('Company deleted successfully!', 'success')
    else:
        flash('Error deleting company.', 'danger')
    return redirect(url_for('companies.list_companies'))
