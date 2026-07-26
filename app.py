"""
app.py
Flask backend for the ZEEROSTOCK HRMS assignment.

- Serves the HTML/CSS/JS frontend (templates/ + static/)
- Exposes a JSON REST API consumed by the frontend JS via fetch()
- Session-based authentication (server-side session cookie) with
  password hashing (werkzeug.security)
- Role-based access control for HR vs Employee
- Uses plain Python sqlite3 (database.py) -- no MySQL, no ORM

Run with:  python app.py
Server starts on http://127.0.0.1:5000
"""

from datetime import datetime, date
from functools import wraps

from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, init_db

app = Flask(__name__)
app.secret_key = "zeerostock-hrms-dev-secret-key-change-in-production"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["JSON_SORT_KEYS"] = False


# --------------------------------------------------------------------------
# Auth helpers / decorators
# --------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Authentication required"}), 401
            if session.get("role") != role:
                return jsonify({"error": "Forbidden: insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def current_employee_id(db):
    """Look up the employees.id row for the logged-in user."""
    row = db.execute(
        "SELECT id FROM employees WHERE user_id = ?", (session["user_id"],)
    ).fetchone()
    return row["id"] if row else None


# --------------------------------------------------------------------------
# Frontend page routes (serve HTML; JS on each page calls the JSON API)
# --------------------------------------------------------------------------

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return redirect(url_for("hr_dashboard_page") if session["role"] == "HR"
                     else url_for("employee_dashboard_page"))


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/hr/dashboard")
def hr_dashboard_page():
    return render_template("hr_dashboard.html")


@app.route("/hr/employees")
def hr_employees_page():
    return render_template("hr_employees.html")


@app.route("/hr/attendance")
def hr_attendance_page():
    return render_template("hr_attendance.html")


@app.route("/hr/leaves")
def hr_leaves_page():
    return render_template("hr_leaves.html")


@app.route("/employee/dashboard")
def employee_dashboard_page():
    return render_template("employee_dashboard.html")


@app.route("/employee/attendance")
def employee_attendance_page():
    return render_template("employee_attendance.html")


@app.route("/employee/leaves")
def employee_leaves_page():
    return render_template("employee_leaves.html")


@app.route("/employee/profile")
def employee_profile_page():
    return render_template("employee_profile.html")


# ==========================================================================
# API: Authentication
# ==========================================================================

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["email"] = user["email"]

    return jsonify({
        "message": "Login successful",
        "user": {"id": user["id"], "email": user["email"], "role": user["role"]}
    })


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me", methods=["GET"])
@login_required
def api_me():
    return jsonify({
        "id": session["user_id"], "email": session["email"], "role": session["role"]
    })


# ==========================================================================
# API: HR - Dashboard
# ==========================================================================

@app.route("/api/hr/dashboard", methods=["GET"])
@role_required("HR")
def hr_dashboard():
    db = get_db()
    today = date.today().isoformat()

    total_employees = db.execute("SELECT COUNT(*) c FROM employees").fetchone()["c"]

    present_today = db.execute(
        "SELECT COUNT(DISTINCT employee_id) c FROM attendance WHERE date = ? AND check_in IS NOT NULL",
        (today,)
    ).fetchone()["c"]

    on_leave_today = db.execute(
        """SELECT COUNT(*) c FROM leaves
           WHERE status = 'Approved' AND ? BETWEEN start_date AND end_date""",
        (today,)
    ).fetchone()["c"]

    recent = db.execute(
        """SELECT a.date, a.check_in, a.check_out, a.status, e.name
           FROM attendance a JOIN employees e ON e.id = a.employee_id
           ORDER BY a.date DESC, a.id DESC LIMIT 10"""
    ).fetchall()
    db.close()

    return jsonify({
        "total_employees": total_employees,
        "present_today": present_today,
        "on_leave_today": on_leave_today,
        "recent_activity": [dict(r) for r in recent]
    })


# ==========================================================================
# API: HR - Employee Management
# ==========================================================================

@app.route("/api/hr/employees", methods=["GET"])
@role_required("HR")
def hr_list_employees():
    q = (request.args.get("q") or "").strip()
    db = get_db()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            """SELECT e.*, u.email as login_email FROM employees e
               JOIN users u ON u.id = e.user_id
               WHERE e.name LIKE ? OR e.email LIKE ? OR e.department LIKE ?
                  OR e.designation LIKE ?
               ORDER BY e.id DESC""",
            (like, like, like, like)
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT e.*, u.email as login_email FROM employees e
               JOIN users u ON u.id = e.user_id ORDER BY e.id DESC"""
        ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/hr/employees", methods=["POST"])
@role_required("HR")
def hr_add_employee():
    data = request.get_json(silent=True) or {}
    required = ["name", "email", "date_of_joining"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    default_password = data.get("password") or "Welcome@123"

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        db.close()
        return jsonify({"error": "A user with this email already exists"}), 409

    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'Employee')",
        (email, generate_password_hash(default_password))
    )
    user_id = cur.lastrowid

    cur.execute(
        """INSERT INTO employees (user_id, name, email, phone, department, designation, date_of_joining)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, data["name"], email, data.get("phone"), data.get("department"),
         data.get("designation"), data.get("date_of_joining"))
    )
    db.commit()
    emp_id = cur.lastrowid
    db.close()

    return jsonify({
        "message": "Employee added",
        "employee_id": emp_id,
        "login_email": email,
        "temporary_password": default_password
    }), 201


