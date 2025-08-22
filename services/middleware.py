from flask import session, redirect, url_for, g
from functools import wraps
from services.models import get_user  # import your get_user function

def firebase_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'uid' not in session:
            return redirect(url_for('routes.login_page'))

        g.uid = session['uid']
        user_data = get_user(g.uid)

        if not user_data:
            # User record missing, maybe log them out or redirect
            return redirect(url_for('routes.login_page'))

        g.user = user_data
        return f(*args, **kwargs)
    return decorated
