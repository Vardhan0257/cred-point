# CredPoint - Enterprise CPE Management Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.1.1](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![Security Hardened](https://img.shields.io/badge/Security-Hardened-brightgreen.svg)](SECURITY_HARDENING.md)

## Overview

CredPoint is a **professional-grade Continuing Professional Education (CPE) management platform** designed for security professionals, developers, and enterprise organizations. It automates CPE tracking, grading, and verification using industry-standard rules (OffSec CPE guidelines).

### Key Features

- 🎓 **Automated CPE Grading** - Intelligent grading engine based on OffSec certification rules
- 📋 **Activity Management** - Track courses, certifications, webinars, labs, and speaking engagements
- 🔐 **Enterprise Security** - Rate limiting, CSRF protection, secure authentication, encrypted sessions
- 🤖 **n8n Automation** - Workflow automation for grading, recommendations, and notifications
- 📊 **Professional Dashboard** - Real-time progress tracking and CPE analytics
- 👥 **Admin Portal** - Review and approve pending CPE submissions
- 📧 **Smart Recommendations** - Daily personalized CPE recommendations via email
- 🔔 **Notifications** - Slack and email alerts for admins on pending submissions
- 📄 **PDF Reports** - Generate and download CPE transcripts

---

## Architecture

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.8+, Flask 3.1.1, Werkzeug 3.1.3 |
| **Database** | Google Firestore (NoSQL) |
| **Authentication** | Firebase Admin SDK 6.6.0 |
| **Frontend** | Bootstrap 5, Jinja2, HTML5 |
| **Automation** | n8n (workflow orchestration) |
| **Security** | Flask-WTF (CSRF), Flask-Limiter, python-magic |
| **Reporting** | ReportLab 4.4.3 (PDF generation) |
| **Deployment** | WSGI-compatible (Gunicorn, uWSGI) |

### System Architecture

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ▼
┌────────────────┐
│ Flask App      │ ◄─── Rate Limiting, CSRF, Session Security
│ (routes.py)    │
└──────┬─────────┘
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Verification │  │   Models     │  │   Services   │
│  Engine      │  │  (Firestore) │  │ (Firebase)   │
└──────────────┘  └──────────────┘  └──────────────┘
       │
       ▼
┌──────────────────────────────────┐
│      Google Firestore            │
│  (users, activities, certs, etc) │
└──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  n8n Workflows                   │
│  - Auto-grading                  │
│  - Daily recommendations         │
│  - Admin notifications           │
└──────────────────────────────────┘
```

---

## CPE Grading Rules

CredPoint implements **OffSec CPE certification rules**:

| Activity Type | CPE Award | Cap | Auto-Approve |
|---|---|---|---|
| **Course** | 1 CPE per hour | 40 CPE | ✅ Yes |
| **Webinar** | 1 CPE per hour | 30 CPE | ✅ Yes |
| **Public Speaking** | 4 CPE per event | — | ✅ Yes |
| **Paper/Article** | 4 CPE per publication | — | ✅ Yes |
| **Lab Submission** | 20 CPE per lab | — | ❌ Admin review |
| **Other** | User-provided | — | ❌ Admin review |

*Rules can be customized in [verification_engine.py](verification_engine.py)*

---

## Quick Start

### Prerequisites

- Python 3.8+
- Firebase project with Admin SDK
- n8n instance (optional, for automation)
- GitHub account (for code contributions)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/cred-point.git
   cd cred-point
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials and settings
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

   Visit: `http://localhost:5000`

### Development

For local development with auto-reload:
```bash
FLASK_ENV=development FLASK_DEBUG=true python main.py
```

---

## Usage Guide

### For Users

1. **Register** - Sign up with email and password
2. **Add Certification** - Input your certification details
3. **Log Activities** - Track courses, webinars, and other CPE activities
4. **Track Progress** - View CPE points in dashboard
5. **Download Report** - Export CPE transcript as PDF

### For Admins

1. **Review Pending** - Navigate to `/admin/pending-cpe`
2. **Grade Activities** - Review submissions with auto-calculated CPE
3. **Approve/Reject** - Accept valid submissions or request revision
4. **Monitor Users** - View user progress and participation

