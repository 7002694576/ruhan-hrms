from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "hrms.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'Active'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()

    total_employees = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    present_today = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE status='Present'"
    ).fetchone()[0]

    on_leave = conn.execute(
        "SELECT COUNT(*) FROM leaves WHERE status='Approved'"
    ).fetchone()[0]

    pending_leaves = conn.execute(
        "SELECT COUNT(*) FROM leaves WHERE status='Pending'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_employees=total_employees,
        present_today=present_today,
        on_leave=on_leave,
        pending_leaves=pending_leaves
    )


@app.route("/employees")
def employees():
    conn = get_db()
    employees = conn.execute(
        "SELECT * FROM employees ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("employees.html", employees=employees)


@app.route("/add_employee", methods=["POST"])
def add_employee():
    employee_id = request.form["employee_id"]
    name = request.form["name"]
    department = request.form["department"]
    designation = request.form["designation"]
    email = request.form["email"]
    phone = request.form["phone"]

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO employees
            (employee_id, name, department, designation, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            employee_id,
            name,
            department,
            designation,
            email,
            phone
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect(url_for("employees"))


@app.route("/attendance")
def attendance():
    conn = get_db()

    records = conn.execute("""
        SELECT * FROM attendance
        ORDER BY id DESC
    """).fetchall()

    employees = conn.execute("""
        SELECT employee_id, name FROM employees
        WHERE status='Active'
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "attendance.html",
        records=records,
        employees=employees
    )


@app.route("/add_attendance", methods=["POST"])
def add_attendance():
    employee_id = request.form["employee_id"]
    date = request.form["date"]
    status = request.form["status"]

    conn = get_db()

    conn.execute("""
        INSERT INTO attendance
        (employee_id, date, status)
        VALUES (?, ?, ?)
    """, (
        employee_id,
        date,
        status
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("attendance"))


@app.route("/leave")
def leave():
    conn = get_db()

    leaves = conn.execute("""
        SELECT * FROM leaves
        ORDER BY id DESC
    """).fetchall()

    employees = conn.execute("""
        SELECT employee_id, name FROM employees
        WHERE status='Active'
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "leave.html",
        leaves=leaves,
        employees=employees
    )


@app.route("/add_leave", methods=["POST"])
def add_leave():
    employee_id = request.form["employee_id"]
    leave_type = request.form["leave_type"]
    from_date = request.form["from_date"]
    to_date = request.form["to_date"]
    reason = request.form["reason"]

    conn = get_db()

    conn.execute("""
        INSERT INTO leaves
        (employee_id, leave_type, from_date, to_date, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (
        employee_id,
        leave_type,
        from_date,
        to_date,
        reason
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("leave"))


@app.route("/leave/<int:leave_id>/<string:status>")
def update_leave(leave_id, status):
    if status not in ["Approved", "Rejected"]:
        return redirect(url_for("leave"))

    conn = get_db()

    conn.execute("""
        UPDATE leaves
        SET status=?
        WHERE id=?
    """, (
        status,
        leave_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("leave"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
