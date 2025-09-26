from flask import Flask, render_template, request, redirect, url_for, flash, session 
import mysql.connector
import random
import smtplib
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"

# DB Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="7556",
        database="littlelearners"
    )

SENDER_EMAIL = "learnerslittle14@gmail.com"
SENDER_PASSWORD = "qqdysslwnuqtxfgw"

# Initialize DB
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fullname VARCHAR(100),
            email VARCHAR(100),
            username VARCHAR(100) UNIQUE,
            password VARCHAR(100)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# Helper: get user by email (returns dict)
def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Helper: update password by email
def update_password(email, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
    conn.commit()
    cursor.close()
    conn.close()
def send_email(to_email, otp):
    subject = "Little Learners - Password Reset OTP"
    body = f"Hello! Your OTP for resetting your password is: {otp}"

    msg = MIMEText(body, "plain")
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    server.quit()    

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("f1.html", title="Loginat", message="Welcome back! Please login 🌟")

# GET login page
@app.route("/login")
def log():
    return render_template("login1.html", title="Login", message="Welcome back! Please login 🌟")

# Simple admin dashboard (safe fallback)
@app.route("/admin")
def admin_dashboard():
    return "<h2>Admin Dashboard</h2><a href='/'>Back</a>"

@app.route("/register-page")
def show_register():
    return render_template("register.html", title="Register", message="Join us and start learning 🚀")

# Other content pages (kept as-is)
@app.route('/therhy')
def riddle():
    return render_template('therhy.html')

@app.route('/7years')
def years():
    return render_template('7years.html')

@app.route('/4years')
def years4():
    return render_template('indexx.html')

@app.route('/5years')
def years5():
    return render_template('5years.html')

@app.route('/8years')
def yearsof8():
    return render_template('8year.html')

@app.route('/6years')
def years6():
    return render_template('6years.html')

@app.route('/7q')
def quiz7():
    return render_template('7Quiz.html')

@app.route('/Riddle')
def Riddle():
    return render_template('Riddle.html')

@app.route('/7p')
def puz():
    return render_template('7puzzle.html')
@app.route('/8p')
def puz8():
    return render_template('8quiz.html.html')
@app.route('/8r')
def puz82():
    return render_template('riddle 8.html')
@app.route('/6p')
def puz6():
    return render_template('1.html')
@app.route('/6r')
def rid6():
    return render_template('Riddleof6.html')
@app.route('/6b')
def blanks():
    return render_template('Blanks.html')
@app.route('/5A')
def animal():
    return render_template('animals.html')
@app.route('/home')
def ret():
    return render_template('inavtar.html')


# Register (POST)
@app.route("/register", methods=["POST"])
def register():
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (fullname, email, username, password) VALUES (%s, %s, %s, %s)",
        (fullname, email, username, password)
    )
    conn.commit()
    cursor.close()
    conn.close()
    # Redirect to GET login page
    return redirect(url_for("log"))

# Login (POST)
@app.route("/login", methods=["GET", "POST"])
def login():
    # 🔹 If user already logged in → redirect to dashboard directly
    if "username" in session:
        if session["username"] == "admin":
            return redirect(url_for("admin_dashboard"))
        return render_template("inavtar.html", title="inavtar", message="Welcome back 🚀")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["username"] = username
            if username == "admin":
                return redirect(url_for("admin_dashboard"))
            
            return render_template("inavtar.html", title="inavtar", message="Join us and start learning 🚀")
        else:
            return "❌ Please Register your data! <a href='/'>try again</a>"

    # If GET request → show login form
    return render_template("login.html")

# Show all users (for debugging only)
@app.route("/users")
def all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT fullname, email, username, password FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    result = "<h2>🌍 All Registered Users</h2><ul>"
    for u in users:
        result += f"<li>{u['fullname']} | {u['email']} | {u['username']} | {u['password']}</li>"
    result += "</ul><a href='/'>Back to Login</a>"
    return result

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


# Forgot Password (OTP)
@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = get_user_by_email(email)

        if user:
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp
            session["email"] = email

            # Send OTP Email
            try:
                msg = MIMEMultipart()
                msg["From"] = SENDER_EMAIL
                msg["To"] = email
                msg["Subject"] = "Your OTP Code"
                body = f"Your OTP for password reset is: {otp}"
                msg.attach(MIMEText(body, "plain"))

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, msg.as_string())
                server.quit()
                send_email(email, otp)

                flash("OTP sent to your email!", "info")
                return redirect(url_for("verify_otp"))
            except Exception as e:
                flash(f"Error sending email: {e}", "danger")
        else:
            flash("enter valid email!", "danger")

    return render_template("forgot.html")


# Verify OTP
@app.route("/verify", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form["otp"]

        if entered_otp == session.get("otp"):
            flash("OTP Verified! Set new password.", "success")
            return redirect(url_for("reset_password"))
        else:
            flash("Invalid OTP!", "danger")

    return render_template("verify.html")


# Reset Password
@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form["password"]
        email = session.get("email")

        if email:
            update_password(email, new_password)
            flash("Password reset successfully!", "success")
            return redirect(url_for("log"))

    return render_template("reset.html")

# Re-login using email (POST)
@app.route("/relogin", methods=["GET", "POST"])
def relogin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)
        if user and user.get('password') == password:
            return "Login Successful!"
        else:
            flash("Invalid login!", "danger")

    return render_template("relogin.html")


if __name__ == "__main__":
    app.run(debug=True)
