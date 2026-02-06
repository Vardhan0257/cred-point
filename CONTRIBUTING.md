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
- Showing empathy towards other community members

Examples of unacceptable behavior include:

- Trolling, insulting/derogatory comments, and personal or political attacks
- Harassment of any kind
- Publishing others' private information without explicit permission

### Enforcement

Project maintainers are responsible for enforcing this Code of Conduct.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A Firebase project with Admin SDK credentials

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
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials
   ```

6. **Run the development server**:
   ```bash
   python main.py
   ```

---

## Making Changes

### Branch Naming

- `feature/short-description` - for new features
- `bugfix/short-description` - for bug fixes
- `docs/short-description` - for documentation
- `security/short-description` - for security improvements
- `refactor/short-description` - for code refactoring

Example: `feature/add-two-factor-auth`

### Commit Messages

Write clear, concise commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore, security
**Subject**: Imperative mood, max 50 characters, no period

Example:
```
feat(verification): implement auto-grading for OffSec CPE

- Add grade_activity() function with OffSec rules
- Support course, webinar, and lab activity types
- Integrate with admin approval workflow

Fixes #42
```

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear, focused commits
3. Add tests for new functionality
4. Update documentation if needed
5. Push to your fork
6. Create a Pull Request with:
   - Clear title describing the change
   - Detailed description of what and why
   - Link to any related issues
   - Screenshots for UI changes

7. Respond to reviews - maintainers will provide feedback

### PR Checklist

Before submitting, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] New functions have docstrings
- [ ] No hardcoded secrets or credentials
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear

---

## Code Standards

### Python

- Follow **PEP 8** style guidelines
- Use type hints for function signatures
- Maximum line length: 100 characters
- Add docstrings to all functions and classes

### HTML/Templates

- Use semantic HTML5 elements
- Ensure responsive design (mobile-first)
- Include ARIA labels for accessibility
- Use Bootstrap 5 utility classes

### CSS

- Use CSS custom properties (variables)
- Mobile-first responsive design
- Avoid inline styles
- Ensure WCAG AA contrast ratios

### JavaScript

- Use ES6+ features
- No `console.log()` in production
- Use meaningful variable names
- Validate user input on client side

### Security

Every change must consider security:

- No hardcoded secrets or API keys
- Validate and sanitize all user inputs
- Use CSRF tokens for state-changing operations
- Implement rate limiting on sensitive endpoints
- Never commit `.env` files with real credentials

---

## Testing

### Running Tests

```bash
pytest                   # Run all tests
pytest --cov            # With coverage
pytest -v               # Verbose
```

### Writing Tests

- Write tests for all new features
- Include both positive and negative test cases
- Test edge cases and error handling
- Aim for 80%+ code coverage

---

## Documentation

### Code Comments

- Add comments for *why*, not *what*
- Keep comments up-to-date with code changes
- Use docstrings for modules, functions, and classes

### Documentation Updates

- Update README.md if changing project scope
- Update API documentation for endpoint changes
- Document configuration options in `.env.example`

---

## Security Reporting

**Do not open a public issue for security vulnerabilities.**

Please email: `security@yourdomain.com`

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We take security seriously and will respond within 48 hours.

For more details, see [SECURITY.md](SECURITY.md).

---

## Project Structure

```
cred-point/
├── app.py                    # Flask initialization
├── main.py                   # Entry point
├── routes.py                 # All endpoints
├── forms.py                  # Form validation
├── verification_engine.py    # CPE grading logic
├── services/
│   ├── firebase_config.py
│   ├── models.py             # Firestore CRUD
│   └── middleware.py         # Auth decorators
├── static/                   # CSS, JS, images
├── templates/                # HTML templates
└── n8n/                      # n8n workflows
```

---

## Common Issues & Solutions

### Module not found errors
```bash
pip install -r requirements.txt
```

### Firebase authentication fails
- Verify service account JSON is in correct location
- Check `.env` file has correct `FIREBASE_CREDENTIALS_PATH`
- Ensure Firebase Admin SDK is installed

### Tests failing
```bash
pip install pytest pytest-cov
pytest -v
```

---

## Questions?

- **General Questions**: Open a GitHub discussion
- **Bug Reports**: Open an issue with details
- **Feature Requests**: Open an issue marked as "enhancement"
- **Security Issues**: Email security@yourdomain.com

---

## License

By contributing, you agree your contributions will be licensed under the MIT License.

---

Thank you for contributing to CredPoint!
