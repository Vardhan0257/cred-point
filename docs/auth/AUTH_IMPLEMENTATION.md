# CredPoint Professional Auth Architecture

## ✅ IMPLEMENTATION COMPLETE

This document outlines the production-grade authentication architecture implemented for CredPoint.

---

## 🔥 AUTH FLOW ARCHITECTURE

```
Register Flow:
  1. User fills form (name, email, password)
  2. Form validation on Flask
  3. SessionStorage: pending_user data
  4. Firebase creates auth user on client
  5. GET Firebase ID token
  6. POST /session-login with token
  7. Flask verifies token
  8. Flask creates Firestore profile
  9. Session cookie stored (secure, httponly)
  10. Redirect to /dashboard

Login Flow:
  1. User enters email/password
  2. Firebase signIn auth
  3. GET Firebase ID token
  4. POST /session-login with token
  5. Flask verifies token
  6. Session cookie stored
  7. Redirect to /dashboard

Protected Route Access:
  1. Request to protected endpoint
  2. @firebase_required decorator checks session
  3. Verifies firebase_id_token from session
  4. Sets g.uid from session
  5. Loads user from Firestore
  6. Route executes with g.uid context

Refresh/Persistent Login:
  1. Page reload
  2. Session cookie sent automatically
  3. @before_request middleware runs
  4. Token verified
  5. g.uid set from session
  6. No delay - session already valid
```

---

## 📄 FILES MODIFIED

### 1. `auth_utils.py` (NEW)
**Purpose:** Centralized auth decorators for route protection

```python
from auth_utils import login_required

@routes.route('/protected')
@login_required
def protected_route():
    uid = g.uid
    # ...
```

**Available Decorators:**
- `@login_required` - Redirects to login if not authenticated

---

### 2. `app.py`
**Updated:** Session-login endpoint now handles new user creation

**Changes:**
- `/session-login` now checks for `pending_user` in session
- If new registration, creates Firestore profile automatically
- Sets `session.permanent = True` for persistent cookies
- Session cookies: HTTPONLY, SAMESITE=Lax, SECURE (production)

**Key Settings:**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 1 hour (configurable)
```

---

### 3. `routes.py`
**Updated:** Register route now handles client-side Firebase auth

**Changes:**
- `/register` validates form and stores `pending_user` in session
- No longer creates Firebase user (client does this)
- Returns `{"status": "ready_for_firebase"}` on success
- Client then creates Firebase user and calls `/session-login`

**Existing Protected Routes:**
All routes already use `@firebase_required` decorator from middleware.py

```python
@routes_bp.route('/dashboard', methods=['GET'])
@firebase_required
def dashboard_page():
    uid = g.uid  # Already available
    # ...
```

---

### 4. `templates/login.html`
**Updated:** Streamlined Firebase login integration

**Flow:**
1. User submits email/password
2. Firebase `signInWithEmailAndPassword()`
3. Get Firebase ID token
4. POST `/session-login` with token
5. On success, redirect to `/dashboard`

**Error Handling:**
- Shows Firebase auth errors
- Clears and displays error messages

---

### 5. `templates/register.html`
**Updated:** Client-side Firebase user creation

**Flow:**
1. User enters form (name, email, password, confirm)
2. Form submits to Flask (validates and stores pending_user)
3. Firebase creates user with email/password
4. Get Firebase ID token
5. POST `/session-login` with token
6. Flask creates Firestore profile
7. Redirect to dashboard

**Error Handling:**
- Form validation errors displayed
- Firebase errors caught and shown
- Graceful failure messages

---

## 🧭 IMPLEMENTATION GUIDE

### Using `@login_required` Decorator

For custom protected routes, use:

```python
from auth_utils import login_required

@routes_bp.route('/my-route')
@login_required
def my_protected_route():
    uid = g.uid  # User UID available here
    user_data = get_user(uid)
    # ...
```

### Accessing Current User

In any route (protected or not):
```python
from flask import g

