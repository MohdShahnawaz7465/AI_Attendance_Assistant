from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from groq_helper import ask_ai
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'


# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Chat history
chat_history = []


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data[0], user_data[1])
    return None


def send_email_alert(student_name, percentage, recipient_email="student@example.com"):
    """Send email alert when attendance drops below 75%"""
    try:
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM email_settings WHERE id=1")
        settings = cursor.fetchone()
        conn.close()
        
        if settings and settings[1] == 1:  # email_enabled
            sender_email = settings[2]
            smtp_server = settings[3]
            smtp_port = settings[4]
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f'⚠️ Low Attendance Alert - {student_name}'
            
            body = f"""
Dear Student,

Your attendance has dropped below 75%.

Student Name: {student_name}
Current Attendance: {percentage}%

Please improve your attendance to avoid any issues.

Best regards,
AI Attendance System
"""
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.send_message(msg)
            server.quit()
            
            return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
    return False


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    student_data = []
    low_attendance = []

    for student in students:
        percentage = round((student[3] / student[4]) * 100, 2)

        if percentage >= 90:
            status = "Excellent"
        elif percentage >= 75:
            status = "Good"
        else:
            status = "Warning"

        student_info = {
            "id": student[0],
            "name": student[1],
            "roll_no": student[2],
            "present": student[3],
            "total": student[4],
            "percentage": percentage,
            "status": status
        }

        student_data.append(student_info)

        if percentage < 75:
            low_attendance.append(student_info)

    total_students = len(student_data)

    if student_data:
        highest_attendance = max(student_data, key=lambda x: x["percentage"])
        lowest_attendance = min(student_data, key=lambda x: x["percentage"])
    else:
        highest_attendance = {"name": "N/A", "percentage": 0}
        lowest_attendance = {"name": "N/A", "percentage": 0}

    ai_report = ""
    response = ""
    search_result = None
    search_message = ""
    delete_message = ""
    update_message = ""
    email_settings = None

    if request.method == "POST":

        if "clear_students" in request.form:
            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students")
            conn.commit()
            conn.close()
            return redirect(url_for("home"))

        if "delete_name" in request.form:
            delete_student_name = request.form["delete_name"].strip()
            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE name=?", (delete_student_name,))
            existing_student = cursor.fetchone()

            if existing_student is not None:
                cursor.execute("DELETE FROM students WHERE name=?", (delete_student_name,))
                conn.commit()
                delete_message = f"Student '{delete_student_name}' deleted successfully!"
            else:
                delete_message = f"Student '{delete_student_name}' not found."

            conn.close()
            return redirect(url_for("home"))

        if "new_name" in request.form:
            name = request.form["new_name"]
            roll = request.form["new_roll"]

            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE roll_no=?", (roll,))
            existing_student = cursor.fetchone()

            if existing_student is None:
                cursor.execute(
                    "INSERT INTO students (name, roll_no, present_days, total_days) VALUES (?, ?, ?, ?)",
                    (name, roll, int(request.form["present_days"]), int(request.form["total_days"]))
                )
                conn.commit()

            conn.close()
            return redirect(url_for("home"))

        if "update_student" in request.form:
            student_id = request.form["update_id"]
            present = int(request.form["update_present"])
            total = int(request.form["update_total"])

            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
            existing_student = cursor.fetchone()

            if existing_student is not None:
                old_percentage = (existing_student[3] / existing_student[4]) * 100
                new_percentage = (present / total) * 100

                cursor.execute(
                    "UPDATE students SET present_days=?, total_days=? WHERE id=?",
                    (present, total, student_id)
                )
                conn.commit()

                if new_percentage < 75 and old_percentage >= 75:
                    send_email_alert(existing_student[1], new_percentage)
                    update_message = f"Updated {existing_student[1]}'s attendance. Email alert sent!"
                else:
                    update_message = f"Updated {existing_student[1]}'s attendance successfully!"
            else:
                update_message = "Student not found."

            conn.close()
            return redirect(url_for("home"))

        if "save_email_settings" in request.form:
            email_enabled = 1 if request.form.get("email_enabled") else 0
            sender_email = request.form["sender_email"]
            smtp_server = request.form["smtp_server"]
            smtp_port = int(request.form["smtp_port"])

            conn = sqlite3.connect("attendance.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_settings WHERE id=1")
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "UPDATE email_settings SET email_enabled=?, sender_email=?, smtp_server=?, smtp_port=? WHERE id=1",
                    (email_enabled, sender_email, smtp_server, smtp_port)
                )
            else:
                cursor.execute(
                    "INSERT INTO email_settings (id, email_enabled, sender_email, smtp_server, smtp_port) VALUES (1, ?, ?, ?, ?)",
                    (email_enabled, sender_email, smtp_server, smtp_port)
                )
            conn.commit()
            conn.close()

            flash("Email settings saved!", "success")
            return redirect(url_for("home"))

        if "generate_report" in request.form:
            prompt = f"""
            Create a professional attendance report.

            Total Students: {total_students}
            Highest Attendance: {highest_attendance['name']} - {highest_attendance['percentage']}%
            Lowest Attendance: {lowest_attendance['name']} - {lowest_attendance['percentage']}%
            Students Below 75%: {low_attendance}

            Write:
            1. Summary
            2. Key Observations
            3. Recommendations
            """
            ai_report = ask_ai(prompt)

        if "question" in request.form:
            question = request.form["question"].lower()
            chat_history.append({"question": question, "user": current_user.username})

            if "highest" in question:
                response = f'{highest_attendance["name"]} has the highest attendance ({highest_attendance["percentage"]}%)'
            elif "lowest" in question:
                response = f'{lowest_attendance["name"]} has the lowest attendance ({lowest_attendance["percentage"]}%)'
            elif "below 75" in question:
                names = [f'{s["name"]} ({s["percentage"]}%)' for s in low_attendance]
                response = ", ".join(names)
            elif "improved" in question or "most improved" in question:
                if len(student_data) >= 2:
                    sorted_by_percentage = sorted(student_data, key=lambda x: x["percentage"], reverse=True)
                    response = f'{sorted_by_percentage[0]["name"]} has the best attendance ({sorted_by_percentage[0]["percentage"]}%)'
                else:
                    response = "Need more student data to determine improvement."
            elif "average" in question:
                avg = round(sum(s["percentage"] for s in student_data) / len(student_data), 2) if student_data else 0
                response = f"The average attendance is {avg}%"
            elif "trend" in question or "pattern" in question:
                response = ask_ai(f"""
                Analyze attendance trends for: {student_data}
                What patterns do you see?
                """)
            else:
                prompt = f"""
                You are an AI Attendance Assistant.

                Student Data: {student_data}
                User Question: {question}

                Answer professionally.
                """
                response = ask_ai(prompt)

        elif "student_search" in request.form:
            search_name = request.form["student_search"].strip().lower()
            for student in student_data:
                if search_name in student["name"].lower():
                    search_result = student
                    break
            if search_result is None:
                search_message = "Student not found."

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_settings WHERE id=1")
    email_settings = cursor.fetchone()
    conn.close()

    return render_template(
        "index.html",
        students=student_data,
        low_attendance=low_attendance,
        response=response,
        chat_history=chat_history,
        total_students=total_students,
        highest_attendance=highest_attendance,
        lowest_attendance=lowest_attendance,
        search_result=search_result,
        ai_report=ai_report,
        search_message=search_message,
        delete_message=delete_message,
        update_message=update_message,
        email_settings=email_settings
    )


