# Walkthrough — PDP University Career Center

**PDP University Career Center** is a production-grade white-labelable Career Center AI platform currently branded for **PDP University**. It provides a dual-sided experience:
1. **Student Side (Telegram Bot)**: Powered by a multi-lingual state machine for skill audits, ATS resume validation, STAR interview practice, and vacancy matchmaking.
2. **Admin Side (Vite + React Dashboard)**: High-contrast, projector-ready analytical panel with student skill directories, curriculum deficit analyzers, and detailed student dossiers.

---

## 🚀 Key Secure Admin Authentication Updates

We implemented a robust, production-grade custom authentication flow for staff members, deleting all public "Demo Mode" buttons and Google OAuth options from the viewport:

### 1. Database Schema Migrations
* Altered `staff_users` dynamically to support `password_hash TEXT` and `must_change_password INTEGER DEFAULT 1`.
* Runs SQLite `ALTER TABLE` queries safely on startup to ensure existing installations upgrade gracefully.

### 2. Password Hashing (PBKDF2 SHA-256)
* Uses standard library `hashlib.pbkdf2_hmac` and `secrets.token_hex` for secure hashing and salt management with zero-dependency binaries.
* Automatically hashes the default admin password (`admin123` from `.env`) on boot for `INITIAL_ADMIN_EMAIL` and sets their change requirement to `0` (false).

### 3. Temporary Password Flow
* Admin account creation (via POST `/api/admin/staff` or CLI `manage.py add-staff`) auto-generates a random 8-character temporary password (`secrets.token_hex(4)`), hashes it in the DB, sets `must_change_password = 1`, and outputs it for staff dispatch.

### 4. Forced Password Changes
* Signing in with a temporary password returns a redirection flag without setting JWT tokens.
* The frontend intercepts the flag and presents a **Set New Password** card.
* Submitting the new password updates it in the database via `/auth/change-password`, clears the requirement flag, and logs the user in.

### 5. Hidden Developer Backdoor
* Presenters and developers can boot the dashboard into offline mock/demo mode by signing in with the email `demo@pdp.uz` (no backend required).

---

## 🛠️ Verification & E2E Logs

### 1. Build Verification
Verified that the Vite compiler produces production bundles with zero compilation or type errors:
```bash
npm run build
```
**Output:**
```
vite v8.0.14 building client environment for production...
✓ 1738 modules transformed.
dist/index.html                   0.89 kB │ gzip:  0.49 kB
dist/assets/index-C_SAMRIy.css   12.51 kB │ gzip:  2.97 kB
dist/assets/index-C7ORAa9E.js   292.47 kB │ gzip: 82.92 kB
✓ built in 128ms
```

### 2. E2E Staff Authentication Tests
We executed the integration script `scratch/verify_real_auth.py` which validated the E2E flow:
```bash
PYTHONPATH=. .venv/bin/python scratch/verify_real_auth.py
```
**Output:**
```
🧪 Starting E2E Staff Hashed Authentication Test...

1. Logging in as Super Admin (seed)...
  Status: 200, Response: {'id': 1, 'email': 'mirjalol0331@gmail.com', 'name': 'Mirjalol0331', 'role': 'super_admin', 'department': 'career', 'avatar_url': None, 'must_change_password': False}

2. Creating a new career staff account...
  Status: 200, Response: {'status': 'ok', 'id': 3, 'temp_password': '8053c3f6'}
  ✅ Generated Temp Password: 8053c3f6

3. Logging in as new staff member with temporary password...
  Status: 200, Response: {'must_change_password': True, 'email': 'teststaff@pdp.uz'}

4. Changing password for new staff member...
  Status: 200, Response: {'id': 3, 'email': 'teststaff@pdp.uz', 'name': 'Test Staff Member', 'role': 'career_staff', 'department': 'career', 'avatar_url': None, 'must_change_password': False}

5. Verifying old temporary password fails now...
  Status: 401, Response: {'detail': "Noto'g'ri parol. / Incorrect password."}

6. Verifying login with new password succeeds...
  Status: 200, Response: {'id': 3, 'email': 'teststaff@pdp.uz', 'name': 'Test Staff Member', 'role': 'career_staff', 'department': 'career', 'avatar_url': None, 'must_change_password': False}

7. Checking that new career_staff is blocked from accessing allowlist APIs...
  Status: 403, Response: {'detail': 'Insufficient permissions. Required: super_admin'}
  ✅ Access correctly blocked for non-admin role!

🎉 ALL E2E STAFF AUTHENTICATION TESTS PASSED SUCCESSFULLY!
```
