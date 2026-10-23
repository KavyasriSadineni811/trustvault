# TrustVault API Documentation

## Overview

TrustVault is a secure document-sharing platform with authentication, document-level permissions, access control, audit logging, search/filtering, and administrative monitoring.

All protected endpoints perform server-side authentication and authorization checks.

---

# Authentication

## POST `/auth/login`

Authenticates a user and creates a login session.

### Access

Public.

### Request

```text
email
password
```

### Supported roles

- Administrator
- Document Owner
- Viewer

### Example accounts

```text
Administrator:
admin@trustvault.local

Owner:
owner@trustvault.local

Viewer:
recipient@trustvault.local
```

---

## POST `/auth/logout`

Logs out the currently authenticated user.

### Access

Authenticated users.

### Effect

Ends the current authenticated session.

---

# Documents

## GET `/documents/`

Displays the document dashboard.

### Access

Authenticated users.

### Features

- View owned documents
- View documents shared with the user
- Search documents
- Filter by owner
- Filter by category
- Filter by upload date

---

## GET `/documents/upload`

Displays the document upload form.

### Access

Authenticated users.

---

## POST `/documents/upload`

Uploads a new document.

### Access

Authenticated users.

### Validation

The application validates uploaded files against the supported file types.

### Security

Uploaded files are associated with the authenticated user as the document owner.

---

## GET `/documents/download/<document_id>`

Downloads a document.

### Access

Authenticated users with permission to access the document.

### Authorization

The server verifies that the current user:

1. Owns the document, or
2. Has an active permission for the document.

Knowing the document ID alone does not grant access.

---

## GET `/documents/edit/<document_id>`

Displays the document editing interface.

### Access

The document owner or a user with edit permission.

---

## POST `/documents/edit/<document_id>`

Updates an existing document.

### Access

The document owner or a user with edit permission.

### Security

Authorization is checked on the server before the document is modified.

---

## POST `/documents/delete/<document_id>`

Deletes a document.

### Access

The document owner or an authorized user according to the application's permission rules.

### Security

The document ID alone is not sufficient to perform deletion.

---

# Document Permissions

## POST `/documents/<document_id>/share`

Shares a document with a named user.

### Access

Document owner.

### Request

The request identifies the recipient who should receive access.

### Supported permissions

- Read
- Edit

### Security

Only the document owner can grant document access.

A normal viewer cannot grant themselves access.

### Audit

A successful permission change generates an audit record with the relevant user, document, action and timestamp.

---

## POST `/documents/<document_id>/revoke/<user_id>`

Revokes a user's permission to a document.

### Access

Document owner.

### Effect

Removes the selected user's active permission.

### Security

Authorization is checked server-side.

After revocation, subsequent protected requests must perform the permission check again.

### Audit

The revocation is recorded in the audit activity.

---

# Document Audit

## GET `/documents/<document_id>/audit`

Displays audit activity for a specific document.

### Access

Authenticated users according to the application's audit-access rules.

### Audit information

Audit records can contain:

- User
- Document
- Action
- Timestamp

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

---

# Administrative Activity

## GET `/documents/admin/activity`

Displays system-wide document activity.

### Access

Administrator.

### Purpose

Allows an administrator to review document-related activity across the system.

### Example information

```text
User
Document
Action
Date & Time
```

Example:

```text
owner@trustvault.local
trustvault_test.txt
UPLOAD
2026-10-22 10:59:54
```

---

# Administrator Dashboard

## GET `/admin/`

Displays the administrator dashboard.

### Access

Administrator only.

### Features

- System-wide activity
- Permission management view
- Document activity monitoring
- Administrative controls

Normal document owners and viewers must not access administrator-only functionality.

---

# Administrator Permissions

## GET `/admin/permissions`

Displays document permission information for administrative review.

### Access

Administrator only.

### Purpose

Allows the administrator to inspect document permissions and access assignments.

---

# Authorization Model

TrustVault uses role-based access control together with document-level permissions.

## Administrator

The administrator can access administrative monitoring functionality.

The administrator is not automatically treated as the owner of every document.

## Document Owner

The document owner can:

- Upload documents
- Manage owned documents
- Grant document permissions
- Revoke document permissions
- Access owned documents
- Review applicable document activity

## Viewer

A viewer can access documents only when the document owner has granted the required permission.

A viewer cannot automatically access every document in the system.

---

# Security Rules

The following rules apply to protected document operations:

1. Authentication is required.
2. Authorization is performed on the server.
3. Document IDs are not treated as authorization credentials.
4. Hidden UI buttons are not considered security controls.
5. Direct URL access is subject to the same authorization checks.
6. Download requests require authorization.
7. Edit requests require authorization.
8. Delete requests require authorization.
9. Permission changes require authorization.
10. Revoked permissions must no longer authorize subsequent protected requests.
11. Important document and permission operations are recorded in the audit trail.

---

# Endpoint Summary

| Endpoint | Method | Access |
|---|---|---|
| `/auth/login` | GET/POST | Public |
| `/auth/logout` | POST | Authenticated |
| `/documents/` | GET | Authenticated |
| `/documents/upload` | GET/POST | Authenticated |
| `/documents/<document_id>/share` | POST | Owner |
| `/documents/<document_id>/revoke/<user_id>` | POST | Owner |
| `/documents/download/<document_id>` | GET | Authorized user |
| `/documents/edit/<document_id>` | GET/POST | Owner/Edit permission |
| `/documents/delete/<document_id>` | POST | Authorized user |
| `/documents/<document_id>/audit` | GET | Authorized user |
| `/documents/admin/activity` | GET | Administrator |
| `/admin/` | GET | Administrator |
| `/admin/permissions` | GET | Administrator |

---

# Security Testing

The API was tested against unauthorized access scenarios including:

- Direct document URL access
- Unauthorized downloads
- Unauthorized editing
- Unauthorized deletion
- Unauthorized sharing
- Access after permission revocation
- Cross-user document access
- Role-based administrative access

The automated security tests are intended to verify that a user cannot access another user's documents without an appropriate permission.