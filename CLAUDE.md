# Claude Code Guidelines for Emily Word Tracker

## Project Overview

This is a Flask web application for tracking a baby's vocabulary development, deployed on Railway with PostgreSQL.

## Database Safety Guidelines

### Before Making Database Changes

**Always backup the database before:**
- Modifying `app/models.py` (adding/removing/changing columns or tables)
- Running any migration commands
- Performing bulk data operations
- Any changes that could potentially affect data integrity

**To backup:**
```bash
./scripts/backup_db.sh
```

Backups are stored in `backups/` (gitignored) and the script keeps the last 10 automatically.

### Making Schema Changes

This project uses Flask-Migrate (Alembic) for database migrations. **Never modify the database schema directly.**

**Workflow for schema changes:**

1. **Backup first:**
   ```bash
   ./scripts/backup_db.sh
   ```

2. **Modify the models** in `app/models.py`

3. **Generate a migration:**
   ```bash
   flask db migrate -m "Description of change"
   ```

4. **Review the generated migration** in `migrations/versions/` - ensure it does what you expect

5. **Test locally:**
   ```bash
   flask db upgrade
   ```

6. **Run tests:**
   ```bash
   pytest -v
   ```

7. **Commit and push** - Railway will auto-run `flask db upgrade` on deploy

### Restoring from Backup

If something goes wrong:
```bash
./scripts/restore_db.sh backups/emily_words_YYYYMMDD_HHMMSS.sql
```

This requires confirmation and will overwrite all production data.

## Development Setup

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally (uses SQLite by default)
python run.py
```

### Environment Variables

Copy `.env.example` to `.env` and fill in values. Key variables:
- `FLASK_ENV` - development/production
- `SECRET_KEY` - session secret (required in production)
- `DATABASE_URL` - PostgreSQL connection string
- `NICK_PASSWORD` / `WIFE_PASSWORD` - user passwords
- `BABY_BIRTHDATE` - for milestone calculations
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` - for backup scripts

### Running Tests

```bash
pytest -v           # All tests
pytest -x           # Stop on first failure
pytest --cov=app    # With coverage
```

## Deployment

### Railway Configuration

- **Web service:** Auto-deploys from GitHub `main` branch
- **Database:** PostgreSQL (separate Railway service)
- **Pre-deploy command:** `flask db upgrade` (runs migrations automatically)

### Environment Variables on Railway

Set these in Railway dashboard → Variables:
- `SECRET_KEY`
- `FLASK_ENV=production`
- `NICK_PASSWORD`
- `WIFE_PASSWORD`
- `BABY_BIRTHDATE`
- `WIFE_DISPLAY_NAME`

`DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

## Project Structure

```
emily-talking-app/
├── app/
│   ├── __init__.py      # App factory, extensions
│   ├── models.py        # SQLAlchemy models (User, Word, Category)
│   ├── routes.py        # Flask routes/views
│   ├── auth.py          # Authentication logic
│   ├── utils.py         # Helper functions
│   ├── milestones.py    # Developmental milestone data
│   ├── export.py        # CSV export logic
│   ├── init_db.py       # Database seeding
│   ├── templates/       # Jinja2 templates
│   └── static/          # CSS, JS, images
├── migrations/          # Alembic migrations
├── tests/               # Pytest test suite
├── scripts/             # Utility scripts (backup/restore)
├── config.py            # Flask configuration classes
├── run.py               # Application entry point
└── requirements.txt     # Python dependencies
```

## Key Files to Know

- `app/models.py` - Database schema (User, Word, Category models)
- `config.py` - Environment-specific configuration
- `migrations/versions/` - Database migration history
- `tests/conftest.py` - Pytest fixtures

## Common Tasks

### Add a new database column

1. Backup: `./scripts/backup_db.sh`
2. Edit `app/models.py`
3. Generate migration: `flask db migrate -m "Add X column to Y table"`
4. Review migration file
5. Test: `flask db upgrade && pytest -v`
6. Commit and push

### Add a new feature

1. Write tests first (in `tests/`)
2. Implement the feature
3. Run `pytest -v` to verify
4. Test manually at mobile viewport (375px)
5. Commit and push

### Debug production issues

1. Check Railway logs in dashboard
2. Run backup before any fixes: `./scripts/backup_db.sh`
3. Test fixes locally first
