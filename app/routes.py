"""Application routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.models import User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """Display the main dashboard."""
    return render_template("base.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please select a user and enter a password.", "error")
            return redirect(url_for("main.login"))

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("main.login"))

        login_user(user)
        flash(f"Welcome back, {user.display_name}!", "success")

        # Redirect to requested page or index
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("main.index"))

    # GET request - display login form
    users = User.query.all()
    return render_template("login.html", users=users)


@main_bp.route("/logout")
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))
