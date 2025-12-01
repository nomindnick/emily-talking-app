# Emily Word Tracker

A simple web application for tracking a baby's vocabulary development. Two parents can log words their baby says, view statistics on language development, and export data for sharing with a pediatrician.

## Features

- **Word Logging** - Quickly add new words with automatic timestamps
- **Duplicate Detection** - Case-insensitive duplicate checking prevents double entries
- **Word Categories** - Organize words by type (Noun, Verb, Animal Sound, Person, Other)
- **Statistics Dashboard** - Track total words and growth over time
- **Milestone Comparison** - Compare vocabulary against CDC developmental milestones
- **CSV Export** - Download all data for backup or sharing with healthcare providers
- **Mobile-First Design** - Optimized for adding words on your phone

## Tech Stack

- **Backend:** Python/Flask
- **Database:** PostgreSQL (Railway) / SQLite (local dev)
- **ORM:** SQLAlchemy with Flask-Migrate
- **Frontend:** HTML/CSS with Jinja2 templates
- **Deployment:** Railway (auto-deploy from GitHub)

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for database backup/restore scripts)

### Local Development

```bash
# Clone the repository
git clone https://github.com/nomindnick/emily-talking-app.git
cd emily-talking-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

The app will be available at `http://localhost:5000`

### Default Development Credentials

- **Username:** nick or wife
- **Password:** devpassword

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# User passwords
NICK_PASSWORD=your-password
WIFE_PASSWORD=partner-password

# Baby info (for milestone calculations)
BABY_BIRTHDATE=2024-01-15
WIFE_DISPLAY_NAME=Partner
```

See `.env.example` for all available options.

## Usage

### Adding Words

1. Log in with your account
2. Type the word in the input field on the dashboard
3. Optionally select a category
4. Click "Add Word"

The app automatically:
- Records who added the word
- Timestamps when it was added
- Checks for duplicates (case-insensitive)

### Viewing Statistics

The Stats page shows:
- Total word count
- Baby's current age (if birthdate configured)
- Comparison against CDC developmental milestones
- Words added by month

### Exporting Data

Click "Export CSV" on the Stats or Word List page to download all words with:
- Word text
- Date added
- Who added it
- Category

### Managing Words

From the Word List page you can:
- Sort by word (A-Z) or date
- Filter by category or user
- Edit word text or category
- Delete words (with confirmation)

## Deployment

### Railway Setup

1. Create a [Railway](https://railway.app) account
2. Create new project → Deploy from GitHub
3. Add PostgreSQL database
4. Configure environment variables:
   - `SECRET_KEY` (generate: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FLASK_ENV=production`
   - `NICK_PASSWORD`
   - `WIFE_PASSWORD`
   - `BABY_BIRTHDATE`
   - `WIFE_DISPLAY_NAME`

5. Set pre-deploy command: `flask db upgrade`
6. Deploy!

### Database Backups

```bash
# Create a backup
./scripts/backup_db.sh

# Restore from backup (use with caution!)
./scripts/restore_db.sh backups/emily_words_YYYYMMDD_HHMMSS.sql
```

Requires Docker and Railway PostgreSQL credentials in `.env`.

## Development

### Running Tests

```bash
pytest -v              # All tests
pytest -x              # Stop on first failure
pytest --cov=app       # With coverage report
```

### Database Migrations

```bash
# After modifying models.py
flask db migrate -m "Description of change"

# Apply migrations locally
flask db upgrade

# Migrations auto-apply on Railway deploy
```

### Project Structure

```
emily-talking-app/
├── app/
│   ├── __init__.py      # App factory
│   ├── models.py        # Database models
│   ├── routes.py        # URL routes
│   ├── auth.py          # Authentication
│   ├── utils.py         # Helper functions
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS
├── migrations/          # Database migrations
├── tests/               # Test suite
├── scripts/             # Backup/restore scripts
├── config.py            # Configuration
└── run.py               # Entry point
```

## Developmental Milestones

The app compares your baby's vocabulary against CDC guidelines:

| Age | Typical Vocabulary |
|-----|-------------------|
| 12 months | 1-3 words |
| 15 months | 3-10 words |
| 18 months | 10-50 words |
| 24 months | 50-100+ words |
| 30 months | 200+ words |
| 36 months | 450+ words |

## License

MIT License - feel free to use and modify for your own family!

## Acknowledgments

- CDC and American Academy of Pediatrics for developmental milestone data
- Built with Flask, SQLAlchemy, and Railway
