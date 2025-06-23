from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import re

app = Flask(__name__)
app.secret_key = "kibra123"

# ------------------ Mail Configuration ------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kimanianthony002@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'  # Replace with your Gmail App Password
mail = Mail(app)

# ------------------ File Paths ------------------
GIGS_FILE = os.path.join("data", "gigs.json")
USERS_FILE = os.path.join("data", "users.json")

# ------------------ Utilities ------------------
def is_valid_password(password):
    return len(password) >= 6 and bool(re.search(r'\d', password)) and bool(re.search(r'[a-zA-Z]', password))

def load_gigs():
    if not os.path.exists(GIGS_FILE):
        return []
    with open(GIGS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_gig(gig):
    gigs = load_gigs()
    gigs.append(gig)
    os.makedirs(os.path.dirname(GIGS_FILE), exist_ok=True)
    with open(GIGS_FILE, "w") as f:
        json.dump(gigs, f, indent=2)

def save_gig_data(gigs):
    os.makedirs(os.path.dirname(GIGS_FILE), exist_ok=True)
    with open(GIGS_FILE, "w") as f:
        json.dump(gigs, f, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ------------------ Routes ------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/how-it-works")
def how_it_works():
    return render_template("how-it-works.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        try:
            msg = Message(subject=f"New Contact Message from {name}",
                          sender='kimanianthony002@gmail.com',
                          recipients=['kimanianthony002@gmail.com'],
                          body=f"Name: {name}\nEmail: {email}\nMessage: {message}")
            mail.send(msg)
            flash("Your message has been sent!", "success")
        except Exception as e:
            flash("Failed to send message. Please try again later.", "error")

    return render_template("contact-us.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

@app.route("/gigs", methods=["GET", "POST"])
def gigs():
    if "user_email" not in session:
        flash("Please log in to view gigs.", "error")
        return redirect(url_for("auth"))

    if request.method == "POST":
        title = request.form["title"]
        gig_type = request.form["type"]
        date = request.form["date"]
        details = request.form["details"]

        new_gig = {
            "title": title,
            "type": gig_type,
            "date": date,
            "details": details
        }

        save_gig(new_gig)
        flash("Gig submitted successfully!", "success")
        return redirect(url_for("gigs"))

    gigs_data = load_gigs()
    return render_template("gigs.html", gigs=gigs_data)

@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        action = request.form.get("action")

        users = load_users()
        user = next((u for u in users if u["email"] == email), None)

        if action == "login":
            if not user or not check_password_hash(user["password"], password):
                flash("Invalid email or password", "error")
                return redirect(url_for("auth"))

            session["user_email"] = user["email"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("gigs"))

        elif action == "signup":
            if user:
                flash("Email already exists.", "error")
                return redirect(url_for("auth"))

            if not is_valid_password(password):
                flash("Password must be at least 6 characters long and include letters and numbers.", "error")
                return redirect(url_for("auth"))

            hashed_password = generate_password_hash(password)
            new_user = {"email": email, "password": hashed_password}
            users.append(new_user)
            save_users(users)
            session["user_email"] = email
            flash("Account created successfully!", "success")
            return redirect(url_for("gigs"))

        else:
            flash("Invalid action.", "error")

    return render_template("auth.html")

@app.route("/reset-password", methods=["POST"])
def reset_password():
    email = request.form.get("email")

    if not email:
        flash("Please enter your email address.", "error")
        return redirect(url_for("auth"))

    users = load_users()
    user_found = next((u for u in users if u["email"] == email), None)

    if not user_found:
        flash("No account found with that email.", "error")
        return redirect(url_for("auth"))

    # This would normally include sending an email with a token
    flash("A password reset link has been sent to your email (mocked).", "success")
    return redirect(url_for("auth"))

# ------------------ Run ------------------
if __name__ == "__main__":
    app.run(debug=True)
