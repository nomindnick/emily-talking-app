"""Application routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import Category, User, Word
from app.utils import check_duplicate_word

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """Display the main dashboard."""
    word_count = Word.query.count()
    categories = Category.query.all()
    return render_template("index.html", word_count=word_count, categories=categories)


@main_bp.route("/words/add", methods=["POST"])
@login_required
def add_word():
    """Handle adding a new word."""
    word_text = request.form.get("word", "").strip()

    if not word_text:
        flash("Please enter a word.", "error")
        return redirect(url_for("main.index"))

    # Check for duplicates (case-insensitive)
    existing = check_duplicate_word(word_text)
    if existing:
        flash(f'"{existing.word}" has already been added.', "error")
        return redirect(url_for("main.index"))

    # Get optional category
    category_id = request.form.get("category_id")
    if category_id:
        category_id = int(category_id)
    else:
        category_id = None

    # Create the new word
    word = Word(
        word=word_text,
        user_id=current_user.id,
        category_id=category_id
    )
    db.session.add(word)
    db.session.commit()

    flash(f'Added "{word_text}" to Emily\'s vocabulary!', "success")
    return redirect(url_for("main.index"))


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
