# TrustVault — Threat Model

## Purpose

TrustVault is a secure document-sharing platform designed around two main security goals:

1. A document must only be reachable by users who have been explicitly granted access.
2. The system must provide an audit trail showing who performed important actions and when.

This document describes the main threats considered during development, the protections implemented, and known limitations.

---

## 1. Unauthorized Document Access

### Threat

A user may try to access another user's document without being granted permission.

An attacker may attempt this by:

- Opening a document URL directly.
- Guessing a document ID.
- Accessing a download URL manually.
- Accessing an edit URL manually.
- Accessing a delete URL manually.
- Bypassing buttons or links in the user interface.

### Protection

TrustVault performs authorization checks on the server for document operations.

Access is based on the authenticated user and the document's ownership or explicit document permission.

The UI hiding a button is not treated as the security boundary.

### Verification

I tested document access using different user accounts and verified that users without permission cannot access protected documents.

### Status

**Mitigated**

---

## 2. Unauthorized Download

### Threat

A user who does not have permission may attempt to download a document by directly calling the download endpoint.

### Protection

The download operation performs authentication and document authorization checks before allowing the file to be returned.

The user must either own the document or have an appropriate permission.

### Verification

I tested the download functionality using users with and without document permissions.

### Status

**Mitigated**

---

## 3. Unauthorized Edit

### Threat

A user may attempt to modify another user's document by directly accessing the edit endpoint instead of using the application interface.

### Protection

The server checks whether the authenticated user has the required permission before allowing the document to be edited.

### Verification

The edit route was tested with authorized and unauthorized users.

### Status

**Mitigated**

---

## 4. Unauthorized Delete

### Threat

A user may attempt to delete another user's document by manually constructing a delete request.

### Protection

Deletion is protected by server-side authentication and authorization checks.

A user cannot delete a document merely because they know its document ID.

### Verification

Delete operations were tested using different accounts.

### Status

**Mitigated**

---

## 5. Unauthorized Permission Changes

### Threat

A user may attempt to grant themselves or another user access to a document they do not own.

### Protection

Document sharing and revocation are controlled by the document owner.

Permission changes are processed through protected server-side routes.

### Verification

Sharing and revocation were tested using owner and recipient accounts.

### Status

**Mitigated**

---

## 6. Revoked Access Still Working

### Threat

A user who previously had access may continue accessing a document after the owner revokes their permission.

This is an important threat because the challenge requires access removal to take effect immediately.

### Protection

TrustVault checks the current document permission when the user attempts to access the document.

Access is not based only on a previously issued URL.

Therefore, revoking a user's permission removes their authorization for subsequent protected requests.

### Verification

I tested the following sequence:

1. Owner uploads a document.
2. Owner shares the document with the recipient.
3. Recipient accesses the document.
4. Owner revokes the recipient's access.
5. Recipient attempts to access the document again.

### Status

**Mitigated**

---

## 7. Audit Trail Missing Important Activity

### Threat

A document may be accessed, shared or revoked without a corresponding audit record.

This would make it difficult to determine who performed an action after a security incident.

### Protection

TrustVault records important document and permission activities in the audit log.

Examples include:

- UPLOAD
- READ
- SHARE
- REVOKE
- DOWNLOAD
- EDIT
- DELETE

Audit records contain information such as the user, document, action and timestamp.

### Verification

I manually performed document operations and checked that corresponding audit records were generated.

### Status

**Mitigated**

---

## 8. Audit Trail Being Modified or Deleted

### Threat

An attacker or privileged application user may attempt to modify audit records in order to hide evidence of document access.

### Protection

The application treats audit records as security evidence and restricts normal users from modifying audit records through the application interface.

The administrator activity interface provides visibility into recorded activity.

### Known Limitation

The current implementation does not provide a separate external append-only audit service or cryptographically signed external log storage.

A database administrator with direct database access could potentially modify database records.

### Status

**Partially Mitigated**

### Accepted Risk

For this project, the database itself is treated as a trusted infrastructure component. Production deployment should use stronger append-only or externally protected logging for high-assurance environments.

---

## 9. User Guessing Document IDs

### Threat

An attacker may guess sequential document IDs and attempt to access documents belonging to other users.

### Protection

Document IDs are not treated as authorization.

Even if an attacker correctly guesses a valid document ID, the server performs the authorization check before returning protected document content.

