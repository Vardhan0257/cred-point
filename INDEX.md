# CredPoint Documentation

**Enterprise CPE Management Platform**  
Professional Continuing Professional Education tracking and automation system.

---

## Core Documentation

### Getting Started
- **[README.md](README.md)** - Project overview, features, quick start, API endpoints
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference and common tasks

### Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines and code standards
- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting

### Operations
- **[SECURITY_HARDENING.md](SECURITY_HARDENING.md)** - Security implementation and deployment checklist

---

## Additional Resources

For detailed guides and checklists:
- **docs/guides/** - Comprehensive guides and references
- **docs/archive/** - Previous versions and archived documentation

See [docs/guides/ENTERPRISE_AUDIT_CHECKLIST.md](docs/guides/ENTERPRISE_AUDIT_CHECKLIST.md) for deployment verification checklist.

---

## Project Structure

```
cred-point/
├── app.py                    # Flask application
├── main.py                   # Entry point
├── routes.py                 # API endpoints
├── verification_engine.py    # CPE grading logic
├── services/
│   ├── models.py
│   ├── middleware.py
│   └── firebase_config.py
├── templates/                # HTML templates
├── static/                   # CSS, JavaScript
├── n8n/                      # Workflow automation
├── docs/
│   ├── guides/              # Detailed guides
│   └── archive/             # Previous versions
├── README.md                # Main documentation
├── CONTRIBUTING.md          # Contribution guide
├── SECURITY.md              # Security policy
├── LICENSE                  # MIT License
└── requirements.txt         # Python dependencies
```

---

## Quick Links

### Essential Files
- 📖 [README.md](README.md) - Start here
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- 🔒 [SECURITY.md](SECURITY.md) - Security information
- 🚀 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick commands

### Support
- 🐙 [GitHub Repository](https://github.com/yourusername/cred-point)
- 📋 [Report Issues](https://github.com/yourusername/cred-point/issues)
- 💬 [Discussions](https://github.com/yourusername/cred-point/discussions)
- 🔐 [Security](SECURITY.md) - Vulnerability reporting

---

## Setup & Deployment

### Quick Start (5 minutes)
```bash
git clone https://github.com/yourusername/cred-point.git
cd cred-point
python -m venv venv
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Visit: http://localhost:5000

### Production Deployment
See [SECURITY_HARDENING.md](SECURITY_HARDENING.md) for pre-deployment checklist and [README.md#deployment](README.md#deployment) for deployment instructions.

---

## Technology Stack

- **Backend**: Python 3.8+, Flask 3.1.1
- **Database**: Google Firestore
- **Authentication**: Firebase Admin SDK
- **Frontend**: Bootstrap 5, Jinja2
- **Automation**: n8n

---

## Key Features

- CPE activity tracking (courses, webinars, labs, speaking)
- Automated grading using OffSec rules
- Admin approval workflow
- Daily recommendations via email
- Admin notifications via Slack
- PDF transcript generation
- Professional web interface

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code standards (PEP 8, documentation)
- Pull request process
- Code of Conduct

---

## Security

CredPoint implements enterprise security standards:
- CSRF protection
- Rate limiting
- Secure sessions
- Input validation
- Secure headers
- File upload validation

For security concerns, see [SECURITY.md](SECURITY.md).

---

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

**Copyright © 2026** Maddilavan Indraneeli Vardhan and Jaladi Sravya

---

**Last Updated**: February 2026  
**Status**: Production Ready

For more information, start with [README.md](README.md).