@app.route("/api/hr/employees/<int:emp_id>", methods=["GET"])
@role_required("HR")
def hr_get_employee(emp_id):
    db = get_db()
    row = db.execute(
        """SELECT e.*, u.email as login_email FROM employees e
           JOIN users u ON u.id = e.user_id WHERE e.id = ?""", (emp_id,)
    ).fetchone()
    db.close()
    if not row:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(dict(row))


@app.route("/api/hr/employees/<int:emp_id>", methods=["PUT"])
@role_required("HR")
def hr_edit_employee(emp_id):
    data = request.get_json(silent=True) or {}
    fields = ["name", "email", "phone", "department", "designation", "date_of_joining"]
    updates = {k: v for k, v in data.items() if k in fields}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    db = get_db()
    row = db.execute("SELECT * FROM employees WHERE id = ?", (emp_id,)).fetchone()
    if not row:
        db.close()
        return jsonify({"error": "Employee not found"}), 404

    set_clause = ", ".join([f"{k} = ?" for k in updates])
    db.execute(f"UPDATE employees SET {set_clause} WHERE id = ?",
               (*updates.values(), emp_id))

    if "email" in updates:
        db.execute("UPDATE users SET email = ? WHERE id = ?",
                   (updates["email"].strip().lower(), row["user_id"]))

    db.commit()
    db.close()
    return jsonify({"message": "Employee updated"})


# ==========================================================================
# API: HR - Attendance Management
# ==========================================================================

@app.route("/api/hr/attendance", methods=["GET"])
@role_required("HR")
def hr_attendance():
    employee_id = request.args.get("employee_id")
    date_filter = request.args.get("date")

    query = """SELECT a.*, e.name as employee_name FROM attendance a
               JOIN employees e ON e.id = a.employee_id WHERE 1=1"""
    params = []
    if employee_id:
        query += " AND a.employee_id = ?"
        params.append(employee_id)
    if date_filter:
        query += " AND a.date = ?"
        params.append(date_filter)
    query += " ORDER BY a.date DESC, e.name ASC"

    db = get_db()
    rows = db.execute(query, params).fetchall()
    employees = db.execute("SELECT id, name FROM employees ORDER BY name").fetchall()
    db.close()
    return jsonify({
        "records": [dict(r) for r in rows],
        "employees": [dict(e) for e in employees]
    })


