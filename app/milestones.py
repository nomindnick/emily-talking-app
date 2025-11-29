"""CDC-based developmental milestones for vocabulary tracking."""

# Based on CDC and American Academy of Pediatrics guidelines
MILESTONES = [
    {"age_months": 12, "min_words": 1, "max_words": 3, "label": "12 months"},
    {"age_months": 15, "min_words": 3, "max_words": 10, "label": "15 months"},
    {"age_months": 18, "min_words": 10, "max_words": 50, "label": "18 months"},
    {"age_months": 24, "min_words": 50, "max_words": 100, "label": "24 months"},
    {"age_months": 30, "min_words": 200, "max_words": None, "label": "30 months"},
    {"age_months": 36, "min_words": 450, "max_words": None, "label": "36 months"},
]


def get_all_milestones():
    """Return all developmental milestones.

    Returns:
        List of milestone dictionaries with age_months, min_words, max_words, label.
    """
    return MILESTONES


def get_milestone_for_age(months):
    """Get the appropriate milestone for a given age in months.

    Finds the milestone range that applies to the given age. Returns the
    milestone where the child's age is at or past that milestone but before
    the next one.

    Args:
        months: Age in months (integer).

    Returns:
        Milestone dictionary or None if age is below first milestone.
    """
    if months is None or months < 12:
        return None

    applicable_milestone = None
    for milestone in MILESTONES:
        if months >= milestone["age_months"]:
            applicable_milestone = milestone
        else:
            break

    return applicable_milestone
