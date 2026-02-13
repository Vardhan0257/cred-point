# CredPoint Auth - Quick Reference

## 🎯 Auth Architecture Summary

**No localStorage. No frontend state. Backend controls everything.**

```
Register → Firebase Auth (client) → /session-login → Session Cookie → Dashboard
Login    → Firebase Auth (client) → /session-login → Session Cookie → Dashboard
Refresh  → Session Cookie + verify → g.uid available → Routes work instantly
Logout   → Clear session → Redirect login
```

---

## 📄 Key Files

| File | Purpose |
|------|---------|
| `auth_utils.py` | Auth decorators (`@login_required`) |
| `app.py` | Session management + `/session-login` endpoint |
| `routes.py` | Protected routes with `@firebase_required` |
| `templates/login.html` | Firebase login + session creation |
| `templates/register.html` | Form validation + Firebase creation |

---

## 🔒 Protected Routes

All routes using `@firebase_required` decorator are protected:

```python
from services.middleware import firebase_required

@routes_bp.route('/dashboard')
@firebase_required
def dashboard_page():
    uid = g.uid  # ✅ User ID available
    # Your code here
```

**What happens:**
1. User not logged in → Redirects to `/login_page`
2. User logged in → `g.uid` and `g.user` set
3. Route executes normally

---

## 🚀 Adding New Protected Routes

```python
from services.middleware import firebase_required

@routes_bp.route('/my-new-endpoint')
@firebase_required
def my_new_endpoint():
    uid = g.uid
    user = g.user  # Full decoded Firebase token
    
    # Access user data
    user_email = user['email']
    
    return render_template('my_template.html')
```

---

## ✅ What's Already Implemented

### Backend (Flask)
- ✅ `/session-login` endpoint - validates Firebase token
- ✅ `@firebase_required` decorator - protects routes
- ✅ Session cookie hardening - HTTPONLY, SECURE, SAMESITE
- ✅ Persistent sessions - survive browser restart
- ✅ `/logout` endpoint - clears session
- ✅ Auto Firestore user creation - on registration

### Frontend (Templates)
- ✅ Login page - Firebase auth + session creation
- ✅ Register page - form + Firebase creation + auto-login
- ✅ Error handling - shows Firebase errors
- ✅ Redirect to dashboard - on success

### Security
- ✅ No localStorage/sessionStorage
- ✅ Secure HTTPOnly cookies
- ✅ CSRF protection (flask_wtf)
- ✅ Rate limiting on register
- ✅ Token verification on every request

---

## 🔄 Login Flow Diagram

```
User                Firebase              Flask
 |                    |                     |
 | Email/Password     |                     |
 |-------------------->                     |
 |                    |                     |
 |<-------- ID Token --|                     |
 |                    |                     |
 |     POST /session-login (token)         |
 |----------------------------------------->|
 |                    |              Verify Token
 |                    |                     |
 |                    |          Create Session
 |                    |                     |
 |<------------ 200 OK -------------------|
 |                    |                     |
 | Set Session Cookie |                     |
 |<-----------'Set-Cookie'----|
 |                    |                     |
 | Redirect /dashboard        |
 |                    |                     |

Result: User at /dashboard with g.uid available
```

---

## 🧪 Quick Test Checklist

### Register
- [ ] Go to `/register`
- [ ] Fill form + submit
- [ ] Should land at `/dashboard`
- [ ] Refresh page - should stay logged in

### Login
- [ ] Go to `/login`
- [ ] Enter credentials
- [ ] Should land at `/dashboard`
- [ ] Refresh page - should stay logged in

### Protected Route
- [ ] Logout
- [ ] Try accessing `/dashboard` directly
- [ ] Should redirect to `/login`

### Error Handling
- [ ] Register with invalid email → error shown
- [ ] Register with password mismatch → error shown
- [ ] Login with wrong password → Firebase error shown

---

## 🔐 Session Security

```python
# All configured in app.py:
SESSION_COOKIE_HTTPONLY = True       # Can't access from JS
SESSION_COOKIE_SECURE = True         # HTTPS only (prod)
SESSION_COOKIE_SAMESITE = 'Lax'     # CSRF protection
PERMANENT_SESSION_LIFETIME = 1 hour  # Auto logout
```

### What this means:
- ✅ Session can't be stolen by XSS
- ✅ Session requires HTTPS (prevents MITM)
- ✅ Browser won't send session to cross-origin
- ✅ Session expires after inactivity

---

## 📚 Common Tasks

### "I need to protect a new route"
```python
@routes_bp.route('/my-endpoint')
@firebase_required
def my_endpoint():
    uid = g.uid
    # ...
```

### "I need to get user data in a route"
```python
from services.models import get_user

@routes_bp.route('/profile')
@firebase_required
def profile():
    user = get_user(g.uid)
    return render_template('profile.html', user=user)
```

### "I need to access user in template"
```html
{% if current_user.uid %}
    <p>Logged in: {{ current_user.uid }}</p>
{% endif %}
```

### "User should not be able to access after logout"
```python
# Logout route clears session
@routes_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.login_page'))
```

---

## 🚨 Common Mistakes (AVOID)

❌ **Don't** store auth token in localStorage
```python
# WRONG - localStorage can be stolen
localStorage.setItem('token', idToken)
```

❌ **Don't** check `g.uid` without decorator
```python
# WRONG - g.uid won't exist without @firebase_required
@routes_bp.route('/dashboard')  # Missing @firebase_required
def dashboard():
    uid = g.uid  # Crashes!
```

❌ **Don't** create Firebase user in Flask
```python
# WRONG - Firebase user created on client
auth.create_user(email, password)  # Unnecessary
```

✅ **Do** use session-based auth
```python
# CORRECT - Session cookie is the source of truth
session['uid'] = decoded_token['uid']
```

---

## 📊 Current Auth Status

| Component | Status | Notes |
|-----------|--------|-------|
| Firebase Auth | ✅ Ready | Creates users |
| Session Cookies | ✅ Ready | Persistent, secure |
| Protected Routes | ✅ Ready | Use @firebase_required |
| Login Flow | ✅ Ready | Instant dashboard redirect |
| Register Flow | ✅ Ready | Auto Firestore creation |
| Logout | ✅ Ready | Clears session |
| Error Handling | ✅ Ready | Shows Firebase errors |
| Rate Limiting | ✅ Ready | 3/hour on register |

---

## 🆘 Need Help?

1. Check `AUTH_IMPLEMENTATION.md` for detailed docs
2. Check Flask/Firebase error logs
3. Check browser console for client-side errors
4. Verify Firebase project config
5. Verify Firestore rules allow user creation

---

## 📝 Version History

- **v1.0** - Professional auth architecture implemented
  - Session-based authentication
  - Firebase identity + Flask session
  - Secure cookies (HTTPONLY, SECURE, SAMESITE)
  - Auto Firestore user creation
  - Protected routes with decorators
