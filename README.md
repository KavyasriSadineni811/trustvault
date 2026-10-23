# TrustVault — Secure Document Sharing with a Real Audit Trail

TrustVault is a secure document-sharing platform designed to ensure that documents can only be accessed by explicitly authorized users and that document activity can be traced through an audit trail.

The project focuses on two core security problems:

1. **Access control** — an unauthorized user must not be able to read, download, edit, delete, or otherwise access a document.
2. **Accountability** — the system records important document and permission activities so that administrators can determine who performed an action and when.

---

## 1. Project Overview

TrustVault provides secure document upload, organization, searching, sharing, revoking, downloading, editing, deletion, and auditing.

The application uses server-side authorization checks rather than relying only on hiding buttons or pages from users.

The main user roles are:

- **Administrator** — monitors system-wide document activity and permission information.
- **Document Owner** — manages documents they own and controls access to those documents.
- **Viewer** — can access documents that have explicitly been shared with them according to their permissions.

---

## 2. Problem Statement

Traditional document-sharing systems can create security problems when:

- users receive access to more documents than intended;
- permissions are not removed when access is revoked;
- direct URLs are used to bypass the user interface;
- unauthorized users attempt to download or modify files;
- there is no reliable record showing who accessed a document;
- administrators cannot investigate document activity afterwards.

TrustVault addresses these problems by enforcing authorization on the server for protected document operations and maintaining audit records for important activities.

---

## 3. Main Features

### Authentication

- Login system using user accounts.
- Password-protected accounts.
- Session-based authentication.
- Role-based access to application areas.
- Logout functionality.

### Document Management

Authenticated users can:

- upload documents;
- view their documents;
- search and filter documents;
- download authorized documents;
- edit authorized documents;
- delete authorized documents.

### Document Permissions

Document owners can:

- share a document with a named user;
- grant document access;
- revoke previously granted access.

Permissions are associated with individual documents rather than automatically exposing all documents owned by a user.

### Access Control

The server verifies authorization before protected document operations.

An unauthorized user should not be able to access a document simply by:

- changing a URL;
- directly requesting a download endpoint;
- attempting to edit a document;
- attempting to delete a document;
- using a document ID belonging to another user.

### Audit Trail

TrustVault records important document activities such as:

- `UPLOAD`
- `READ`
- `DOWNLOAD`
- `EDIT`
- `DELETE`
- `SHARE`
- `REVOKE`

Audit records contain information such as the user, document, action, and timestamp.

### Administrative Activity View

Administrators can inspect system-wide document activity and permission-related operations.

The administrative interface provides visibility into activity performed by document owners and viewers.

### Search and Filtering

Documents can be searched or filtered using information such as:

- document name;
- owner;
- category;
- upload date.

### File Validation

Uploaded files are validated before being accepted by the application.

Supported document/image extensions are restricted rather than allowing arbitrary file types.

---

## 4. User Roles

### Administrator

The administrator is responsible for system-level monitoring.

Administrator capabilities include:

- viewing system-wide activity;
- viewing document permission information;
- monitoring audit activity.

The administrator is not automatically treated as the owner of every document.

### Document Owner

A document owner can manage documents they own.

Typical owner capabilities include:

- upload;
- view;
- download;
- edit;
- delete;
- share;
- revoke access;
- view audit information for their documents.

### Viewer

A viewer can access documents explicitly shared with them.

A viewer cannot automatically access another user's private documents.

Access is determined by the server-side permission associated with the particular document.

---

## 5. Permission Model

TrustVault uses a **per-document permission model**.

Instead of giving a user access to an entire owner's document collection, access is granted to individual documents.

For example:

```text
Owner
  |
  +---- Document A
  |       |
  |       +---- Recipient 1: READ
  |
  +---- Document B
          |
          +---- Recipient 2: EDIT
```

This prevents access to one document from automatically granting access to all documents owned by the same person.

When access is revoked, subsequent protected requests are checked against the current permission state.

---

## 6. Security Model

The application follows the principle that:

> The server decides whether a user is allowed to perform an operation.

Hiding a button in the browser is not considered authorization.

For protected operations, the application checks the authenticated user and the document's ownership or permission relationship.

Examples include:

```text
GET document
        |
        v
Authenticated?
        |
        v
Owner OR explicitly permitted?
        |
     +--+--+
     |     |
    YES    NO
     |     |
 Allow    Deny
```

The same authorization principle is applied to protected operations such as download, edit, delete, share, and revoke.

---

## 7. Audit Trail

TrustVault maintains an audit record for important document operations.

An audit record contains information including:

```text
User
Document
Action
Timestamp
```

Example:

```text
owner@trustvault.local
trustvault_test_10.txt
SHARE
2026-10-22 11:05:55
```

Another example:

```text
recipient@trustvault.local
trustvault_test.txt
READ
2026-10-22 10:20:21
```

The audit history allows an administrator or authorized user to investigate document activity after an operation has occurred.

The project also treats audit integrity as a security concern and documents the current audit design and limitations in `THREATS.md`.

---

## 8. Application Routes

The current application exposes routes including:

```text
/
```

Application entry point.

```text
/auth/login
```

User login.

```text
/auth/logout
```

User logout.

```text
/documents/
```

Document dashboard.

```text
/documents/upload
```

Document upload.

```text
/documents/<int:document_id>/share
```

Share a document with another user.

```text
/documents/<int:document_id>/revoke/<int:user_id>
```

Revoke a user's permission.

```text
/documents/download/<int:document_id>
```

Download a document after authorization.

```text
/documents/edit/<int:document_id>
```

Edit a document after authorization.

```text
/documents/delete/<int:document_id>
```

Delete a document after authorization.

```text
/documents/<int:document_id>/audit
```

View document audit information.

```text
/documents/admin/activity
```

Administrative activity view.

```text
/admin/
```

Administrator dashboard.

```text
/admin/permissions
```

Administrator permission view.

Detailed endpoint authorization information will be maintained separately in `API.md`.

---

## 9. Project Structure

The project follows a Flask application structure similar to:

```text
trustvault/
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   │
│   ├── auth/
│   │   └── routes.py
│   │
│   ├── documents/
│   │   └── routes.py
│   │
│   ├── admin/
│   │   └── routes.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── permission.py
│   │   └── audit.py
│   │
│   └── templates/
│       ├── auth/
│       ├── documents/
│       └── admin/
│
├── instance/
│   └── uploads/
│
├── migrations/
│
├── tests/
│
├── seed.py
├── run.py
├── config.py
├── requirements.txt
├── .env
├── README.md
├── THREATS.md
├── PROMPTS.md
├── API.md
├── SCHEMA.md
└── DEPLOYMENT.md
```

The exact file structure may evolve as the project is deployed and documented.

---

## 10. Technology Stack

### Backend

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Migrate
- Alembic

### Database

- SQLite for the current development configuration.

### Frontend

- HTML
- CSS
- Jinja templates

### Security-related components

- Flask-Login authentication
- Server-side authorization
- CSRF protection
- File validation
- Per-document permissions
- Audit logging

---

## 11. Local Setup

