# Contributing to CredPoint

Thank you for considering contributing to CredPoint! We welcome contributions from the community to help improve this CPE tracking tool.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/YOUR_USERNAME/cred-point.git
    cd cred-point
    ```
3.  **Create a virtual environment** and install dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -r requirements.txt
    ```
4.  **Set up Environment Variables**:
    Create a `.env` file or set variables for `GOOGLE_API_TOKEN` (Firebase) and `FLASK_SECRET_KEY`.

## How to Submit Changes

1.  **Create a Branch**: Always work on a new branch for your feature or fix.
    ```bash
    git checkout -b feature/amazing-new-feature
    ```
2.  **Commit Changes**: Write clear, concise commit messages.
    ```bash
    git commit -m "Add: Automatic PDF generation for activity reports"
    ```
3.  **Push to GitHub**:
    ```bash
    git push origin feature/amazing-new-feature
    ```
4.  **Open a Pull Request**: Go to the original repository and open a PR describing your changes.

## Code Style

-   Follow PEP 8 guidelines for Python code.
-   Ensure HTML templates are responsive (Bootstrap 5).
-   Do not commit secrets (API keys, service accounts) to the repository.

## Reporting Issues

If you find a bug or security vulnerability, please refer to our Security Policy or open an issue on GitHub.