### For Automation (n8n)

See [n8n/N8N_SETUP_GUIDE.md](n8n/N8N_SETUP_GUIDE.md) for:
- Auto-grading workflow setup
- Daily recommendations scheduler
- Admin notification alerts

---

## Security

CredPoint implements **enterprise-grade security**:

### Implemented Protections

✅ **CSRF Protection** - Flask-WTF CSRF tokens on all forms
✅ **Rate Limiting** - Per-endpoint rate limits (5 login attempts/15min, 3 register/1hr)
✅ **Secure Sessions** - HTTPONLY, SECURE, SAMESITE cookies with 1-hour lifetime
✅ **Input Validation** - Strict file upload validation (size, extension, MIME type)
✅ **Secret Management** - Environment-only secrets, no hardcoding
✅ **Secure Headers** - Content-Security-Policy, X-Frame-Options, X-Content-Type-Options
✅ **Password Hashing** - Firebase automatic password hashing (bcrypt)
✅ **Dependency Auditing** - Regular security updates in requirements.txt

### Vulnerability Reporting

**DO NOT open public issues for security vulnerabilities.**

Email: `security@yourdomain.com`

See [SECURITY.md](SECURITY.md) for details.

For implementation details, see [SECURITY_HARDENING.md](SECURITY_HARDENING.md).

---

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Dashboard & Profile
- `GET /` - Home page
- `GET /dashboard` - User dashboard
- `GET /profile` - User profile
- `POST /profile` - Update profile

### Activities
- `GET /activities` - List activities
- `POST /add-activity` - Create activity
- `GET /activity/<id>/edit` - Edit activity
- `POST /activity/<id>/edit` - Update activity
- `POST /activity/<id>/delete` - Delete activity

### Certifications
- `GET /certifications` - List certifications
- `POST /add-certification` - Create certification
- `POST /edit-certification/<id>` - Update certification

### Recommendations
- `GET /recommendations` - Browse recommendations
- `GET /my-recommendations` - User's recommendations
- `POST /recommendations/generate` - API endpoint for n8n (generate recommendations)

### Admin
- `GET /admin/pending-cpe` - View pending CPE (requires admin role)
- `POST /admin/approve/<user_id>/<activity_id>` - Approve CPE
- `POST /admin/reject/<user_id>/<activity_id>` - Reject CPE

---

## Project Structure

```
cred-point/
├── app.py                    # Flask app initialization & config
├── main.py                   # Entry point
├── routes.py                 # All endpoints (auth, activities, admin, etc)
├── forms.py                  # WTForms validation
├── utils.py                  # Utility functions
├── pdf_generator.py          # PDF generation for transcripts
├── verification_engine.py    # CPE grading logic (OffSec rules)
├── recommendation_engine.py  # Recommendation algorithm
│
├── services/
│   ├── firebase_config.py    # Firebase initialization
│   ├── models.py             # Firestore CRUD operations
│   └── middleware.py         # Authentication decorators
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth_refresh.js
│       └── main.js
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── activities.html
│   ├── admin_pending_verifications.html
│   └── ... (other pages)
│
├── n8n/                      # n8n workflow automation
│   ├── workflow_auto_grade_activity.json
│   ├── workflow_daily_recommendations.json
│   ├── workflow_admin_notifications.json
│   ├── N8N_SETUP_GUIDE.md
│   └── README.md
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── LICENSE                   # MIT License
├── README.md                 # This file
├── CONTRIBUTING.md           # Contribution guidelines
├── SECURITY.md               # Security policy
└── SECURITY_HARDENING.md     # Hardening checklist & testing
```

---

## Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# Flask
FLASK_APP=main.py
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-secret-key-here

# Firebase
FIREBASE_CREDENTIALS_PATH=/path/to/service-account-key.json
FIRESTORE_DATABASE_ID=default

# Session
PERMANENT_SESSION_LIFETIME=3600
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Rate Limiting
RATELIMIT_ENABLED=True

# n8n (optional)
N8N_API_URL=https://your-n8n.com/api/v1
N8N_API_KEY=your-api-key

# Email (optional)
SENDGRID_API_KEY=your-sendgrid-key
ADMIN_EMAIL=admin@yourdomain.com

