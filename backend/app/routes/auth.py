from flask import Blueprint, request, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.user import User
from app.utils.sanitizer import sanitize_text

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return {
            "message": "Username, email and password are required."
        }, 400

    clean_username = sanitize_text(username)
    clean_email = sanitize_text(email)

    existing_user = User.query.filter_by(email=clean_email).first()
    if existing_user:
        return {
            "message": "Email already registered."
        }, 409

    password_hash = generate_password_hash(password)

    new_user = User(
        username=clean_username,
        email=clean_email,
        password_hash=password_hash
    )
    db.session.add(new_user)
    db.session.commit()

    return {
        "message": "User registered successfully!"
    }, 201

@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {
            "message": "Email and password are required."
        }, 400

    clean_email = sanitize_text(email)

    user = User.query.filter_by(email=clean_email).first()
    if user is None:
        return {
            "message": "Invalid email or password."
        }, 401

    if not check_password_hash(user.password_hash, password):
        return {
            "message": "Invalid email or password."
        }, 401

    session["user_id"] = user.id
    session["username"] = user.username

    return {
        "message": "Login successful!",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }, 200

@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return {
        "message": "Logged out successfully!"
    }, 200

@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "logged_in": False
        }

    user = db.session.get(User, user_id)
    if user is None:
        session.clear()
        return {
            "logged_in": False
        }

    return {
        "logged_in": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }
