# TrustVault AI Development Log

## Overview

TrustVault was developed with AI assistance during the seven-day hiring challenge.

AI was used for code generation, debugging, documentation, security review, testing ideas, and implementation guidance.

AI-generated suggestions were reviewed and tested against the actual TrustVault application. When generated code caused errors or did not match the existing application structure, the code was corrected rather than accepted blindly.

AI assistance was used as a development aid, but the final implementation decisions, integration, testing, debugging, and deployment were performed and verified by me.

---

# Entry 1 — 2026-10-19

## Task

I asked the AI to help me design and implement the initial TrustVault Flask application structure, including authentication, users, documents, and document permissions.

## Prompt / Request

> Help me build the TrustVault secure document-sharing application step by step. The application needs authentication, document owners, viewers, document uploads, and per-document permissions.

## What AI Produced

The AI suggested a Flask application structure containing:

- Authentication
- User model
- Document model
- Document permission model
- Flask blueprints
- Login/logout functionality
- Document upload functionality

## What Was Wrong

Some of the initial generated code did not exactly match the existing project structure and required adjustments to imports, routes, and model locations.

## What I Did

I tested the generated code locally and changed the structure so that it matched the actual TrustVault application.

I verified the application by running the Flask server and testing login, upload, and document functionality.

---

# Entry 2 — 2026-10-20

## Task

I asked the AI to implement document-level access control.

## Prompt / Request

> Implement secure document authorization so that a user cannot access another user's document simply by knowing the document ID or URL.

## What AI Produced

The AI recommended checking authorization on the server before protected document operations.

The proposed checks covered operations such as:

- Download
- Edit
- Delete
- Share
- Read

## What Was Wrong

The first approach relied too heavily on the visible interface in some places.

That is not sufficient for TrustVault because hiding a button does not prevent someone from directly calling the URL.

## What I Did

I tested the protected routes directly and ensured that authorization was checked on the server.

This was important because the challenge requires that unauthorized users cannot access documents through alternative routes.

---

# Entry 3 — 2026-10-21

## Task

I asked the AI to implement and verify the audit trail.

## Prompt / Request

> Implement audit logging for document operations and permission changes so TrustVault can prove who performed an action and when.

## What AI Produced

The AI proposed recording important actions such as:

```text
UPLOAD
READ
DOWNLOAD
EDIT
DELETE
SHARE
REVOKE
```

with information including the user, document, action, and timestamp.

## What Was Wrong

During development, the generated implementation and the actual database schema did not always remain synchronized.

This resulted in migration and schema problems when additional audit fields were considered.

For example, the application database did not contain the expected `previous_hash` and `record_hash` fields when the code attempted to access them.

## What I Did

I checked the actual database schema and migration state rather than assuming that a generated migration had already been applied.

After encountering migration and schema inconsistencies during development, I reverted the experimental tamper-evident migration changes and retained the stable audit implementation for the final deployed version.

This showed that AI-generated database changes must be checked against the actual migration state and database structure.

---

# Entry 4 — 2026-10-22

## Task

I asked the AI to implement an administrator dashboard and administrative activity view.

## Prompt / Request

> Create an administrator dashboard where an administrator can view system-wide document activity and permission information.

## What AI Produced

The AI generated administrator routes and templates for:

- Admin dashboard
- Activity view
- Permission view

## What Was Wrong

Several generated templates referred to endpoint names that did not exist in the actual Flask application.

Examples included:

```text
admin.dashboard
admin.permissions
admin.activity
documents.index
```

while the actual application contained different endpoint names.

This caused Flask `BuildError` exceptions.

## What I Did

I checked the application's actual URL map using:

```powershell
python -c "from app import create_app; app=create_app(); print('\n'.join(str(rule) for rule in app.url_map.iter_rules()))"
```

I then corrected the template endpoint references to match the real registered routes.

I also tested the administrator dashboard, permissions page, and logout functionality after making the corrections.

---

# Entry 5 — 2026-10-23

## Task

I asked the AI to improve the visual design of the administrator pages.

## Prompt / Request

> Make the administrator activity and permissions pages visually consistent with the TrustVault dashboard instead of displaying plain HTML tables.

## What AI Produced

The AI proposed replacing the plain HTML presentation with a dashboard-style interface containing:

- Navigation
- Cards
- Styled tables
- Colored action badges
- Consistent spacing
- Responsive layout
- TrustVault branding

## What Was Wrong

The first template replacement did not correctly preserve the existing data variables and route endpoints.

As a result, one version displayed an empty table even though audit records existed.

Another version contained an incorrect endpoint reference:

```text
documents.index
```

which caused:

```text
werkzeug.routing.exceptions.BuildError
```

## What I Did

I compared the template with the existing Flask route and context variables before replacing it.

I corrected the endpoint references and ensured that the existing audit records were passed to the template.

I then tested the page again using the actual TrustVault audit records.

---

# AI Mistakes I Identified

The development process showed several cases where AI-generated code could not be accepted without verification.

### 1. Incorrect Flask endpoint names

Generated templates sometimes referenced endpoints that were not registered.

### 2. Database migration mismatch

Generated database changes did not automatically mean that the actual database schema had changed.

### 3. UI-only security assumptions

Hiding a button is not authorization. The server must perform the permission check.

### 4. Existing application context was important

Generated code sometimes assumed a different project structure, variable name, or route structure than the existing application.

### 5. Generated code required testing

The application was repeatedly run and tested after AI-generated changes instead of assuming that generated code was correct.

---

# Reusable Development Context

The following information was repeatedly used when working with AI:

- TrustVault is a Flask application.
- The application uses Flask-Login for authentication.
- SQLAlchemy is used for database access.
- Flask-Migrate/Alembic is used for migrations.
- Documents have individual owners.
- Document permissions are granted to named users.
- Access must be checked server-side.
- Permission revocation must immediately affect subsequent access checks.
- Audit activity is recorded for important document and permission operations.
- The administrator has a separate administrative interface.
- The application supports administrator, owner, and viewer roles.

---

# How AI Was Used Responsibly

AI was used as a development assistant rather than as an authority.

The general workflow was:

```text
Requirement
    ↓
AI suggestion
    ↓
Implementation
    ↓
Run application
    ↓
Test actual behavior
    ↓
Inspect errors
    ↓
Correct implementation
    ↓
Retest
```

Security-sensitive suggestions were not accepted solely because the generated code looked correct.

The actual Flask routes, database state, authorization behavior, and application responses were checked during development.

Database and migration changes were also checked against the actual local database state before being used in the final implementation.

---

# Summary

AI significantly accelerated development of TrustVault, especially for:

- Flask implementation
- Debugging
- UI development
- Authentication
- Authorization guidance
- Audit logging
- Testing ideas
- Documentation

However, several AI-generated suggestions were incorrect or incompatible with the existing application.

The most important lesson was that AI-generated security, authorization, routing, and database changes must be tested against the actual application rather than trusted without verification.

The final TrustVault implementation was developed by combining AI-assisted suggestions with manual verification, debugging, testing, and deployment validation.