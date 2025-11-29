"""CSV export functionality for word data."""

import csv
import io
from datetime import date


def generate_csv_content(words):
    """Generate CSV string from Word objects with UTF-8 BOM for Excel compatibility.

    Args:
        words: List of Word model instances to export.

    Returns:
        String containing CSV data with headers and all word rows.
    """
    output = io.StringIO()
    # Add UTF-8 BOM for Excel compatibility
    output.write('\ufeff')

    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    # Headers
    writer.writerow(['Word', 'Date Added', 'Added By', 'Category'])

    # Data rows
    for word in words:
        writer.writerow([
            word.word,
            word.date_added.strftime('%Y-%m-%d') if word.date_added else '',
            word.user.display_name if word.user else '',
            word.category.name if word.category else ''
        ])

    return output.getvalue()


def get_export_filename():
    """Generate filename with current date.

    Returns:
        String filename in format: emily_words_YYYY-MM-DD.csv
    """
    return f"emily_words_{date.today().strftime('%Y-%m-%d')}.csv"
