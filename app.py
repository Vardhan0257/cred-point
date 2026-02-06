from flask import Flask, request, jsonify, g, render_template, session, redirect, url_for
from firebase_admin import auth  # Only use 'auth', no need to initialize Firebase here
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import os
import logging

app = Flask(__name__)

# Require a secret key in production; do not fall back to a weak default.
secret = os.environ.get('FLASK_SECRET_KEY')
if not secret:
    # allow local development if FLASK_ENV=development
    if os.environ.get('FLASK_ENV') != 'development':
        raise RuntimeError('FLASK_SECRET_KEY must be set in the environment for production')
    secret = 'dev-secret-key'

app.config['SECRET_KEY'] = secret
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Session cookie hardening
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.environ.get('SESSION_LIFETIME_HOURS', '1')))

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable CSRF protection for forms and state-changing requests
csrf = CSRFProtect()
csrf.init_app(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.environ.get('RATE_LIMIT_DEFAULT', '200 per day, 50 per hour')],
    storage_uri=os.environ.get('RATE_LIMIT_STORAGE', 'memory://')
)

# Secure headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains' if app.config['SESSION_COOKIE_SECURE'] else ''
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response


# =====================
# Session Login Endpoint
# =====================
@app.route('/session-login', methods=['POST'])
def session_login():
    data = request.get_json()
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({'error': 'ID token missing'}), 400
    try:
        decoded_token = auth.verify_id_token(id_token)
        # Store minimal session data; do not treat the raw ID token as the canonical session.
        session.permanent = True
        session['firebase_id_token'] = id_token
        session['uid'] = decoded_token['uid']
        return jsonify({'message': 'Login successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Invalid token: {str(e)}'}), 401

# =====================
# Middleware: Verify Firebase ID Token (only for protected routes)
# =====================
@app.before_request
def verify_token():
    public_endpoints = [
        'routes.index',
        'routes.login_page',
        'routes.register_page',
        'session_login',
        'static'
    ]
    if request.endpoint in public_endpoints or request.endpoint is None:
        return

    id_token = session.get('firebase_id_token')
    if not id_token:
        return redirect(url_for('routes.login_page'))

    try:
        decoded_token = auth.verify_id_token(id_token)
        # minimal g context for routes
        g.uid = decoded_token.get('uid')
        g.user = decoded_token
    except Exception:
        session.clear()
        return redirect(url_for('routes.login_page'))

# =====================
# Context processor
# =====================
@app.context_processor
def inject_user():
    return dict(current_user={'uid': g.get('uid', None)})

# =====================
# Register routes — imported last to avoid circular import
# =====================
from routes import routes_bp
app.register_blueprint(routes_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True', host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
