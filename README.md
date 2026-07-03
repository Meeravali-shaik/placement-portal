# Placement Portal

A Flask-based placement management portal for colleges and training teams. The application supports role-based access for students, training coordinators, placement officers, and super admins, with Supabase used as the backend data store.

## Features

- Role-based authentication and dashboard routing
- Student profile management
- Placement drive creation, editing, listing, and eligibility checks
- Student drive applications and withdrawal
- Admin view of drive applicants and application status updates
- Company and announcement management
- Analytics and reports dashboards
- Supabase-backed persistence for users, students, companies, drives, applications, and announcements

## Roles

The application currently uses these roles:

- `student`
- `training_coordinator`
- `placement_officer`
- `super_admin`

Public registration creates only student accounts. Admin accounts should be created by the super admin from the admin user-creation page.

## Project Structure

```text
app.py
config.py
requirements.txt
seed_dummy_data.py
database/schema.sql
routes/
services/
templates/
utils/
```

## Prerequisites

- Python 3.10+ recommended
- A Supabase project
- Supabase `URL` and `service role / API` key values

## Installation

1. Create and activate a virtual environment.

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root.

   ```env
   SECRET_KEY=your-secret-key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-key
   ```

## Database Setup

1. Open your Supabase SQL editor.
2. Run the schema in [database/schema.sql](database/schema.sql).
3. Confirm the required tables exist:
   - `users`
   - `students`
   - `companies`
   - `placement_drives`
   - `applications`
   - `announcements`
   - `notifications`

If you want sample data, inspect and run [seed_dummy_data.py](seed_dummy_data.py) after configuring Supabase credentials.

## Running Locally

Start the app from the project root:

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Deployment Notes

The app is currently configured for development in `app.py`, so before production deployment you should:

- Set `SECRET_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY` in your hosting environment
- Disable Flask debug mode for production execution
- Run behind a production WSGI server such as Gunicorn
- Keep Supabase credentials out of source control
- Ensure the database schema is migrated before first launch

Example production command on Linux-based hosts:

```bash
gunicorn --factory app:create_app
```

## Authentication and Access Control

The app uses session-based auth and role guards.

- Students can register publicly.
- Super admins can create staff/admin accounts from the admin user-creation page.
- Role-aware redirects send users to the correct dashboard after login.
- Protected routes use decorators in [utils/decorators.py](utils/decorators.py).

## Main Modules

- `routes/auth.py` - login, logout, public registration, and super-admin user creation
- `routes/dashboard.py` - role-based dashboards
- `routes/students.py` - student listing, profile management, and admin student management
- `routes/companies.py` - company management
- `routes/drives.py` - placement drives and eligibility checks
- `routes/applications.py` - student applications and admin applicant management
- `routes/announcements.py` - announcements
- `routes/reports.py` - analytics and reports

## Common Workflows

### Student

- Register an account
- Log in
- Complete or update profile
- View placement drives
- Apply for a drive
- Track your applications

### Training Coordinator

- Review student readiness and training progress
- View eligible students for a drive
- Monitor student support needs

### Placement Officer / Super Admin

- Create and manage placement drives
- Manage companies
- Review applicants for each drive
- Update application statuses
- Create staff/admin accounts

## Troubleshooting

- If login fails, verify the Supabase environment variables and that the `users` table is populated.
- If pages redirect unexpectedly, check the `user_role` stored in session and confirm the role name matches the schema.
- If the app cannot connect to Supabase, re-check the project URL and key.
- If templates render strangely, confirm you are on the latest version of the dashboard templates.

## Security Checklist Before Deployment

- Public signup must stay student-only
- Admin roles must be created only by super admins
- Debug mode should be disabled in production
- Supabase keys must be stored in environment variables only
- Database schema should match the app before launch

## License

No license file is currently included. Add one if you plan to distribute the project publicly.