# Slack (optional)
SLACK_WEBHOOK_URL=your-webhook-url
```

---

## Database Schema

### Users Collection
```javascript
{
  uid: "firebase-uid",
  email: "user@example.com",
  name: "John Doe",
  is_admin: false,
  created_at: timestamp,
  updated_at: timestamp
}
```

### Activities Collection
```javascript
{
  activity_id: "uuid",
  uid: "user-id",
  activity_type: "course", // course, webinar, lab, speaking, paper
  title: "OSCP Prep Course",
  duration_hours: 40,
  submission_source: "online", // online, in-person, virtual
  subcategory: "offensive-security",
  awarded_cpe: 40,
  awarded_reason: "1 CPE per hour capped at 40",
  status: "approved", // pending, approved, rejected
  created_at: timestamp,
  offsec_submission_id: "ref" // for lab tracking
}
```

---

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Setup for Production

1. Set `FLASK_ENV=production`
2. Use strong `FLASK_SECRET_KEY` (generate with `openssl rand -hex 32`)
3. Enable CSRF, rate limiting, and secure headers
4. Use HTTPS only (configure reverse proxy)
5. Set up proper logging and monitoring
6. Configure Firebase security rules
7. Set up automated backups for Firestore

---

## Performance

### Optimization Tips

- **Caching**: Implement Redis caching for frequently accessed data
- **Database Indexes**: Firestore indexes on commonly filtered fields
- **CDN**: Use CDN for static assets (CSS, JS, images)
- **Async Tasks**: Use Celery + Redis for long-running tasks (PDF generation, email)
- **Monitoring**: Set up Sentry for error tracking

---

## Testing

### Running Tests

```bash
pytest                    # Run all tests
pytest --cov            # With coverage report
pytest -v               # Verbose output
```

### Test Files

```
tests/
├── test_verification_engine.py
├── test_routes.py
├── test_models.py
└── test_forms.py
```

### Writing Tests

See [CONTRIBUTING.md#testing](CONTRIBUTING.md#testing) for guidelines.

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of Conduct
- Development setup
- Code standards
- Pull request process
- Testing requirements
- Security reporting

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "feat: add amazing feature"`
4. Push to fork: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## Roadmap

### Planned Features

- [ ] Two-factor authentication (2FA)
- [ ] Role-based access control (RBAC) enhancement
- [ ] Audit logging for compliance
- [ ] Advanced CPE analytics and forecasting
- [ ] Mobile app (React Native)
- [ ] SSO integration (SAML, OAuth2)
- [ ] Bulk activity import (CSV)
- [ ] Integration with certification bodies (ISC2, CompTIA)
- [ ] Dark/Light mode toggle
- [ ] Multi-language support

---

## Support

### Getting Help

- **Documentation**: See [README.md](README.md) and individual guides
- **Issues**: [GitHub Issues](https://github.com/yourusername/cred-point/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cred-point/discussions)
- **Security**: [SECURITY.md](SECURITY.md)

### Community

- Follow us on GitHub
- Star the repository if you find it useful
- Share feedback and feature requests

---

## License

Licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

```
Copyright (c) 2026 Maddilavan Indraneeli Vardhan and Jaladi Sravya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...
```

---

## Acknowledgments

- **OffSec** - For CPE grading guidelines
- **Flask** - Web framework
- **Firebase** - Backend infrastructure
- **Bootstrap** - UI framework
- **n8n** - Workflow automation
- **Contributors** - All who help improve CredPoint

---

## Authors

- **Maddilavan Indraneeli Vardhan** - Primary Developer
- **Jaladi Sravya** - Co-Developer

---

## Changelog

### Version 1.0.0 (Current)
- ✅ Core CPE management system
- ✅ OffSec grading rules
- ✅ Admin approval workflow
- ✅ n8n automation
- ✅ Enterprise security hardening
- ✅ Professional UI/UX

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

<div align="center">

**CredPoint** - Enterprise CPE Management Made Simple

[🌐 Website](#) • [📖 Docs](#) • [🐛 Report Bug](https://github.com/yourusername/cred-point/issues) • [✨ Request Feature](https://github.com/yourusername/cred-point/issues)

</div>
