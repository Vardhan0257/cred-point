# CredPoint Deployment Guide

## MVP Hosting - Zero Cost Options

### Current Status: ✅ Local Testing Complete

Your app is running successfully locally at:
- **Local**: `http://127.0.0.1:5000`
- **Network**: `http://192.168.1.8:5000`

---

## Phase 1: Local Development (COMPLETE ✅)

### Environment Setup
```bash
# Set environment variable (required every session)
$env:FLASK_ENV="development"

# Start app
python main.py

# Access at: http://127.0.0.1:5000
```

### Configuration
- **Config File**: `.env` (created automatically)
- **Features Working**: UI, Forms, Navigation, Styling
- **Firebase**: Using test credentials (data not persisted)

---

## Phase 2: Deploy to Cloud (Choose One)

### Option A: PythonAnywhere (RECOMMENDED - Easiest)

**Why PythonAnywhere?**
- ✅ No auto-sleep on free tier
- ✅ Firebase integration works great
- ✅ Easy environment variables
- ✅ Custom domain support
- ✅ Daily backup included

**Steps:**

```
1. Sign Up
   → pythonanywhere.com/register
   → Confirm email

2. Upload Code
   → Files tab
   → Create folder: cred-point
   → Upload ALL files and folders

3. Install Dependencies
   → Bash console
   → cd /home/USERNAME/cred-point
   → pip install -r requirements.txt

4. Create Web App
   → Web tab → Add new web app
   → Choose Python 3.10
   → Choose Flask
   → Source code: /home/USERNAME/cred-point

5. Configure .env
   → Files tab
   → Create .env in /home/USERNAME/cred-point
   → Copy values from .env.example
   → Update Firebase credentials

6. Reload & Test
   → Web tab → Reload button
   → Visit: USERNAME.pythonanywhere.com

7. Custom Domain (Optional, Paid)
   → Web tab → Add domain
   → Update DNS records
```

**Free Tier Limits:**
- 512 MB storage (enough for MVP)
- Limited CPU usage
- Runs 24/7 (no sleep)
- Perfect for MVP

**Cost**: Free ($5/month for pro features if needed)

---

### Option B: Render

**Why Render?**
- ✅ Automatic deployments from GitHub
- ✅ Free tier available
- ✅ Supports Flask perfectly
- ✅ Zero configuration

**Steps:**

```
1. Push to GitHub
   → Create GitHub account
   → Create new repository
   → Push your code:
     git init
     git add .
     git commit -m "Initial commit"
     git remote add origin https://github.com/USERNAME/cred-point.git
     git push -u origin main

2. Connect Render
   → render.com/register
   → New → Web Service
   → Connect GitHub repo
   → Choose cred-point

3. Configure
   → Build command: pip install -r requirements.txt
   → Start command: gunicorn app:app
   → Environment variables:
     FLASK_ENV=production
     FLASK_SECRET_KEY=your-secret-key-here
     (add Firebase credentials)

4. Deploy
   → Click Deploy
   → Render builds automatically
   → Get URL: cred-point-xyz.onrender.com

5. Test
   → Click the URL
   → Test features
```

**Free Tier Limits:**
- Auto-sleeps after 15 min inactivity
- OK for MVP/demo
- Wakes up when accessed

**Cost**: Free ($7/month to remove sleep)

---

### Option C: Replit (Fastest Testing)

**Why Replit?**
- ✅ Fastest to setup (5 min)
- ✅ Good for quick testing
- ✅ Built-in IDE

**Steps:**

```
1. Create Account
   → replit.com/register

2. Create Project
   → New Replit → Python
   → Drag & drop your files

3. Create .env
   → Secrets (lock icon) bottom left
   → Add variables from .env.example

4. Configure
   → Edit main.py:
     app.run(host='0.0.0.0', port=8080)

5. Run
   → Click Run
   → Get public URL
   → Test features
```

**Free Tier Limits:**
- Auto-sleeps after 30 min
- Good for demos
- Limited disk space

**Cost**: Free ($7/month for unlimited)

---

## Recommended Deployment Flow

```
WEEK 1: Local Testing
├── Run locally ✅
├── Test all features
└── Verify UI looks good

WEEK 2: Deploy MVP
├── Choose PythonAnywhere (recommended)
├── Upload code
├── Add Firebase credentials
└── Test on live URL

WEEK 3: Setup n8n
├── Create n8n.cloud account
├── Import workflows
├── Connect to your app
└── Test automation

WEEK 4: Production
├── Update configuration
├── Setup custom domain (optional)
├── Monitor performance
└── Add features
```

---

## Firebase Setup (Required for Data Persistence)

Without real Firebase credentials, data won't persist. Here's how to set it up:

### Get Firebase Credentials

```
1. Go to console.firebase.google.com
2. Create new project (free Spark plan)
3. Enable Firestore Database
4. Go to Settings → Service Accounts
5. Generate new private key
6. Download JSON file
7. Copy the entire JSON content
```

### Add to .env

```
GOOGLE_API_TOKEN={"type":"service_account","project_id":"YOUR_PROJECT","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk@YOUR_PROJECT.iam.gserviceaccount.com","...":"..."}
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
```

### Restart App

```
# Local:
$env:FLASK_ENV="development"; python main.py

# PythonAnywhere:
Web tab → Reload
```

---

## Environment Variables Checklist

```
[ ] FLASK_SECRET_KEY - Required for production
[ ] FLASK_ENV - Set to "development" for dev, "production" for prod
[ ] GOOGLE_API_TOKEN - Firebase service account key
[ ] FIREBASE_PROJECT_ID - Firebase project ID
[ ] SESSION_COOKIE_SECURE - True for HTTPS, False for local
[ ] SESSION_COOKIE_SAMESITE - Lax (default)
[ ] RATE_LIMIT_STORAGE - memory:// (local), redis (production)
```

---

## Testing Checklist

After deployment, verify these work:

```
[ ] Homepage loads
[ ] Sign Up page works
[ ] Can create account
[ ] Can login
[ ] Dashboard displays
[ ] Can add activity
[ ] CPE calculated correctly
[ ] Can download PDF
[ ] Admin panel accessible
[ ] Responsive on mobile
[ ] No console errors
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | App crashed. Check error logs. |
| Firebase errors | Verify credentials in .env file. |
| CSS/JS not loading | Check static files were uploaded. |
| 404 errors | Verify all folders uploaded (templates, static, services). |
| Slow page loads | Free tier is slower; upgrade if needed. |
| Login doesn't work | Firebase authentication not configured. |

---

## Next Steps After Deployment

1. **Setup n8n Automation** (see `n8n/N8N_SETUP_GUIDE.md`)
2. **Configure Email Notifications** (SendGrid, optional)
3. **Setup Slack Alerts** (optional)
4. **Monitor Performance** (add analytics, optional)
5. **Get SSL Certificate** (automatic on PythonAnywhere/Render)

---

## Cost Breakdown

| Service | Cost | Why |
|---------|------|-----|
| PythonAnywhere | Free | MVP hosting |
| Firebase | Free (Spark) | 50,000 read/day, sufficient for MVP |
| GitHub | Free | Code repository |
| n8n Cloud | Free | Automation (20 executions/month) |
| Domain | ~$10/year | Optional, custom domain |
| **Total** | **Free** | Everything for MVP works free |

---

## Security Checklist Before Production

- [ ] Update `FLASK_SECRET_KEY` (min 32 chars, random)
- [ ] Set `SESSION_COOKIE_SECURE=True` (only over HTTPS)
- [ ] Update `FLASK_ENV=production` (disables debug)
- [ ] Enable rate limiting
- [ ] Setup CSRF tokens (already done)
- [ ] Use HTTPS only (automatic on Render/PythonAnywhere)
- [ ] Rotate Firebase keys regularly
- [ ] Enable Firebase security rules
- [ ] Monitor logs for suspicious activity

---

## Scale to Production (Future)

When ready for production use:

1. **Use PythonAnywhere Professional** ($5/month)
   - Persistent log-in
   - Custom domains
   - 24/7 uptime SLA

2. **Setup Proper Database**
   - Firebase Blaze plan ($1-5/month)
   - Unlimited reads/writes
   - Automatic scaling

3. **Add Monitoring**
   - Sentry (error tracking)
   - Uptime Robot (monitoring)
   - Google Analytics (user tracking)

4. **Implement Backups**
   - Daily Firebase exports
   - Code backup (GitHub)
   - Database snapshots

---

## Commands Reference

### Local Development
```bash
# Start app
$env:FLASK_ENV="development"; python main.py

# Install dependencies
pip install -r requirements.txt

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Run tests (when added)
pytest
```

### Production (PythonAnywhere)
```bash
# SSH into server
ssh USERNAME@ssh.pythonanywhere.com

# Navigate to app
cd /home/USERNAME/cred-point

# Install/update dependencies
pip install -r requirements.txt

# View logs
tail -f /var/log/USERNAME_pythonanywhere_com_wsgi.log

# Reload app
# (Done via web interface)
```

---

**Ready to deploy? Start with PythonAnywhere - it's the easiest path to MVP! 🚀**
