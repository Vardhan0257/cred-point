from flask import Flask, request, jsonify, g, render_template, session, redirect, url_for
from firebase_admin import auth  # Only use 'auth', no need to initialize Firebase here
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        g.uid = decoded_token['uid']
        g.user = decoded_token  # Fix: Populate g.user so routes don't crash
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