# After @firebase_required, g.uid is available
uid = g.uid
user = g.user  # Full Firebase decoded token
```

### In Templates

```html
{% if current_user.uid %}
    <!-- User is logged in -->
    <p>Welcome, {{ current_user.uid }}</p>
{% else %}
    <!-- User not logged in -->
{% endif %}
```

### Logout

```python
@routes_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('routes.login_page'))
```

---

## 🔒 SECURITY FEATURES

### Session Cookies
- ✅ **HttpOnly**: Cannot be accessed by JavaScript
- ✅ **Secure**: Only sent over HTTPS (production)
- ✅ **SameSite=Lax**: CSRF protection
- ✅ **Permanent**: Survives browser restart
- ✅ **Timeout**: 1 hour (configurable)

### Token Verification
- ✅ Firebase ID tokens verified on every protected request
- ✅ Token expiration checked by Firebase
- ✅ Invalid tokens redirect to login
- ✅ Session cleared on auth failure

### No Frontend Hacks
- ✅ No localStorage for auth
- ✅ No localStorage for tokens
- ✅ Backend controls all auth state
- ✅ Client only handles UI feedback

### Rate Limiting
- Register route: 3 attempts per hour
- Applies to `/register` endpoint

---

## 🧪 TESTING CHECKLIST

### Register Flow
- [ ] Fill registration form
- [ ] Click "Create Account"
- [ ] Firebase creates user
- [ ] Firestore profile created
- [ ] Lands in dashboard
- [ ] Session persists on refresh

### Login Flow
- [ ] Enter email/password
- [ ] Click "Sign In"
- [ ] Firebase validates credentials
- [ ] Lands in dashboard
- [ ] Session persists on refresh + close/reopen browser

### Protected Routes
- [ ] Access `/dashboard` without login → redirects to login
- [ ] After login, `/dashboard` loads
- [ ] `g.uid` available in route

### Logout
- [ ] Click logout
- [ ] Session cleared
- [ ] Accessing protected route → login page

### Error Handling
- [ ] Invalid email format → shown in form
- [ ] Password mismatch → shown in form
- [ ] Firebase auth error → shown in UI
- [ ] Expired session → redirects to login

---

## 🌍 ENVIRONMENT VARIABLES

```bash
# Flask
FLASK_SECRET_KEY=<strong-secret-key>
FLASK_ENV=development  # or production

# Session
SESSION_COOKIE_SECURE=True  # False for local dev
SESSION_COOKIE_SAMESITE=Lax
SESSION_LIFETIME_HOURS=1

# Rate Limiting
RATE_LIMIT_DEFAULT='200 per day, 50 per hour'
RATE_LIMIT_STORAGE='memory://'

# Firebase Config (in templates)
firebase_config={
    apiKey: "...",
    authDomain: "...",
    projectId: "..."
}
```

---

## 📊 USER FLOW SUMMARY

### First Time User
```
1. Click "Sign Up"
2. Fill form (name, email, pwd)
3. Submit → Form validates, stores pending_user
4. Firebase creates auth user
5. Get JWT token
6. POST /session-login
7. Flask verifies, creates Firestore profile
8. Session cookie set
9. → Dashboard
```

### Returning User
```
1. Click "Sign In"
2. Enter email/pwd
3. Submit → Firebase verifies
4. Get JWT token
5. POST /session-login
6. Session cookie set
7. → Dashboard
```

### After Page Refresh
```
1. Session cookie sent in request
2. @before_request middleware checks
3. Verifies firebase_id_token
4. g.uid set from session
5. Protected routes accessible
6. No auth delay
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Pre-Deployment Checklist
- [ ] `FLASK_SECRET_KEY` set to strong random string
- [ ] `SESSION_COOKIE_SECURE=True` (HTTPS enabled)
- [ ] HTTPS certificate installed
- [ ] Firebase rules updated
- [ ] Firestore rules restrict access
- [ ] Rate limiting configured
- [ ] Error logging configured
- [ ] Backup/recovery plan documented

### Deployment Commands
```bash
export FLASK_SECRET_KEY=$(openssl rand -hex 32)
export FLASK_ENV=production
export SESSION_COOKIE_SECURE=True

flask run --bind 0.0.0.0 --port 8080
```

---

## 🐛 TROUBLESHOOTING

### "Session login failed"
- Check Firebase config in templates
- Verify `/session-login` endpoint accessible
- Check browser console for Firebase errors

### "Invalid token"
- Firebase ID token expired (try logout/login again)
- Firebase project misconfigured
- Check Firebase rules

### "Redirect loop"
- Clear session and cookies
- Verify `public_endpoints` list in app.py
- Check `@firebase_required` decorator applied

### User persists after logout
- Check `session.clear()` in logout route
- Verify cookies cleared
- Check browser dev tools → Application → Cookies

---

## 📝 NOTES

- No auth state kept in localStorage
- No JWT in localStorage
- Session cookie is the canonical auth mechanism
- Backend always validates tokens
- Frontend is stateless for auth
- Firebase is used only for identity verification
- Firestore is used for user profiles

This is production SaaS architecture.
