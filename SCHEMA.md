# TrustVault Database Schema

## Overview

TrustVault uses a relational database to store users, documents, document permissions and audit activity.

The database is accessed through SQLAlchemy and managed using Flask-Migrate/Alembic migrations.

---

## 1. Users

The `users` table stores authenticated TrustVault users.

### Main fields

| Field | Purpose |
|---|---|
| `id` | Unique user identifier |
| `name` | User's display name |
| `email` | User's login email |
| `password_hash` | Hashed user password |
| `role` | User role |

### Roles

TrustVault supports three main roles:

- `admin` — administrator
- `owner` — document owner
- `viewer` — document viewer/recipient

Passwords are not stored as plaintext passwords. The application stores password hashes.

---

## 2. Documents

The `documents` table stores uploaded documents.

### Main fields

| Field | Purpose |
|---|---|
| `id` | Unique document identifier |
| `owner_id` | ID of the document owner |
| `original_filename` | Original uploaded filename |
| `stored_filename` | Application-controlled stored filename |
| `storage_path` | Location of the stored document |
| `created_at` | Document creation/upload timestamp |

### Relationships

Each document belongs to a user through `owner_id`.

A user can own multiple documents.

Conceptually:

```text
User
 |
 +---- owns ----> Document
```

---

## 3. Document Permissions

The `document_permissions` table stores document-level access grants.

Permissions are associated with a specific document and a specific user.

### Main fields

| Field | Purpose |
|---|---|
| `id` | Unique permission identifier |
| `document_id` | Document receiving the permission |
| `user_id` | User receiving the permission |
| `permission` | Permission level |

### Permission levels

TrustVault supports document permissions such as:

- `read`
- `edit`

### Relationships

```text
User
 |
 +---- receives ----> DocumentPermission
                         |
                         +---- applies to ----> Document
```

This prevents permissions from being automatically inherited across every document belonging to an owner.

---

## 4. Audit Logs

The `audit_logs` table records security-relevant document activity.

### Main fields

| Field | Purpose |
|---|---|
| `id` | Unique audit record identifier |
| `document_id` | Related document |
| `user_id` | User who performed the action |
| `action` | Action performed |
| `timestamp` | Time of the action |

### Example actions

```text
UPLOAD
READ
DOWNLOAD
EDIT
DELETE
SHARE
REVOKE
```

### Example

```text
User:
recipient@trustvault.local

Document:
trustvault_test.txt

Action:
READ

Timestamp:
2026-10-22 10:20:21
```

This allows the system to answer questions such as:

> Who accessed this document and when?

---

# Entity Relationships

The main relationships are:

```text
                 +----------------+
                 |      User      |
                 +----------------+
                    |     |     |
                    |     |     |
                 owns  receives  performs
                    |     |     |
                    v     v     v
              +---------+  +----------------+
              | Document|  |   AuditLog     |
              +---------+  +----------------+
                   |
                   |
                   v
          +--------------------+
          | DocumentPermission |
          +--------------------+
```

---

# Access Model

TrustVault uses a combination of role-based access control and document-level permissions.

## Administrator

The administrator is allowed to access administrative functionality and review system-wide activity.

The administrator role is not automatically treated as the owner of every document.

## Document Owner

The document owner can manage documents they own.

Owners can:

- Upload documents
- View their documents
- Share documents
- Grant permissions
- Revoke permissions
- Manage owned documents

## Viewer

A viewer can access a document only when the owner has granted the appropriate permission.

Knowing a document ID does not automatically provide access.

---

# Authorization Relationship

For a protected document operation, the application determines whether the current user is authorized.

Conceptually:

```text
Current User
     |
     v
Is authenticated?
     |
     v
Is user the document owner?
     |
   Yes -----> Allow
     |
    No
     |
     v
Does an active document permission exist?
     |
   Yes -----> Allow
     |
    No
     |
     v
    Deny
```

The authorization decision is performed server-side.

---

# Database Security Considerations

## Password Security

Passwords are stored as password hashes rather than plaintext passwords.

## Document Authorization

Document IDs are not treated as authorization credentials.

A user knowing another user's document ID does not automatically provide access.

## Permission Revocation

Document permissions are checked when protected operations are performed.

When an owner revokes a user's permission, subsequent authorization checks should no longer allow that user to access the document.

## Auditability

Important document and permission operations are recorded in the audit log.

---

# Database Setup

The application uses SQLAlchemy for database access.

Flask-Migrate/Alembic is used to manage database schema migrations.

Typical migration commands are:

```powershell
flask db current
flask db heads
flask db migrate -m "migration description"
flask db upgrade
```

For a clean development setup, the application's configured database is created using the application's database configuration and migration process.

---

# Current Development Database

The project uses SQLite during development.

The database connection is configured through the application's environment configuration.

The default development configuration uses:

```text
sqlite:///trustvault.db
```

Production deployments can use a production database such as PostgreSQL.

---

# Seed Accounts

The development seed process provides accounts for testing the different roles.

Example:

```text
Administrator
Email: admin@trustvault.local

Owner
Email: owner@trustvault.local

Viewer
Email: recipient@trustvault.local
```

Passwords should not be committed to a public production repository. Development credentials are intended only for the challenge/demo environment.

---

# Schema Design Decisions

### Per-document permissions

Permissions are associated with individual documents rather than automatically granting access to all documents owned by a user.

### Named users

Permissions are granted to specific users.

### Separate audit records

Audit information is stored separately from document metadata so document activity can be reviewed independently.

### Application-controlled file storage

The original filename is stored as document metadata while the application controls the stored filename/path.

---

# Known Limitations

The current challenge implementation is intentionally smaller than a production enterprise document-management system.

Known limitations include:

- SQLite is used for development.
- Local filesystem storage is used for development document storage.
- Audit records are database-backed.
- There is no external immutable audit-log service.
- The permission model is document-level rather than folder/group based.

These are documented design decisions rather than hidden functionality.

---

# Schema Summary

| Table | Purpose |
|---|---|
| `users` | Authentication and user roles |
| `documents` | Uploaded document metadata |
| `document_permissions` | Per-document user permissions |
| `audit_logs` | Document and permission activity |

The schema is designed around the central TrustVault requirement:

> A document must only be reachable by a user who has been granted access, and the system must be able to show who performed important actions and when.