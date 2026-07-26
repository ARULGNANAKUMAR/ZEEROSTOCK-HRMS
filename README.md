# ZEEROSTOCK HRMS

A basic Human Resource Management System built for the ZEEROSTOCK full-stack
developer assignment.

## Tech stack

| Layer          | Technology |
|----------------|------------|
| Frontend       | HTML, CSS, vanilla JavaScript (fetch API) |
| Backend        | Python, Flask (`app.py`) |
| Database       | SQLite via Python's built-in `sqlite3` module — plain hand-written SQL, no ORM, no MySQL server |
| Auth           | Session-cookie based auth, passwords hashed with Werkzeug's `generate_password_hash` / `check_password_hash` |

The Flask app (`app.py`) both serves the HTML/CSS/JS frontend (via
`render_template` + the `static/` folder) **and** exposes a JSON REST API
(`/api/...`) that the frontend JavaScript calls with `fetch()`. This is the
"frontend/backend connection" layer requested in the assignment.

## Project structure

```
hrms/
├── app.py                  # Flask app: page routes + REST API + auth
├── database.py             # sqlite3 connection helper + init/seed logic
├── schema.sql              # Table definitions (users, employees, attendance, leaves)
├── requirements.txt
├── instance/
│   └── hrms.db             # SQLite database file (created automatically)
├── templates/               # Jinja HTML pages
│   ├── login.html
│   ├── hr_dashboard.html / hr_employees.html / hr_attendance.html / hr_leaves.html
│   ├── employee_dashboard.html / employee_attendance.html / employee_leaves.html / employee_profile.html
│   └── _hr_sidebar.html / _employee_sidebar.html (shared nav partials)
└── static/
    ├── css/style.css
    └── js/ (api.js helper + one script per page)
```

## Setup instructions

1. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python app.py
   ```
   The first run automatically creates `instance/hrms.db` from `schema.sql`
   and seeds a default HR account. The server starts at:
   ```
   http://127.0.0.1:5000
   ```

4. **Log in**

   Default HR login (seeded automatically):
   ```
   Email:    hr@zeerostock.com
   Password: HrAdmin@123
   ```

   Employee accounts don't exist yet on a fresh database — log in as HR,
   go to **Employee Management → + Add Employee**, and create one. The
   employee's login email is the email you enter, and the login password
   is either the "Temporary Login Password" you type or the default
   `Welcome@123` if left blank.

## Resetting the database

To wipe and recreate the database (e.g. during development):
```bash
python database.py
```
This drops and recreates all tables and reseeds the default HR account.

## Features implemented

**Authentication**
- Login / logout, hashed passwords, server-side session auth
- Role-based access control (HR vs Employee) enforced on every API route

**HR Portal**
- Dashboard: total employees, present today, on leave today, recent attendance activity
- Employee Management: add / edit / list / search employees
- Attendance Management: view records, filter by employee and date, see check-in/out times
- Leave Management: view, approve, reject leave requests

**Employee Portal**
- Dashboard: personal info, today's attendance status, leave summary, notifications
- Attendance: check in, check out, view history
- Leave Requests: apply, view status and history
- Profile: view profile, edit phone number, change password

## Notes / assumptions

- Employee accounts are provisioned by HR (there's no public self-signup, which
  matches a typical HRMS).
- "Department" edits are restricted to HR; employees can edit their phone
  number and password themselves from the Profile page.
- The secret key in `app.py` is a hardcoded development value — in a real
  deployment this should come from an environment variable.
- No external services (e.g. email) are wired up; leave-decision
  "notifications" are surfaced in-app on the employee dashboard instead.