### Verification

Direct document routes were tested using document IDs belonging to other users.

### Status

**Mitigated**

---

## 10. Access Through an Alternative Route

### Threat

An attacker may bypass the normal UI and call another route directly.

For example, hiding a Download button would not be sufficient if the download URL itself remained accessible.

### Protection

Authorization is enforced in protected server-side routes rather than relying only on frontend visibility.

### Verification

Protected URLs were tested directly instead of only using the visible application buttons.

### Status

**Mitigated**

---

## 11. Unauthenticated Access

### Threat

A person who is not logged in may attempt to access protected document operations.

### Protection

Protected routes require an authenticated session.

Unauthenticated users are redirected to the login interface where appropriate.

### Verification

Protected routes were accessed without logging in.

### Status

**Mitigated**

---

## 12. Cross-User Data Exposure

### Threat

A user may attempt to view documents, permissions or audit information belonging to another user without having the required role or permission.

### Protection

TrustVault separates users according to their roles and applies authorization checks to protected functionality.

Document permissions are stored per document rather than treating all documents as globally accessible.

### Verification

Owner, recipient and administrator accounts were tested separately.

### Status

**Mitigated**

---

## 13. Invalid File Upload

### Threat

A user may upload a file type that the application does not intend to support.

Unexpected file types may introduce security or processing risks.

### Protection

TrustVault validates uploaded files against the application's allowed file extensions/types.

The application does not blindly accept every file type.

### Verification

Supported and unsupported file types were tested during upload.

### Status

**Mitigated**

---

## 14. Malicious File Names

### Threat

A user may upload a file with a dangerous or unusual filename.

A malicious filename could potentially cause path traversal or filesystem problems if it were used directly as the storage path.

### Protection

Uploaded files are stored using application-controlled storage names rather than relying solely on the original filename.

The original filename is retained as document metadata while the stored filename is controlled by the application.

### Status

**Mitigated**

---

## 15. Session and Authentication Abuse

### Threat

An attacker may attempt to access protected functionality without a valid authenticated session.

### Protection

TrustVault uses Flask-Login for session-based authentication.

Protected routes use authentication requirements before performing protected operations.

### Verification

Login and logout flows were tested with the owner, recipient and administrator accounts.

### Status

**Mitigated**

---

# Threats Specifically Tested

The following security scenarios were included in testing:

| Threat | Tested |
|---|---|
| Unauthorized document read | Yes |
| Unauthorized document download | Yes |
| Unauthorized document edit | Yes |
| Unauthorized document deletion | Yes |
| Unauthorized sharing | Yes |
| Revoked user accessing document | Yes |
| Direct URL access | Yes |
| Document ID guessing | Yes |
| Audit activity generation | Yes |
| Role-based access | Yes |

---

# Security Design Principles

TrustVault follows these principles:

### Server-side authorization

Security decisions are made on the server rather than relying on hidden UI elements.

### Least privilege

Users receive access to individual documents rather than automatically receiving access to all documents belonging to another user.

### Explicit permissions

Access is granted to named users through document-level permissions.

### Immediate revocation

Current permissions are checked when protected operations are performed so that revoked access does not remain valid simply because the user previously had access.

### Auditability

Important document and permission operations generate audit records containing the acting user, document, action and timestamp.

---

# Known Limitations

The following limitations are acknowledged rather than hidden:

1. The current audit system is database-backed and does not use a separate tamper-proof external logging service.
2. The application is currently intended as a challenge/demo system rather than a production enterprise document-management platform.
3. Production deployment would require additional infrastructure hardening, secure secret management, HTTPS configuration, monitoring and stronger log protection.
4. Large-scale file storage would normally use dedicated object storage rather than local filesystem storage.
5. The current permission model is document-level rather than a full group/folder inheritance model.

These limitations do not change the core authorization requirement: protected document routes must verify the current user's permission before allowing access.

---

# Security Testing Philosophy

AI-generated code was treated as a starting point rather than as proof of security.

Security-sensitive functionality was manually inspected and tested, especially:

- Authentication
- Authorization
- Document access
- Download protection
- Permission changes
- Revocation
- Audit logging
- Administrative access

The main security question used during testing was:

> Can a user who should not have access reach the document by bypassing the normal interface?

The answer must remain **no**, including when the user attempts to access protected routes directly.