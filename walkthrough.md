# Walkthrough — PDP University Career Center

**PDP University Career Center** is a production-grade white-labelable Career Center AI platform currently branded for **PDP University**. It provides a dual-sided experience:
1. **Student Side (Telegram Bot)**: Powered by a multi-lingual state machine for skill audits, ATS resume validation, STAR interview practice, and vacancy matchmaking.
2. **Admin Side (Vite + React Dashboard)**: High-contrast, projector-ready analytical panel with student skill directories, curriculum deficit analyzers, and detailed student dossiers.

---

## 🚀 Key Admin Dashboard Authentication Updates

We updated the Admin Web login system to align with staging and production requirements:

### 1. Removed Google OAuth from UI
* Excluded Google Cloud Console configuration loading and the Google Identity SDK integration on the login screen.
* Staff members are no longer forced to configure or rely on live Google OAuth project credentials.

### 2. Implemented Secure Custom Staff Sign-In
* Added a clean, professional Email & Password form under the staff login section.
* Credentials are submitted directly to the `/auth/login` endpoint, validating inputs against the `staff_users` SQLite database allowlist and the secure environment-only `ADMIN_PASSWORD` variable.
* Added translations for all form labels, buttons, and validation warnings in English and Uzbek.

### 3. Primary Demo Mode Access
* Designed a prominent primary action button for **Demo rejimga kirish** (Access Demo Mode) styled in the official PDP brand color (`var(--primary)`).
* Allows instant, single-click entry into a fully populated mock dashboard context for demonstration and hackathon testing.

---

## 🛠️ Verification & Verification Commands

### 1. Build Compilation
We verified that the React dashboard builds cleanly with Vite and has no TypeScript or syntax compiler issues:
```bash
cd dashboard && npm run build
```
**Output:**
```
vite v8.0.14 building client environment for production...
✓ 1738 modules transformed.
dist/index.html                   0.89 kB │ gzip:  0.48 kB
dist/assets/index-C_SAMRIy.css   12.51 kB │ gzip:  2.97 kB
dist/assets/index-Cdc53jeg.js   288.64 kB │ gzip: 82.32 kB
✓ built in 133ms
```

### 2. Integration Tests
We executed the integration script `scratch/verify_custom_auth.py` which validated the authentication scenarios:
```bash
PYTHONPATH=. .venv/bin/python scratch/verify_custom_auth.py
```
**Output:**
```
Testing Backend Custom Email & Password Login...
1. Testing incorrect password...
  ✅ Correctly failed: Status 401, Body: {"detail":"Noto'g'ri parol. / Incorrect password."}
2. Testing incorrect/non-allowlisted email...
  ✅ Correctly failed: Status 403, Body: {"detail":"Kirish taqiqlandi. Sizning emailingiz ro'yxatdan o'tmagan. / Access denied. Your email is not allowlisted."}
3. Testing successful login with allowlisted email & correct password...
  ✅ Success: Status 200, Body: {"id":1,"email":"mirjalol0331@gmail.com","name":"Mirjalol0331","role":"super_admin","department":"career","avatar_url":null}
  ✅ Issued Cookies: {'pdp_access_token': '...', 'pdp_refresh_token': '...'}

🎉 All custom authentication backend tests passed successfully!
```
