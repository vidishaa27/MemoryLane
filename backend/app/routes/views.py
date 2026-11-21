from flask import Blueprint, render_template, session, redirect

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def home():
    return render_template("index.html")

@views_bp.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("dashboard.html")

@views_bp.route("/create-magazine")
def create_magazine_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("create-magazine.html")

@views_bp.route("/create-page")
def create_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("create-page.html")

@views_bp.route("/magazine")
def magazine():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("magazine.html")
