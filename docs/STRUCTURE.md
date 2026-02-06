# Project Structure

## Root Directory

Essential files and folders for the CredPoint application.

```
cred-point/
├── Core Application
│   ├── app.py                  Flask application initialization
│   ├── main.py                 Application entry point
│   ├── requirements.txt         Python dependencies
│   └── .env.example             Environment configuration template
│
├── Source Code
│   ├── routes.py               API endpoints and request handlers
│   ├── forms.py                Form definitions and validation
│   ├── utils.py                Utility functions
│   ├── pdf_generator.py         PDF report generation
│   ├── verification_engine.py   CPE grading and verification logic
│   └── recommendation_engine.py Recommendation system
│
├── Services & Configuration
│   └── services/
│       ├── firebase_config.py   Firebase initialization
│       ├── models.py            Database operations (Firestore)
│       └── middleware.py        Authentication and authorization
│
├── Frontend & Assets
│   ├── templates/               HTML templates (Jinja2)
│   │   ├── base.html           Master template
│   │   ├── dashboard.html      User dashboard
│   │   ├── activities.html     Activity management
│   │   ├── admin_pending_verifications.html
│   │   └── ... (other templates)
│   │
│   └── static/                 Static assets
│       ├── css/
│       │   └── style.css       Enterprise styling
│       └── js/
│           ├── main.js
│           └── auth_refresh.js
│
├── Automation & Workflows
│   └── n8n/                    n8n workflow templates
│       ├── N8N_SETUP_GUIDE.md
│       ├── workflow_auto_grade_activity.json
│       ├── workflow_daily_recommendations.json
│       └── workflow_admin_notifications.json
│
├── Documentation (Root Level)
│   ├── README.md               Project overview and setup
│   ├── CONTRIBUTING.md         Contribution guidelines
│   ├── SECURITY.md             Security policy
│   ├── SECURITY_HARDENING.md   Security implementation details
│   ├── QUICK_REFERENCE.md      Quick start and commands
│   ├── INDEX.md                Documentation index
│   └── LICENSE                 MIT License
│
└── Additional Documentation
    └── docs/
        ├── guides/             Detailed guides and checklists
        │   ├── ENTERPRISE_UPGRADE_SUMMARY.md
        │   └── ENTERPRISE_AUDIT_CHECKLIST.md
        │
        └── archive/            Previous versions
            ├── CONTRIBUTING_OLD.md
            ├── README_OLD.md
            └── SECURITY_OLD.md
```

---

## Key Directories

### Root Level Files
**Essential files needed for running the application:**
- `app.py` - Flask application with security configuration
- `main.py` - Entry point
- `requirements.txt` - All Python dependencies
- `.env.example` - Configuration template
- `LICENSE` - MIT License

### Source Code (`/` root)
**Business logic and feature implementation:**
- `routes.py` - All API endpoints (auth, activities, admin, etc.)
- `verification_engine.py` - CPE grading using OffSec rules
- `forms.py` - Input validation with WTForms
- `services/` - Database and authentication logic

### Frontend (`templates/` and `static/`)
**User interface and styling:**
- `templates/` - Jinja2 HTML templates
- `static/css/` - Professional enterprise styling
- `static/js/` - Client-side JavaScript

### Automation (`n8n/`)
**Workflow automation templates:**
- Auto-grading workflows
- Daily recommendation scheduler
- Admin notification alerts

### Documentation
**Professional project documentation:**

**Root level (essential):**
- `README.md` - Start here
- `CONTRIBUTING.md` - How to contribute
- `SECURITY.md` - Security policy
- `QUICK_REFERENCE.md` - Quick commands

**Detailed guides (`docs/guides/`):**
- `ENTERPRISE_UPGRADE_SUMMARY.md` - Feature overview
- `ENTERPRISE_AUDIT_CHECKLIST.md` - Deployment checklist

**Archive (`docs/archive/`):**
- Previous versions of documentation

---

## Development Workflow

```
1. Make changes to source code
   └─ routes.py, forms.py, verification_engine.py, etc.

2. Update templates if needed
   └─ templates/

3. Test locally
   └─ python main.py

4. Update documentation if applicable
   └─ README.md, CONTRIBUTING.md, etc.

5. Commit with clear message
   └─ git commit -m "feat: description"

6. Push and create pull request
   └─ See CONTRIBUTING.md for process
```

---

## File Organization Principles

### Keep Root Clean
- Only essential files at root level
- Detailed guides moved to `docs/guides/`
- Old versions moved to `docs/archive/`

### Logical Grouping
- Application code: root level
- Frontend assets: `templates/` and `static/`
- Services: `services/` folder
- Workflows: `n8n/` folder
- Documentation: root + `docs/`

### Professional Structure
- Clear separation of concerns
- Easy to navigate
- Obvious where to find things
- Scalable for growth

---

## Adding New Features

### New Endpoint
1. Add function to `routes.py`
2. Add form to `forms.py` (if needed)
3. Create template in `templates/`
4. Update `README.md` API section

### New Database Operation
1. Add method to `services/models.py`
2. Call from routes via service layer
3. Add validation in `forms.py`

### New Automation
1. Create workflow in `n8n/`
2. Document in `n8n/N8N_SETUP_GUIDE.md`
3. Add webhook endpoint in `routes.py`

### New Documentation
1. Add to existing `.md` files if related
2. Create new file in `docs/guides/` if significant
3. Update `INDEX.md` links

---

## File Size Management

### Keep Small
- Individual templates should be < 500 lines
- Individual Python files should be < 1000 lines
- Use imports and modular design

### Refactor When
- Single file grows > 1000 lines
- Too many responsibilities in one module
- Complex logic becomes hard to test

---

## Clean-up Guidelines

### Remove Files
- Old backups → `docs/archive/`
- Temporary files → delete
- Unused code → delete

### Organize Files
- Related code → same folder
- Old docs → `docs/archive/`
- New guides → `docs/guides/`
- Essential docs → root level

### Documentation
- Keep root docs minimal and current
- Move detailed guides to `docs/guides/`
- Archive old versions in `docs/archive/`

---

## Quick Reference

### Important Files
- **Run app**: `main.py`
- **Configure**: `.env.example` → `.env`
- **API routes**: `routes.py`
- **CPE grading**: `verification_engine.py`
- **Database**: `services/models.py`
- **Auth**: `services/middleware.py`

### First Steps
1. Read `README.md`
2. Setup: `cp .env.example .env`
3. Install: `pip install -r requirements.txt`
4. Run: `python main.py`
5. Contribute: See `CONTRIBUTING.md`

### Deployment
1. Review `SECURITY_HARDENING.md`
2. Check `docs/guides/ENTERPRISE_AUDIT_CHECKLIST.md`
3. Follow `README.md#deployment`

---

**This structure keeps the project organized, professional, and easy to navigate.**
