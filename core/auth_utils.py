"""
Authentication utilities for CredPoint.
Provides decorators and helpers for protecting routes.
"""

from functools import wraps
from flask import redirect, url_for, g


def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not authenticated.
    
    Usage:
        @routes.route('/dashboard')
        @login_required
        def dashboard_page():
            uid = g.uid
            ...
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.get('uid'):
            return redirect(url_for('routes.login_page'))
        return f(*args, **kwargs)
    return wrapper
