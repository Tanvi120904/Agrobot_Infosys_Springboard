# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify # [cite: 223, 499]
from flask_sqlalchemy import SQLAlchemy # ORM for database [cite: 235, 500]
from flask_bcrypt import Bcrypt # For password hashing [cite: 236, 501]
from chatbot_model import get_response
 # Import the chatbot function [cite: 237, 502]
from flask import make_response

# Flask app setup
app = Flask(__name__) # [cite: 505]
app.secret_key = "secret123" # Used for session/flash security; MUST be strong in production [cite: 241, 506]

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Database setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # [cite: 246, 508]
db = SQLAlchemy(app) # [cite: 247, 509]
bcrypt = Bcrypt(app) # [cite: 248, 510]

# User Database Model [cite: 252, 511]
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Unique ID [cite: 254, 513]
    username = db.Column(db.String(150), nullable=False, unique=True) # Must be unique [cite: 255, 514]
    password = db.Column(db.String(150), nullable=False) # Stores hashed password [cite: 256, 515]

# Create database and tables if they don't exist [cite: 261, 516]
with app.app_context():
    db.create_all() # [cite: 262, 518]

# ----------- ROUTES -----------

# 1. Home (Chatbot Page) - Requires Login [cite: 264, 520]
@app.route("/")
def home():
    if "user_id" not in session: # Check if user is logged in [cite: 267, 523]
        return redirect(url_for("login")) # Redirect to login if not [cite: 268, 524]
    return render_template("index.html") # Show the chatbot interface [cite: 269, 525]

# 2. Registration / Signup [cite: 273, 527]
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST": # Handling form submission [cite: 276, 529]
        username = request.form.get("username") # [cite: 277, 530]
        password = request.form.get("password") # [cite: 278, 531]

        # Check for existing user [cite: 281, 533]
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Try another.", "error") # [cite: 535]
            return redirect(url_for("register"))

        # Hash password securely [cite: 283, 538]
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Save new user to DB [cite: 285, 540]
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit() # [cite: 287, 542]

        flash("Account created successfully! Please login.", "success") # [cite: 543]
        return redirect(url_for("login")) # Redirect after successful registration [cite: 288, 544]

    return render_template("register.html") # Show the registration form (GET request) [cite: 545]

# 3. Login [cite: 289, 547]
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST": # Handling form submission [cite: 292, 549]
        username = request.form.get("username") # [cite: 293, 550]
        password = request.form.get("password") # [cite: 294, 551]

        user = User.query.filter_by(username=username).first() # Fetch user from DB [cite: 295, 552]

        # Check if user exists AND password is correct [cite: 296, 553]
        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id # Store user info in session [cite: 297, 554]
            session["username"] = user.username # [cite: 298, 555]
            flash("Login successful!", "success") # [cite: 299, 556]
            return redirect(url_for("home")) # Redirect to chatbot page [cite: 300, 557]
        else:
            flash("Invalid username or password", "error") # [cite: 302, 559]
            return redirect(url_for("login")) # Redirect back to login [cite: 303, 560]

    return render_template("login.html") # Show the login form (GET request) [cite: 304, 561]

# 4. Logout [cite: 308, 563]
@app.route("/logout")
def logout():
    session.clear() # Clears all session data (logs user out) [cite: 311, 565]
    flash("You have been logged out.", "info") # [cite: 312, 566]
    return redirect(url_for("login")) # [cite: 313, 567]

# 5. Chatbot API Endpoint [cite: 316, 569]
@app.route("/get", methods=["POST"])
def chatbot_response():
    if "user_id" not in session: # Security check: Must be logged in to chat [cite: 319, 571]
        return jsonify({"response": "Please log in to chat with me!"}) # [cite: 320, 572]

    user_message = request.json["message"] # Get message from AJAX POST request [cite: 321, 573]
    bot_reply = get_response(user_message) # Get the reply from the chatbot logic [cite: 322, 574]

    return jsonify({"response": bot_reply}) # Send reply back to frontend as JSON [cite: 323, 575]

# Run app
if __name__ == "__main__": # [cite: 328, 577]
    app.run(debug=True) # Starts the development server [cite: 329, 578]