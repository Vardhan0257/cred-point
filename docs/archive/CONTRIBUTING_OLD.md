# Contributing to CredPoint

We're excited you want to contribute to CredPoint! This document provides guidelines for contributing to our project.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We pledge that participation in our project will be a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing opinions, viewpoints, and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior include:

- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Project maintainers are responsible for enforcing this Code of Conduct. Those who violate it may face temporary or permanent removal from the project.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A Firebase project with Admin SDK credentials
- Understanding of Flask, Firestore, and security best practices

### Local Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/cred-point.git
   cd cred-point
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   - **macOS/Linux**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate`

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials and settings
   ```

7. **Run the development server**:
   ```bash
   python main.py
   ```

---

## Making Changes

### Branch Naming Convention

Use descriptive branch names following this pattern:
- `feature/short-description` - for new features
- `bugfix/short-description` - for bug fixes
- `docs/short-description` - for documentation
- `security/short-description` - for security improvements
- `refactor/short-description` - for code refactoring

Example: `feature/add-two-factor-auth` or `bugfix/fix-cpe-calculation`

### Commit Message Guidelines

Write clear, concise commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore, security
**Scope**: routes, models, services, templates, etc.
**Subject**: Imperative mood, no period, max 50 characters

Example:
```
feat(verification): implement auto-grading for OffSec CPE

- Add grade_activity() function with OffSec rules
- Support course, webinar, and lab activity types
- Integrate with admin approval workflow

Fixes #42
```

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** with clear, focused commits
3. **Add tests** for new functionality (see Testing section)
4. **Update documentation** if needed
5. **Push to your fork**
6. **Create a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what and why
   - Link to any related issues
   - Screenshots for UI changes
   - Security considerations if applicable

7. **Respond to reviews** - maintainers will review your PR and may request changes

### PR Checklist

Before submitting, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] New functions/methods have docstrings
- [ ] No hardcoded secrets, keys, or credentials
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary dependencies added
- [ ] Changes are backwards compatible where possible

---

## Code Standards

### Python

- Follow **PEP 8** style guidelines
- Use type hints for function signatures where practical
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all functions and classes

Tools:
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### HTML/Templates (Jinja2)

- Use semantic HTML5 elements
- Ensure responsive design (mobile-first approach)
- Include ARIA labels for accessibility
- Validate against HTML5 standards
- Use Bootstrap 5 utility classes consistently

### CSS

- Use CSS custom properties (variables)
- Mobile-first responsive design
- Follow a logical property order
- Avoid inline styles (use classes)
- Ensure WCAG AA contrast ratios

### JavaScript

- Use ES6+ features
- No `console.log()` in production code
- Use meaningful variable names
- Comment complex logic
- Validate user input on the client side

### Security

Every change must consider security:

- No hardcoded secrets or API keys
- Validate and sanitize all user inputs
- Use CSRF tokens for state-changing operations
- Implement rate limiting on sensitive endpoints
- Log security-relevant events
- Update dependencies regularly
- Never commit `.env` files with real credentials

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_verification_engine.py
```

### Writing Tests

- Write tests for all new features
- Include both positive and negative test cases
- Test edge cases and error handling
- Use descriptive test names: `test_grade_activity_with_invalid_duration()`
- Aim for 80%+ code coverage

Example test structure:
```python
def test_grade_activity_course_type():
    """Test CPE grading for course activity type."""
    activity = {
        'activity_type': 'course',
        'duration_hours': 10,
        'submission_source': 'online'
    }
    cpe, reason, auto_approved = grade_activity(activity)
    assert cpe == 10  # 1 CPE per hour, not exceeding 40
    assert auto_approved == True
```

---

## Documentation

### Code Comments

- Add comments for *why*, not *what*
- Keep comments up-to-date with code changes
- Use docstrings for modules, functions, and classes

Example:
```python
def grade_activity(activity: dict) -> tuple[int, str, bool]:
    """
    Grade an activity according to OffSec CPE guidelines.
    
    Args:
        activity: Dictionary containing activity_type, duration_hours, etc.
        
    Returns:
        Tuple of (awarded_cpe, reason, auto_approved)
    """
```

### Documentation Updates

- Update README.md if changing project scope
- Update API documentation for endpoint changes
- Add comments to complex algorithms
- Document configuration options in `.env.example`

---

## Security Reporting

**Do not open a public issue for security vulnerabilities.**

Please email: security@yourdomain.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We take security seriously and will respond within 48 hours.

For more details, see [SECURITY.md](SECURITY.md).

---

## Review Process

1. **Automated Checks**: GitHub Actions run tests and linting
2. **Code Review**: At least one maintainer reviews the PR
3. **Feedback**: Changes requested if needed
4. **Approval**: PR is approved and merged

### Reviewer Responsibilities

- Check for security issues
- Verify code quality and standards
- Ensure documentation is updated
- Validate testing
- Be respectful and constructive in feedback

---

## Project Structure

```
cred-point/
├── app.py                 # Flask app initialization
├── main.py               # Entry point
├── routes.py             # All endpoints
├── forms.py              # Form definitions
├── utils.py              # Utility functions
├── pdf_generator.py      # PDF generation
├── verification_engine.py # CPE grading logic
├── recommendation_engine.py
├── requirements.txt      # Python dependencies
├── services/
│   ├── firebase_config.py
│   ├── models.py        # Firestore CRUD
│   └── middleware.py    # Auth decorators
├── static/              # CSS, JS, images
├── templates/           # HTML templates
└── n8n/                 # n8n workflows
```

---

## Common Issues & Solutions

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Port 5000 already in use
```bash
# Find and kill the process, or use a different port:
python main.py --port 5001
```

### Firebase authentication fails
- Verify service account JSON is in correct location
- Check `.env` file has correct `FIREBASE_CREDENTIALS_PATH`
- Ensure Firebase Admin SDK is installed: `pip install firebase-admin`

### Tests failing
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run with verbose output
pytest -v
```

---

## Recognition

Contributors will be recognized in:
- GitHub Contributors page
- CONTRIBUTORS.md file (maintained in main branch)
- Release notes for significant contributions

---

## Questions?

- **General Questions**: Open a discussion on GitHub
- **Bug Reports**: Open an issue with details
- **Feature Requests**: Open an issue marked as "enhancement"
- **Security Issues**: Email security@yourdomain.com (see SECURITY.md)

---

## License

By contributing, you agree your contributions will be licensed under the MIT License.

---

Thank you for contributing to CredPoint! 🚀
