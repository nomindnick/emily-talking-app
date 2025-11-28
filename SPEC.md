# Emily Word Tracker - Specification

## Overview

A simple web application for tracking a baby's vocabulary development. Two users (parents) can log words their baby says, view statistics on language development, and export data for backup or sharing with a pediatrician.

## Tech Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL (hosted on Railway)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Frontend**: HTML/CSS with Jinja2 templates, minimal JavaScript
- **Charts**: Chart.js (future enhancement)
- **Deployment**: Railway (auto-deploy from GitHub)

## Authentication

Hardcoded two-user system (no registration). Users are "Nick" and "[Wife's Name]" with simple password authentication using Flask sessions. Passwords stored as hashed values.

## Core Features

### Word Management
- Add new words with automatic timestamp
- Duplicate detection (case-insensitive) before adding
- Edit existing words (word text and category)
- Delete words with confirmation
- Each word tracks: word text, date added, who added it, category (optional)

### Data Views
- Total word count
- Full word list (sortable/filterable)
- Words grouped by month added
- Words by category (when implemented)
- Words by user who added them

### Analytics (MVP)
- Total words vs. developmental milestones (CDC-based reference points)
- Words added per month (table view initially, charts later)

### Data Export
- Download all words as CSV
- CSV includes: word, date added, added by, category

## Database Schema

### Users Table
| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary key |
| username | String(50) | Unique |
| password_hash | String(256) | Bcrypt hash |
| display_name | String(100) | For UI display |

### Words Table
| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary key |
| word | String(100) | The word itself |
| date_added | DateTime | When word was recorded |
| user_id | Integer | Foreign key to Users |
| category_id | Integer | Foreign key to Categories (nullable) |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last edit timestamp |

### Categories Table (for future use)
| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary key |
| name | String(50) | Category name |
| description | String(200) | Optional description |

## Developmental Milestones Reference

Based on CDC and American Academy of Pediatrics guidelines:

| Age | Typical Vocabulary |
|-----|-------------------|
| 12 months | 1-3 words |
| 15 months | 3-10 words |
| 18 months | 10-50 words |
| 24 months | 50-100+ words |
| 30 months | 200+ words |
| 36 months | 450+ words |

Display baby's actual count against these benchmarks based on baby's birthdate.

## Configuration

Environment variables (set in Railway):
- `DATABASE_URL` - PostgreSQL connection string (provided by Railway)
- `SECRET_KEY` - Flask session secret
- `NICK_PASSWORD` - Hashed password for Nick
- `WIFE_PASSWORD` - Hashed password for wife account
- `BABY_BIRTHDATE` - For milestone calculations (format: YYYY-MM-DD)

## UI/UX Guidelines

- **Mobile-first design** (primary use case is adding words on phones)
- Minimum touch target size: 44x44px
- Responsive layout that works on phones, tablets, and desktop
- Simple, clean interface
- Quick word entry as primary action (minimal taps to add a word)
- Confirmation dialogs for destructive actions (delete)
- Flash messages for success/error feedback

## Architecture Guidelines

- **Modularity is critical** - this app will be actively modified and extended
- Keep templates modular: use Jinja2 template inheritance and partials
- Keep CSS organized: consider separate files for layout, components, utilities
- Keep routes organized: group related routes, consider blueprints if app grows
- Keep business logic out of routes: use helper functions in separate modules
- Database models should be self-contained with clear method interfaces

## Testing Requirements

- Every feature must have corresponding tests
- Use pytest as the test framework
- Test categories:
  - Unit tests for models and utility functions
  - Integration tests for routes (using Flask test client)
  - Database tests should use a separate test database or transactions
- Tests must pass before any sprint is considered complete

## Future Enhancements (Post-MVP)

- Chart visualizations (words over time, by category)
- Word categorization UI
- Notes field for words (context, pronunciation, etc.)
- Photo/video attachment for words
- Multiple children support
