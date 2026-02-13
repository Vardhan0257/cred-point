# 🧪 Authentication Testing Guide

Complete step-by-step guide to test the new authentication system.

---

## 📋 Pre-Test Checklist

Before testing, ensure:
- [ ] Flask app can start without errors
- [ ] Firebase config is set in environment
- [ ] Firestore is accessible
- [ ] Browser cookies are enabled
- [ ] JavaScript is enabled

---

## 🧪 TEST 1: Registration Flow

### Steps:
1. Start Flask app: `python app.py`
2. Navigate to: `http://localhost:8080/register`
3. Fill registration form:
   - Name: "Test User"
   - Email: "test@example.com" (CREATE NEW - must not exist)
   - Password: "TestPassword123!"
   - Confirm: "TestPassword123!"
4. Click "Create Account"

### Expected Result:
- ✅ Form validates (no red errors below fields)
- ✅ No error message in UI
- ✅ Browser redirects to `/dashboard`
- ✅ Dashboard displays (certifications, activities, etc.)
- ✅ User is logged in

### If It Fails:
- Check browser console for JavaScript errors
- Check Flask logs for exceptions
- Verify Firebase config in template
- Ensure email doesn't already exist

---

## 🧪 TEST 2: Persistence After Refresh

### Steps:
1. From test 1, user should be at `/dashboard`
2. Press F5 to refresh page
3. Wait for page to reload

### Expected Result:
- ✅ Dashboard still visible (no redirect to login)
- ✅ Page loads quickly (no delay)
- ✅ User remains logged in
- ✅ Session cookie present in dev tools

### If It Fails:
- Check browser cookies (DevTools → Application → Cookies)
- Verify session cookie is set and not expired
- Check Flask `SESSION_COOKIE_HTTPONLY` setting

---

## 🧪 TEST 3: Login Flow

### Steps:
1. Logout first (if logged in): navigate to `/logout`
2. Navigate to: `http://localhost:8080/login`
3. Enter credentials:
   - Email: "test@example.com" (from test 1)
   - Password: "TestPassword123!"
4. Click "Sign In"

### Expected Result:
- ✅ No error message shown
- ✅ Browser redirects to `/dashboard`
- ✅ Dashboard loads instantly
- ✅ User data visible

### If It Fails:
- Verify email/password match registration
- Check Firefox/Chrome console for Firebase errors
- Verify Firebase project allows email+password auth

---

## 🧪 TEST 4: Protected Routes

### Steps:
1. Logout: navigate to `/logout`
2. Verify session cleared (check DevTools cookies)
3. Try accessing protected route: `http://localhost:8080/dashboard`

### Expected Result:
- ✅ Redirected to `/login` page automatically
- ✅ Cannot access dashboard without login

### If It Fails:
- Check `@firebase_required` decorator on route
- Verify session is actually cleared on logout
- Check Flask `before_request` middleware

---

## 🧪 TEST 5: Error Handling - Wrong Password

### Steps:
1. Navigate to `/login`
2. Enter:
   - Email: "test@example.com"
   - Password: "WrongPassword123"
3. Click "Sign In"

### Expected Result:
- ✅ Error message shown: "Firebase: Error (auth/wrong-password)"
- ✅ User stays on login page
- ✅ Error message is red and visible

### If It Fails:
- Check browser console for error
- Verify Firebase project allows email auth

---

## 🧪 TEST 6: Error Handling - Invalid Email

### Steps:
1. Navigate to `/login`
2. Enter:
   - Email: "nonexistent@example.com"
   - Password: "anything"
3. Click "Sign In"

### Expected Result:
- ✅ Error message shown: "Firebase: Error (auth/user-not-found)"
- ✅ User stays on login page

---

## 🧪 TEST 7: Error Handling - Registration Validation

### Steps:
1. Navigate to `/register`
2. Fill form with invalid data:
   - Name: "Test"
   - Email: "notanemail"
   - Password: "weak"
   - Confirm: "different"
3. Click "Create Account"

### Expected Result:
- ✅ Form shows validation errors below fields
- ✅ User stays on registration page
- ✅ Firebase user not created

### If It Fails:
- Check form validators in `forms.py`
- Verify Flask-WTF is configured

---

## 🧪 TEST 8: Logout

### Steps:
1. Login with test user
2. Verify at `/dashboard`
3. Click logout button (or navigate `/logout`)

### Expected Result:
- ✅ Session cleared (can check DevTools)
- ✅ Redirected to login page
- ✅ "You have been logged out." message shown
- ✅ Cannot access `/dashboard` anymore

### If It Fails:
- Check logout route implementation
- Verify `session.clear()` is called
- Verify redirect to login page

---

## 🧪 TEST 9: Multiple Tabs/Windows

### Steps:
1. Login in tab 1
2. Open same app in tab 2 (new tab at localhost:8080)
3. Navigate to `/dashboard` in tab 2

