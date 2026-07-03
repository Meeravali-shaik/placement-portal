from flask import Flask, redirect, url_for
from config import Config
from supabase import create_client, Client
import inspect
import httpx
import os


def _patch_httpx_proxy_compatibility() -> None:
    signature = inspect.signature(httpx.Client.__init__)
    if "proxy" in signature.parameters or "proxies" not in signature.parameters:
        return

    original_init = httpx.Client.__init__

    def patched_init(self, *args, proxy=None, **kwargs):
        if proxy is not None and "proxies" not in kwargs:
            kwargs["proxies"] = proxy
        return original_init(self, *args, **kwargs)

    httpx.Client.__init__ = patched_init

# Initialize Supabase client
url: str = Config.SUPABASE_URL or ""
key: str = Config.SUPABASE_KEY or ""
_patch_httpx_proxy_compatibility()
supabase: Client = create_client(url, key) if url and key else None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.students import students_bp
    from routes.companies import companies_bp
    from routes.drives import drives_bp
    from routes.applications import applications_bp
    from routes.announcements import announcements_bp
    from routes.reports import reports_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(companies_bp, url_prefix='/companies')
    app.register_blueprint(drives_bp, url_prefix='/drives')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(announcements_bp, url_prefix='/announcements')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login')) # Assuming auth blueprint is named 'auth'

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
