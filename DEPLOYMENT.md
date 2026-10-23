# TrustVault Deployment Guide

## Overview

This document explains how to set up and run TrustVault from a clean clone of the repository.

TrustVault is a Flask-based secure document-sharing application with:

- Authentication
- Three user roles
- Document upload and management
- Per-document permissions
- Share and revoke functionality
- Server-side authorization
- Audit logging
- Administrative monitoring
- Automated security tests

---

# 1. Requirements

Install the following software:

- Python 3.11 or later
- Git
- pip
- A supported browser

For local development, SQLite can be used.

---

# 2. Clone the Repository

Clone the public repository:

```powershell
git clone https://github.com/KavyasriSadineni811/trustvault
```

Move into the project directory:

```powershell
cd trustvault
```

---

# 3. Create a Virtual Environment

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should show:

```text
(.venv)
```

---

# 4. Install Dependencies

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

If a dependency file is not available, install the dependencies listed by the project configuration.

---

# 5. Environment Configuration

Create a `.env` file in the project root.

Example:

```text
SECRET_KEY=replace-with-a-secure-random-secret
DATABASE_URL=sqlite:///trustvault.db
```

Do not commit the real `.env` file to a public repository.

A `.env.example` file can be committed instead.

Example:

```text
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///trustvault.db
```

---

# 6. Database Setup

Initialize or upgrade the database using Flask-Migrate:

```powershell
flask db upgrade
```

Check the current migration:

```powershell
flask db current
```

Check available migration heads:

```powershell
flask db heads
```

The database should be at the latest migration before starting the application.

---

# 7. Seed Test Accounts

TrustVault provides a seed script for creating the development/demo accounts.

Run:

```powershell
python seed.py
```

The seed process creates or resets the development accounts.

Example roles:

```text
Administrator
admin@trustvault.local

Document Owner
owner@trustvault.local

Viewer
recipient@trustvault.local
```

The passwords used for the challenge/demo environment should be documented in the private deployment/demo instructions or the README when intentionally provided for judging.

Do not use development passwords in a real production deployment.

---

# 8. Run the Application

Start the Flask development server:

```powershell
python run.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the URL in a browser.

Unauthenticated users should be redirected to the login page.

---

# 9. Test the Different Roles

## Administrator

Log in using the administrator account.

The administrator can access:

```text
/admin/
```

and administrative permission/activity functionality.

---

## Document Owner

Log in using:

```text
owner@trustvault.local
```

The owner can:

- Upload documents
- View owned documents
- Search/filter documents
- Share documents
- Grant read/edit permissions
- Revoke permissions
- Perform allowed document management operations

---

## Viewer

Log in using:

```text
recipient@trustvault.local
```

The viewer can access only documents for which an appropriate permission has been granted.

---

# 10. Security Verification

After deployment, verify that unauthorized users cannot access protected documents.

Test cases should include:

### Unauthorized document access

Attempt to access another user's document without permission.

Expected result:

```text
Access denied
```

### Unauthorized download

Attempt to download a document without permission.

Expected result:

```text
Access denied
```

### Unauthorized edit

Attempt to edit a document without edit permission.

Expected result:

```text
Access denied
```

### Unauthorized deletion

Attempt to delete a document without authorization.

Expected result:

```text
Access denied
```

### Permission revocation

Grant a viewer access to a document.

Verify that the viewer can access it.

Revoke the permission.

Attempt to access the document again.

Expected result:

```text
Access denied
```

---

# 11. Automated Tests

Run the project's automated tests using the configured test runner.

For example:

```powershell
pytest
```

The tests should include authorization/security cases such as:

- One user cannot access another user's document.
- Unauthorized download is rejected.
- Unauthorized edit is rejected.
- Unauthorized deletion is rejected.
- Unauthorized permission changes are rejected.
- Revoked users cannot continue accessing documents.

---

# 12. Production Deployment

For production, the Flask development server should not be used.

A production deployment should use:

- A production WSGI server
- HTTPS
- A production database such as PostgreSQL
- Secure environment variables
- Persistent document storage
- Secure secret management
- Appropriate logging and monitoring

The exact production platform may be selected according to the deployment provider.
### Live Deployment

TrustVault is deployed on Render and is available at:

https://trustvault-xmuw.onrender.com

### Demo Video

The five-minute demonstration video is available here:

https://drive.google.com/file/d/1yTENiFUL5Q6c6SYVkmA3gkjWR_ob3cl0/view?usp=sharing

---

# 13. Deployment Environment Variables

Production configuration should provide environment variables such as:

```text
SECRET_KEY=<secure-production-secret>
DATABASE_URL=<production-database-url>
```

Secrets must not be committed to GitHub.

---

# 14. Deployment Checklist

Before submitting the project:

- [x] Application runs successfully
- [x] Database migrations are applied
- [x] Seed accounts are available
- [x] Login works
- [x] Owner functionality works
- [x] Viewer functionality works
- [x] Administrator functionality works
- [x] Document upload works
- [x] Document sharing works
- [x] Permission revocation works
- [x] Unauthorized access is rejected
- [x] Audit activity is recorded
- [x] Automated security tests pass
- [x] Production environment variables are configured
- [x] HTTPS is enabled
- [x] Live URL is accessible

---

# 15. Clean Clone Verification

A fresh setup should follow this sequence:

```powershell
git clone https://github.com/KavyasriSadineni811/trustvault
cd trustvault

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

flask db upgrade

python seed.py

python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

The application should redirect an unauthenticated user to the login page.

---

# 16. Security Notes

TrustVault's primary security boundary is server-side authorization.

The application should not rely on:

- Hidden buttons
- Hidden URLs
- Frontend-only permission checks
- Document IDs being difficult to guess

Protected document operations must verify the current user's authorization before allowing the operation.

Permission revocation must be checked again when a protected resource is requested.

---

# 17. Deployment Limitations

The challenge implementation is primarily designed as a focused security demonstration rather than a complete enterprise document-management platform.

Known limitations should be documented honestly in the project README and final write-up.

Examples may include:

- Local filesystem storage
- SQLite in development
- Limited external sharing functionality
- No dedicated immutable external audit service
- No enterprise identity provider integration

---

# 18. Submission Information

The final submission should provide:

- Public GitHub repository
- Live deployed URL
- Seed/demo credentials
- README.md
- THREATS.md
- PROMPTS.md
- API.md
- SCHEMA.md
- DEPLOYMENT.md
- Automated tests
- Five-minute demonstration video
- Final write-up