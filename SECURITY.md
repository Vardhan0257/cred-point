# Security Policy

CredPoint is designed with enterprise security principles. We take the security of compliance data seriously.

## Security Features

- **Authentication:** All access is secured via Firebase Authentication (OAuth2/OIDC).
- **Data Storage:** User files are stored in private Cloud Storage buckets. Public access is disabled.
- **Access Control:** Files are accessed only via time-limited Signed URLs generated on-demand.
- **Logging:** Critical actions and errors are logged for auditability.
- **Environment Security:** No secrets are hardcoded; all credentials are managed via Environment Variables.


## Reporting a Vulnerability
If you find a security vulnerability:
- Please **do not** open a public GitHub issue.
- Instead, use [GitHub's private security advisory](../../security/advisories/new) feature to report it.

## Supported Versions

We actively maintain the `main` branch. Please ensure you are using the latest release.

## Maintainers
This project is maintained by:
- [@Vardhan0257](https://github.com/Vardhan0257)
- [@Sravya0605](https://github.com/Sravya0605)
