"""Application routes."""

from datetime import datetime

from flask import Blueprint, current_app, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.export import generate_csv_content, get_export_filename
from app.milestones import get_all_milestones
from app.models import Category, User, Word
from app.utils import (
    calculate_age_months,
    check_duplicate_word,
    check_duplicate_word_excluding,
    get_milestone_for_age,
    get_monthly_stats,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """Display the main dashboard."""
    word_count = Word.query.count()
    categories = Category.query.all()
    recent_words = Word.query.order_by(Word.date_added.desc()).limit(5).all()
    return render_template(
        "index.html",
        word_count=word_count,
        categories=categories,
        recent_words=recent_words,
    )


@main_bp.route("/words")
@login_required
def word_list():
    """Display the word list with sorting and filtering."""
    # Get query parameters
    sort = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    category_id = request.args.get("category", type=int)
    user_id = request.args.get("user", type=int)

    # Build query with filters
    query = Word.query

    if category_id:
        query = query.filter_by(category_id=category_id)
    if user_id:
        query = query.filter_by(user_id=user_id)

    # Apply sorting
    if sort == "word":
        order_col = Word.word.asc() if order == "asc" else Word.word.desc()
    else:  # date
        order_col = Word.date_added.asc() if order == "asc" else Word.date_added.desc()

    words = query.order_by(order_col).all()
    categories = Category.query.all()
    users = User.query.all()

    return render_template(
        "words.html",
        words=words,
        categories=categories,
        users=users,
        current_sort=sort,
        current_order=order,
        current_category=category_id,
        current_user_filter=user_id,
    )


@main_bp.route("/stats")
@login_required
def stats():
    """Display statistics and developmental milestones."""
    total_words = Word.query.count()

    # Get baby's age from config
    birthdate_str = current_app.config.get("BABY_BIRTHDATE")
    age_months = None
    current_milestone = None

    if birthdate_str:
        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
            age_months = calculate_age_months(birthdate)
            current_milestone = get_milestone_for_age(age_months)
        except ValueError:
            # Invalid date format, skip age calculation
            pass

    # Get all milestones for display
    milestones = get_all_milestones()

    # Get monthly stats
    monthly_stats = get_monthly_stats()

    return render_template(
        "stats.html",
        total_words=total_words,
        age_months=age_months,
        current_milestone=current_milestone,
        milestones=milestones,
        monthly_stats=monthly_stats,
    )


@main_bp.route("/export")
@login_required
def export_csv():
    """Export all words as CSV file."""
    # Get all words sorted by date (oldest first)
    words = Word.query.order_by(Word.date_added.asc()).all()

    csv_content = generate_csv_content(words)

    response = make_response(csv_content)
    response.headers["Content-Disposition"] = f"attachment; filename={get_export_filename()}"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response


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


@main_bp.route("/words/<int:word_id>/edit", methods=["GET", "POST"])
@login_required
def edit_word(word_id):
    """Edit a word."""
    word = Word.query.get_or_404(word_id)
    categories = Category.query.all()

    if request.method == "POST":
        word_text = request.form.get("word", "").strip()

        if not word_text:
            flash("Please enter a word.", "error")
            return render_template("edit_word.html", word=word, categories=categories)

        # Check for duplicates (excluding current word)
        existing = check_duplicate_word_excluding(word_text, word_id)
        if existing:
            flash(f'"{existing.word}" already exists.', "error")
            return render_template("edit_word.html", word=word, categories=categories)

        # Get optional category
        category_id = request.form.get("category_id")
        if category_id:
            category_id = int(category_id)
        else:
            category_id = None

        # Update the word
        word.word = word_text
        word.category_id = category_id
        db.session.commit()

        flash(f'Updated "{word_text}" successfully!', "success")
        return redirect(url_for("main.word_list"))

    # GET request - display edit form
    return render_template("edit_word.html", word=word, categories=categories)


@main_bp.route("/words/<int:word_id>/delete", methods=["POST"])
@login_required
def delete_word(word_id):
    """Delete a word."""
    word = Word.query.get_or_404(word_id)
    word_text = word.word

    db.session.delete(word)
    db.session.commit()

    flash(f'Deleted "{word_text}" from vocabulary.', "success")
    return redirect(url_for("main.word_list"))


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