# ==========================================================================
# API: HR - Leave Management
# ==========================================================================

@app.route("/api/hr/leaves", methods=["GET"])
@role_required("HR")
def hr_leaves():
    status_filter = request.args.get("status")
    db = get_db()
    query = """SELECT l.*, e.name as employee_name FROM leaves l
               JOIN employees e ON e.id = l.employee_id WHERE 1=1"""
    params = []
    if status_filter:
        query += " AND l.status = ?"
        params.append(status_filter)
    query += " ORDER BY l.applied_at DESC"
    rows = db.execute(query, params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/hr/leaves/<int:leave_id>", methods=["PUT"])
@role_required("HR")
def hr_decide_leave(leave_id):
    data = request.get_json(silent=True) or {}
    decision = data.get("status")
    if decision not in ("Approved", "Rejected"):
        return jsonify({"error": "Status must be 'Approved' or 'Rejected'"}), 400

    db = get_db()
    row = db.execute("SELECT * FROM leaves WHERE id = ?", (leave_id,)).fetchone()
    if not row:
        db.close()
        return jsonify({"error": "Leave request not found"}), 404

    db.execute(
        "UPDATE leaves SET status = ?, decided_at = ? WHERE id = ?",
        (decision, datetime.now().isoformat(timespec="seconds"), leave_id)
    )
    db.commit()
    db.close()
    return jsonify({"message": f"Leave {decision.lower()}"})


# ==========================================================================
# API: Employee - Dashboard
# ==========================================================================

@app.route("/api/employee/dashboard", methods=["GET"])
@role_required("Employee")
def employee_dashboard():
    db = get_db()
    emp_id = current_employee_id(db)
    if emp_id is None:
        db.close()
        return jsonify({"error": "Employee profile not found"}), 404

    profile = db.execute("SELECT * FROM employees WHERE id = ?", (emp_id,)).fetchone()
    today = date.today().isoformat()

    today_attendance = db.execute(
        "SELECT * FROM attendance WHERE employee_id = ? AND date = ?", (emp_id, today)
    ).fetchone()

    leave_counts = db.execute(
        """SELECT status, COUNT(*) c FROM leaves WHERE employee_id = ? GROUP BY status""",
        (emp_id,)
    ).fetchall()

    recent_notifications = []
    recent_leave = db.execute(
        """SELECT * FROM leaves WHERE employee_id = ? AND status != 'Pending'
           ORDER BY decided_at DESC LIMIT 3""", (emp_id,)
    ).fetchall()
    for lv in recent_leave:
        recent_notifications.append(
            f"Your leave request ({lv['start_date']} to {lv['end_date']}) was {lv['status'].lower()}."
        )
    db.close()

    return jsonify({
        "profile": dict(profile) if profile else None,
        "today_attendance": dict(today_attendance) if today_attendance else None,
        "leave_summary": {r["status"]: r["c"] for r in leave_counts},
        "notifications": recent_notifications
    })


# ==========================================================================
# API: Employee - Attendance
# ==========================================================================

@app.route("/api/employee/attendance", methods=["GET"])
@role_required("Employee")
def employee_attendance_history():
    db = get_db()
    emp_id = current_employee_id(db)
    rows = db.execute(
        "SELECT * FROM attendance WHERE employee_id = ? ORDER BY date DESC", (emp_id,)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/employee/attendance/checkin", methods=["POST"])
@role_required("Employee")
def employee_checkin():
    db = get_db()
    emp_id = current_employee_id(db)
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M:%S")

    existing = db.execute(
        "SELECT * FROM attendance WHERE employee_id = ? AND date = ?", (emp_id, today)
    ).fetchone()
    if existing and existing["check_in"]:
        db.close()
        return jsonify({"error": "Already checked in today"}), 409

    if existing:
        db.execute("UPDATE attendance SET check_in = ?, status = 'Present' WHERE id = ?",
                   (now, existing["id"]))
    else:
        db.execute(
            "INSERT INTO attendance (employee_id, date, check_in, status) VALUES (?, ?, ?, 'Present')",
            (emp_id, today, now)
        )
    db.commit()
    db.close()
    return jsonify({"message": "Checked in", "time": now})


@app.route("/api/employee/attendance/checkout", methods=["POST"])
@role_required("Employee")
def employee_checkout():
    db = get_db()
    emp_id = current_employee_id(db)
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M:%S")

    existing = db.execute(
        "SELECT * FROM attendance WHERE employee_id = ? AND date = ?", (emp_id, today)
    ).fetchone()
    if not existing or not existing["check_in"]:
        db.close()
        return jsonify({"error": "You must check in before checking out"}), 400
    if existing["check_out"]:
        db.close()
        return jsonify({"error": "Already checked out today"}), 409

    db.execute("UPDATE attendance SET check_out = ? WHERE id = ?", (now, existing["id"]))
    db.commit()
    db.close()
    return jsonify({"message": "Checked out", "time": now})


# ==========================================================================
# API: Employee - Leave Requests
# ==========================================================================

@app.route("/api/employee/leaves", methods=["GET"])
@role_required("Employee")
def employee_leaves_history():
    db = get_db()
    emp_id = current_employee_id(db)
    rows = db.execute(
        "SELECT * FROM leaves WHERE employee_id = ? ORDER BY applied_at DESC", (emp_id,)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/employee/leaves", methods=["POST"])
@role_required("Employee")
def employee_apply_leave():
    data = request.get_json(silent=True) or {}
    required = ["leave_type", "start_date", "end_date"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if data["start_date"] > data["end_date"]:
        return jsonify({"error": "Start date must be before end date"}), 400

    db = get_db()
    emp_id = current_employee_id(db)
    db.execute(
        """INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason)
           VALUES (?, ?, ?, ?, ?)""",
        (emp_id, data["leave_type"], data["start_date"], data["end_date"], data.get("reason", ""))
    )
    db.commit()
    db.close()
    return jsonify({"message": "Leave request submitted"}), 201


# ==========================================================================
# API: Employee - Profile
# ==========================================================================

@app.route("/api/employee/profile", methods=["GET"])
@role_required("Employee")
def employee_get_profile():
    db = get_db()
    emp_id = current_employee_id(db)
    row = db.execute("SELECT * FROM employees WHERE id = ?", (emp_id,)).fetchone()
    db.close()
    if not row:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(dict(row))


@app.route("/api/employee/profile", methods=["PUT"])
@role_required("Employee")
def employee_update_profile():
    data = request.get_json(silent=True) or {}
    editable = ["phone", "department_note"]  # employees may edit limited fields
    allowed = ["phone"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No editable fields provided (only phone can be edited)"}), 400

    db = get_db()
    emp_id = current_employee_id(db)
    set_clause = ", ".join([f"{k} = ?" for k in updates])
    db.execute(f"UPDATE employees SET {set_clause} WHERE id = ?", (*updates.values(), emp_id))
    db.commit()
    db.close()
    return jsonify({"message": "Profile updated"})


@app.route("/api/employee/change-password", methods=["PUT"])
@role_required("Employee")
def employee_change_password():
    data = request.get_json(silent=True) or {}
    current_pw = data.get("current_password") or ""
    new_pw = data.get("new_password") or ""

    if len(new_pw) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    if not check_password_hash(user["password_hash"], current_pw):
        db.close()
        return jsonify({"error": "Current password is incorrect"}), 401

    db.execute("UPDATE users SET password_hash = ? WHERE id = ?",
               (generate_password_hash(new_pw), user["id"]))
    db.commit()
    db.close()
    return jsonify({"message": "Password changed successfully"})


# --------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("login.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