### Step 1 — Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd trustvault
```

### Step 2 — Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 — Configure environment variables

Create a `.env` file.

Example:

```env
SECRET_KEY=replace-with-a-random-secret-key
DATABASE_URL=sqlite:///trustvault.db
```

Do not commit real production secrets to GitHub.

### Step 5 — Initialize/update the database

If the repository contains the required migrations:

```powershell
flask db upgrade
```

### Step 6 — Seed the development accounts

```powershell
python seed.py
```

The seed script creates or resets the development accounts used for testing.

### Step 7 — Start the application

```powershell
python run.py
```

The development application is available at:

```text
http://127.0.0.1:5000
```

---

## 12. Development Test Accounts

The development seed data currently provides:

### Administrator

```text
Email:
admin@trustvault.local
```

Password:

```text
admin123
```

### Document Owner

```text
Email:
owner@trustvault.local
```

Password:

```text
owner123
```

### Viewer

```text
Email:
recipient@trustvault.local
```

Password:

```text
recipient123
```

These are development credentials only.

For a deployed system, production credentials must be changed and secrets must not be exposed publicly except where intentionally required by the challenge instructions.

---

## 13. Testing

TrustVault includes automated security and functional tests.

The important security objective is to verify that one user cannot access another user's documents without permission.

Examples of security cases include:

- unauthorized document read;
- unauthorized download;
- unauthorized edit;
- unauthorized delete;
- access after permission revocation;
- authorized document access;
- owner access;
- viewer access;
- permission changes;
- audit activity.

The tests are intended to verify server-side authorization rather than merely checking whether UI controls are displayed.

Run the test suite using the project's configured test command, for example:

```powershell
pytest
```

---

## 14. Security Testing

The project was manually tested against the major document-sharing flows.

The security model is based on the assumption that a malicious user may attempt to bypass the UI and directly call application routes.

Important attack cases include:

```text
User A owns Document A.

User B attempts:

/documents/download/<Document A ID>

/documents/edit/<Document A ID>

/documents/delete/<Document A ID>

/documents/<Document A ID>/audit
```

The server must evaluate the user's authorization before allowing the operation.

The detailed threat analysis is documented in:

```text
THREATS.md
```

---

## 15. API Documentation

Endpoint authorization and expected request/response behavior are documented separately in:

```text
API.md
```

The API documentation identifies:

- endpoint;
- HTTP method;
- purpose;
- authentication requirement;
- allowed roles;
- authorization rule;
- expected result;
- possible failure conditions.

---

## 16. Database Schema

The main entities include:

```text
User
Document
DocumentPermission
AuditLog
```

Conceptually:

```text
User
 |
 +--------------------+
 |                    |
 v                    v
Document        DocumentPermission
 |
 |
 v