@app.route("/export_excel")
@login_required
def export_excel():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    student_data = []
    for student in students:
        percentage = round((student[3] / student[4]) * 100, 2)
        student_info = {
            "id": student[0],
            "name": student[1],
            "roll_no": student[2],
            "present": student[3],
            "total": student[4],
            "percentage": percentage,
            "status": "Excellent" if percentage >= 90 else "Good" if percentage >= 75 else "Warning"
        }
        student_data.append(student_info)

    df = pd.DataFrame(student_data)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        download_name="attendance_report.xlsx"
    )


@app.route("/export_pdf")
@login_required
def export_pdf():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    student_data = []
    for student in students:
        percentage = round((student[3] / student[4]) * 100, 2)
        student_info = {
            "id": student[0],
            "name": student[1],
            "roll_no": student[2],
            "present": student[3],
            "total": student[4],
            "percentage": percentage,
            "status": "Excellent" if percentage >= 90 else "Good" if percentage >= 75 else "Warning"
        }
        student_data.append(student_info)

    total_students = len(student_data)
    highest = max(student_data, key=lambda x: x["percentage"]) if student_data else {"name": "N/A", "percentage": 0}
    lowest = min(student_data, key=lambda x: x["percentage"]) if student_data else {"name": "N/A", "percentage": 0}

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "AI Attendance Report")
    c.setFont("Helvetica", 12)
    y = 700
    c.drawString(100, y, f"Total Students: {total_students}")
    y -= 20
    c.drawString(100, y, f"Highest Attendance: {highest['name']} - {highest['percentage']}%")
    y -= 20
    c.drawString(100, y, f"Lowest Attendance: {lowest['name']} - {lowest['percentage']}%")
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Student Details:")
    y -= 25
    c.setFont("Helvetica", 12)
    for student in student_data:
        c.drawString(100, y, f"{student['name']} - {student['percentage']}% ({student['status']})")
        y -= 18
    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        download_name="attendance_report.pdf"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user = User(user_data[0], user_data[1])
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)