### Expected Result:
- ✅ Tab 2 shows dashboard immediately (session shared)
- ✅ Both tabs have same session

### If It Fails:
- Sessions might be tab-specific (browser issue, not app issue)
- This is acceptable behavior

---

## 🧪 TEST 10: Browser Close and Reopen

### Steps:
1. Login to app
2. Close browser completely
3. Reopen browser and go to `localhost:8080`

### Expected Result:
- ✅ Session cookie deleted (persistent=False)
- ✅ Redirected to login
- ✅ Must login again

### Alternative (If persistent login desired):
- Check if `session.permanent = True` in `/session-login`
- Should survive browser close if permanent

---

## 🧪 TEST 11: User Data in Routes

### Steps:
1. Login successfully
2. Navigate to `/profile` (or any protected route)

### In Route Code:
```python
@routes_bp.route('/profile')
@firebase_required
def profile():
    print(f"g.uid: {g.uid}")  # Should print user ID
    print(f"g.user: {g.user}")  # Should print Firebase data
```

### Expected Result:
- ✅ `g.uid` contains user's Firebase UID
- ✅ `g.user` contains decoded Firebase token
- ✅ User data available to route

### If It Fails:
- Check `@firebase_required` decorator sets g.uid
- Verify `before_request` middleware runs

---

## 🧪 TEST 12: Session Timeout (Optional)

### Steps:
1. Login successfully
2. Set `PERMANENT_SESSION_LIFETIME = 1 minute` (for testing)
3. Wait 2 minutes without navigating
4. Try accessing protected route

### Expected Result:
- ✅ Session expired
- ✅ Redirected to login
- ✅ Must login again

### Note:
- For production, set to 1-2 hours
- Check `app.py` for configuration

---

## 📊 Test Summary

| Test | Category | Status |
|------|----------|--------|
| Registration | Core | ⬜ |
| Persistence | Session | ⬜ |
| Login | Core | ⬜ |
| Protected Routes | Security | ⬜ |
| Wrong Password | Error | ⬜ |
| Invalid Email | Error | ⬜ |
| Registration Validation | Error | ⬜ |
| Logout | Core | ⬜ |
| Multiple Tabs | Edge Case | ⬜ |
| Browser Close | Session | ⬜ |
| Route Data Access | Integration | ⬜ |
| Session Timeout | Security | ⬜ |

**Mark with ✅ as tests pass**

---

## 🐛 Debugging Checklist

If tests fail, check these in order:

### 1. Flask App Debug
```python
# Add to app.py temporarily:
@app.before_request
def debug_session():
    print(f"Session UID: {session.get('uid')}")
    print(f"g.uid: {g.get('uid')}")
```

### 2. Browser Console
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab for failed requests
- Look for Firebase error messages

### 3. Flask Logs
```
python app.py 2>&1 | tee app.log
```

### 4. Session Cookies
- DevTools → Application → Cookies
- Look for `session` cookie
- Check expiration time
- Verify HttpOnly flag is set

### 5. Firebase Config
- Verify `firebase_config` in template
- Check Firebase project settings
- Ensure authentication method enabled

### 6. Firestore
- Check if user document created in Firestore
- Verify Firestore rules allow creation
- Check user data is stored correctly

---

## ✅ Full Test Checklist

When all tests pass:

- [ ] Registration creates user and logs in
- [ ] Session persists on refresh
- [ ] Login works with correct credentials
- [ ] Wrong credentials show error
- [ ] Protected routes require login
- [ ] Logout clears session
- [ ] Error messages are user-friendly
- [ ] No console errors
- [ ] No Flask errors
- [ ] Session cookie present and valid
- [ ] User data accessible in routes
- [ ] Firestore records created
- [ ] Firebase auth working

---

## 🚀 Production Readiness

Before deploying to production:

- [ ] All tests pass
- [ ] `FLASK_SECRET_KEY` set to random value
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] HTTPS enabled
- [ ] Error logging configured
- [ ] Monitoring set up
- [ ] Backup procedure documented
- [ ] Recovery procedure documented

---

## 📞 Troubleshooting Notes

### "Redirect loop"
- Clear cookies: DevTools → Application → Clear site data
- Check `public_endpoints` list in app.py
- Verify `@firebase_required` not duplicated

### "Session login failed"
- Check browser console for Firebase errors
- Verify `/session-login` endpoint accessible
- Check Flask logs for exceptions

### "Invalid token"
- Firebase token expired (logout and login again)
- Verify Firebase project configured
- Check Firebase rules

### "User not created in Firestore"
- Check Firestore rules allow creation
- Verify `/session-login` executing correctly
- Check Flask logs for create_user exceptions

---

## Done! 🎉

Once all tests pass, your authentication system is working perfectly. Ready for production deployment.