AuditLog
```

`SCHEMA.md` contains the detailed database structure, relationships, setup information, and migration instructions.

---

## 17. Threat Model

TrustVault treats the application as a security-sensitive document system rather than simply a CRUD application.

Potential threats include:

- unauthorized direct URL access;
- IDOR-style document access;
- unauthorized download;
- unauthorized edit;
- unauthorized deletion;
- stale permissions after revocation;
- invalid file uploads;
- session/authentication problems;
- CSRF attacks;
- audit manipulation;
- accidental privilege escalation;
- unauthorized administrative access.

The project's detailed threat analysis is maintained in:

```text
THREATS.md
```

The document also identifies limitations that were knowingly left unresolved rather than hiding them.

---

## 18. AI Usage

AI tools were used during development for:

- debugging;
- code generation;
- UI development;
- implementation guidance;
- test planning;
- documentation;
- security reasoning.

AI-generated code was not treated as automatically correct.

Particular attention was given to authentication, authorization, permission checks, audit logging, routing, and security-sensitive functionality.

The development prompts, AI output, identified problems, and corrections are documented in:

```text
PROMPTS.md
```

---

## 19. Deployment

The application is intended to be deployed as a Flask web application with a persistent database and persistent document storage.

Deployment instructions are maintained in:

```text
DEPLOYMENT.md
```

The deployment documentation covers:

- production environment setup;
- environment variables;
- database initialization;
- migration;
- seed data;
- application server;
- persistent storage;
- production configuration.

---

## 20. Live Application

Live URL:
https://trustvault-xmuw.onrender.com

The deployed application should contain seed data that allows the evaluator to test the administrator, owner, and viewer flows.

---

## 21. Demo Video

Five-minute demonstration:

https://drive.google.com/file/d/1yTENiFUL5Q6c6SYVkmA3gkjWR_ob3cl0/view?usp=sharing

The demonstration will cover:

1. Login.
2. Owner document upload.
3. Document search/filtering.
4. Sharing a document.
5. Viewer access.
6. Unauthorized access attempt.
7. Permission revocation.
8. Attempted access after revocation.
9. Audit history.
10. Administrator activity view.

---

## 22. Known Limitations

TrustVault is a challenge project and intentionally focuses on the security and functionality requirements specified by the challenge.

Features that are outside the current core scope may include:

- enterprise SSO;
- email-based invitations;
- advanced external sharing;
- document versioning;
- large-scale distributed storage;
- production-grade malware scanning;
- enterprise key management;
- high-availability deployment;
- automated retention policies.

These limitations should not be confused with the required authorization controls.

---

## 23. Design Decisions

### Per-document permissions

Permissions are granted to named users for individual documents rather than automatically exposing an entire document collection.

### Server-side authorization

Authorization decisions are made by the backend rather than trusting the frontend.

### Immediate revocation

Current permission state is checked when protected operations are requested so that removing a permission prevents subsequent access.

### Auditability

Important document and permission activities are recorded with user, document, action, and timestamp information.

### Administrator visibility

The administrator has a system-wide view intended for investigating document activity and permission changes.

---

## 24. What Was Deliberately Not Built

The project prioritizes the security requirements of the challenge over building every possible document-management feature.

The following areas were deliberately kept outside the core implementation unless explicitly required:

- enterprise identity providers;
- complex organization/group permissions;
- advanced document versioning;
- large-scale object storage;
- production-grade antivirus scanning;
- enterprise disaster recovery;
- multi-region deployment.

The purpose was to make the core document authorization model understandable and testable rather than expanding the feature set at the expense of security.

---

## 25. Project Status

### Core Application

- [x] Authentication
- [x] Administrator role
- [x] Document owner role
- [x] Viewer role
- [x] Document upload
- [x] Document management
- [x] Per-document permissions
- [x] Share document
- [x] Revoke access
- [x] Document access control
- [x] Audit activity
- [x] Search/filter functionality
- [x] File validation
- [x] Administrative activity view
- [x] Automated security tests

### Submission Deliverables

- [ ] README.md
- [ ] THREATS.md
- [ ] PROMPTS.md
- [ ] API.md
- [ ] SCHEMA.md
- [ ] DEPLOYMENT.md
- [ ] Public GitHub repository
- [ ] Live deployed URL
- [ ] Five-minute demo video
- [ ] Final write-up

---

## 26. Repository Deliverables

The final repository should contain at least:

```text
README.md
THREATS.md
PROMPTS.md
API.md
SCHEMA.md
DEPLOYMENT.md
```

along with the application source code, tests, migration files, setup scripts, and dependency configuration.

---

## 27. Final Submission

### GitHub Repository

https://github.com/KavyasriSadineni811/trustvault

### Live URL
https://trustvault-xmuw.onrender.com

### Demo Video

https://drive.google.com/file/d/1yTENiFUL5Q6c6SYVkmA3gkjWR_ob3cl0/view?usp=sharing

### Documentation

```text
README.md
THREATS.md
PROMPTS.md
API.md
SCHEMA.md
DEPLOYMENT.md
```

---

## 28. Summary

TrustVault is designed around the principle that **document access must be enforced by the server and must be explainable afterwards through an audit trail**.

The most important security properties are:

1. Unauthorized users cannot access documents simply by manipulating URLs or document IDs.
2. Permissions are evaluated for each protected document operation.
3. Document owners can grant and revoke access.
4. Important document and permission activity is recorded.
5. Administrative users can investigate system-wide activity.
6. Automated tests verify important authorization boundaries.

The project prioritizes a defensible document permission model and security-focused implementation over unnecessary features.
