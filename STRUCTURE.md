# CredPoint - Project Structure

Professional CPE (Continuing Professional Education) management platform with n8n automation.

## 📁 Project Structure

```
cred-point/
│
├── 📄 main.py                      # Application entry point
├── 📄 app.py                       # Flask app initialization
├── 📄 routes.py                    # Main application routes
├── 📄 forms.py                     # WTForms form definitions
│
├── 📁 config/                      # Configuration files
│   ├── firestore.indexes.json     # Firestore database indexes
│   └── serviceAccountKey.json     # Firebase credentials (git-ignored)
│
├── 📁 core/                        # Core application modules
│   ├── __init__.py
│   ├── utils.py                   # Utility functions
│   ├── auth_utils.py              # Authentication utilities
│   ├── pdf_generator.py           # PDF report generation
│   ├── recommendation_engine.py   # CPE recommendations engine
│   └── verification_engine.py     # Activity verification logic
│
├── 📁 services/                    # External services integration
│   ├── __init__.py
│   ├── firebase_config.py         # Firebase configuration
│   ├── middleware.py              # Flask middleware (auth, etc.)
│   └── models.py                  # Firestore data models
│
├── 📁 static/                      # Static assets
│   ├── css/                       # Stylesheets
│   │   └── style.css
│   └── js/                        # JavaScript files
│       ├── main.js
│       └── auth_refresh.js
│
├── 📁 templates/                   # Jinja2 HTML templates
│   ├── base.html                  # Base template
│   ├── dashboard.html             # User dashboard
│   ├── activities.html            # Activity management
│   ├── certifications.html        # Certification management
│   ├── recommendations.html       # CPE recommendations (n8n)
│   ├── events.html                # Cybersecurity events (n8n)
│   └── ...                        # Other templates
│
├── 📁 docs/                        # Documentation
│   ├── README.md                  # Documentation index
│   ├── auth/                      # Authentication docs
│   ├── deployment/                # Deployment guides
│   ├── security/                  # Security docs
│   ├── guides/                    # Development guides
│   └── archive/                   # Legacy documentation
│
├── 📁 n8n/                         # n8n workflow automation
│   ├── README.md                  # n8n setup guide
│   ├── N8N_SETUP_GUIDE.md        # Detailed setup instructions
│   └── workflow_*.json            # n8n workflow definitions
│
├── 📁 scripts/                     # Utility scripts
│   ├── debug_routes.py            # Route debugging
│   ├── fix_*.py                   # Migration/fix scripts
│   └── replace_function.py        # Code refactoring tools
│
├── 📁 screenShots/                 # Application screenshots
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 pyproject.toml              # Project configuration
├── 📄 uv.lock                     # uv package manager lock file
├── 📄 .env.example                # Environment variables template
├── 📄 .gitignore                  # Git ignore rules
├── 📄 LICENSE                     # MIT License
└── 📄 README.md                   # Main project README
```

## 🗂️ Directory Details

### `config/`
Contains configuration files and credentials:
- **firestore.indexes.json**: Database index definitions for Firestore queries
- **serviceAccountKey.json**: Firebase service account credentials (never commit!)

### `core/`
Core business logic modules:
- **utils.py**: Shared utilities (CSV/PDF generation, normalization, file URLs)
- **auth_utils.py**: Authentication helpers and token management
- **pdf_generator.py**: CPE report PDF generation
- **recommendation_engine.py**: Generate CPE activity recommendations
- **verification_engine.py**: Verify activity CPE claims

### `services/`
External service integrations:
- **firebase_config.py**: Firebase Admin SDK initialization
- **middleware.py**: Flask request middleware (auth decorators, etc.)
- **models.py**: Firestore CRUD operations (activities, certificates, users)

### `static/`
Client-side assets:
- **css/style.css**: Custom styles (dark theme, card layouts)
- **js/main.js**: Core JavaScript functionality
- **js/auth_refresh.js**: Token refresh logic

### `templates/`
Server-rendered HTML templates using Jinja2:
- Authentication pages (login, register)
- Dashboard and profile
- Activity and certification management
- Recommendations and events (n8n-powered)

### `docs/`
Comprehensive documentation organized by topic:
- **auth/**: Authentication system documentation
- **deployment/**: Production deployment and testing guides
- **security/**: Security policies and hardening
- **guides/**: Development and contribution guides

### `n8n/`
Automation workflow definitions:
- Webhook endpoints for receiving RSS feed data
- Workflow JSON files for importing into n8n
- Setup and configuration guides

### `scripts/`
Development and maintenance scripts:
- Debugging utilities
- Database migration scripts
- Code refactoring tools

## 🚀 Quick Start

```bash
# Set up environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Firebase credentials

# Run development server
python main.py
```

## 📦 Key Dependencies

- **Flask**: Web framework
- **Firebase Admin SDK**: Backend authentication & Firestore
- **WTForms**: Form validation
- **ReportLab**: PDF generation
- **python-dotenv**: Environment variable management

## 🔐 Security Notes

- `config/serviceAccountKey.json` is git-ignored
- Use environment variables for production credentials
- Set `FLASK_SECRET_KEY` in production
- Set `FIREBASE_STORAGE_BUCKET` for file uploads

## 📚 Documentation

See [docs/README.md](docs/README.md) for complete documentation index.

## 🔗 Related

- [n8n Setup Guide](n8n/N8N_SETUP_GUIDE.md)
- [Deployment Guide](docs/deployment/DEPLOYMENT.md)
- [Security Hardening](docs/security/SECURITY_HARDENING.md)
- [Contributing Guidelines](docs/guides/CONTRIBUTING.md)
