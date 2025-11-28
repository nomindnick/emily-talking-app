# Emily Word Tracker - Implementation Plan

## Instructions for Claude Code

This document breaks the project into focused sprints. **Complete one sprint at a time.** Each sprint should take roughly 1-2 hours and results in testable functionality.

### Sprint Completion Requirements
1. Complete all tasks listed
2. **Write all specified tests**
3. **Run `pytest -v` and verify ALL tests pass**
4. Check off all items in "Deliverables"
5. Verify "Definition of Done" criteria are met
6. Only then move to the next sprint

### Critical Rules
- **Never mark a sprint complete without passing tests**
- Keep code modular - this app will be heavily modified
- Mobile-first: test at 375px viewport width
- No hardcoded secrets - use environment variables

Reference `SPEC.md` for detailed requirements and schema definitions.

---

## Sprint 0: Project Setup
**Goal**: Initialize project structure and dependencies

### Tasks
1. Create project directory structure:
   ```
   emily-word-tracker/
   ├── app/
   │   ├── __init__.py
   │   ├── models.py
   │   ├── routes.py
   │   ├── auth.py
   │   └── templates/
   │       └── base.html
   ├── tests/
   │   ├── __init__.py
   │   ├── conftest.py
   │   └── test_app.py
   ├── config.py
   ├── requirements.txt
   ├── .env.example
   ├── .gitignore
   └── run.py
   ```

2. Create `requirements.txt` with:
   - Flask
   - Flask-SQLAlchemy
   - Flask-Login
   - psycopg2-binary
   - python-dotenv
   - bcrypt
   - gunicorn
   - pytest
   - pytest-flask

3. Create `config.py` with:
   - Development and production config classes
   - Testing config class (uses SQLite in-memory for fast tests)
   - DATABASE_URL handling (parse Railway's PostgreSQL URL)
   - SECRET_KEY from environment

4. Create basic Flask app factory in `app/__init__.py`

5. Create `run.py` entry point

6. Create `.gitignore` (Python defaults, .env, __pycache__, etc.)

7. Create `.env.example` showing required environment variables (this documents what to set in Railway)

8. Create `tests/conftest.py` with pytest fixtures for app and test client

### Deliverables
- [ ] All files in directory structure exist
- [ ] `pip install -r requirements.txt` succeeds
- [ ] App runs with `python run.py` without errors
- [ ] Root route returns 200 status

### Tests to Write and Pass
```python
# tests/test_app.py
def test_app_exists(app):
    """App factory creates app instance"""
    assert app is not None

def test_app_runs(client):
    """App responds to requests"""
    response = client.get('/')
    assert response.status_code == 200
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing (`pytest` returns 0 failures)
- [ ] Code runs without errors or warnings

---

## Sprint 1: Database Models
**Goal**: Define all database models with proper relationships

### Tasks
1. In `app/models.py`, create SQLAlchemy models:
   - User model (id, username, password_hash, display_name)
   - Category model (id, name, description)
   - Word model (id, word, date_added, user_id, category_id, created_at, updated_at)

2. Set up proper foreign key relationships:
   - Word.user_id → User.id
   - Word.category_id → Category.id (nullable)

3. Add model methods:
   - User: `set_password()`, `check_password()` using bcrypt
   - Word: `to_dict()` for easy serialization

4. Create `app/init_db.py` script that:
   - Creates all tables
   - Seeds the two user accounts (Nick, Wife)
   - Seeds default categories: "Noun", "Verb", "Animal Sound", "Person", "Other"

### Deliverables
- [ ] All three models defined in models.py
- [ ] Foreign key relationships work correctly
- [ ] Password hashing methods functional
- [ ] init_db.py creates tables and seeds data

### Tests to Write and Pass
```python
# tests/test_models.py
def test_user_password_hashing(app):
    """User password hashing and verification works"""
    user = User(username='test', display_name='Test')
    user.set_password('secret123')
    assert user.check_password('secret123') is True
    assert user.check_password('wrong') is False

def test_word_user_relationship(app, db_session):
    """Word correctly links to User"""
    user = User(username='test', display_name='Test')
    user.set_password('test')
    db_session.add(user)
    db_session.commit()
    
    word = Word(word='hello', user_id=user.id)
    db_session.add(word)
    db_session.commit()
    
    assert word.user.username == 'test'

def test_word_to_dict(app, db_session):
    """Word.to_dict() returns correct structure"""
    # Create word and verify to_dict has expected keys
    
def test_category_optional(app, db_session):
    """Word can be created without category"""
    # Verify nullable category works
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Can run init_db.py and verify data in database

---

## Sprint 2: Authentication
**Goal**: Implement login/logout with Flask-Login

### Tasks
1. In `app/auth.py`:
   - Configure Flask-Login
   - Create login_required decorator usage
   - Create `load_user` function

2. Create `app/templates/login.html`:
   - Simple form: username dropdown (Nick/Wife), password field
   - Error message display
   - Mobile-friendly styling (large touch targets, readable text)

3. In `app/routes.py`, create routes:
   - `GET /login` - display login form
   - `POST /login` - authenticate and redirect
   - `GET /logout` - clear session and redirect to login

4. Create `app/templates/base.html`:
   - Basic HTML5 structure
   - Mobile viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
   - Navigation with logout button (when logged in)
   - Flash message display area
   - Block for page content
   - Modular structure: use blocks for head, nav, content, scripts

### Deliverables
- [ ] Login page renders correctly
- [ ] Authentication validates password correctly
- [ ] Session persists across requests
- [ ] Logout clears session
- [ ] Protected routes redirect to login
- [ ] Templates use inheritance from base.html

### Tests to Write and Pass
```python
# tests/test_auth.py
def test_login_page_loads(client):
    """Login page is accessible"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'password' in response.data.lower()

def test_login_success(client, seeded_db):
    """Valid credentials log user in"""
    response = client.post('/login', data={
        'username': 'nick',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to dashboard, not show login error

def test_login_failure(client, seeded_db):
    """Invalid password rejected"""
    response = client.post('/login', data={
        'username': 'nick',
        'password': 'wrongpass'
    })
    assert b'invalid' in response.data.lower() or response.status_code == 401

def test_protected_route_redirects(client):
    """Unauthenticated user redirected to login"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_logout(authenticated_client):
    """Logout clears session"""
    response = authenticated_client.get('/logout', follow_redirects=True)
    # After logout, accessing protected route should redirect
    response = authenticated_client.get('/')
    assert response.status_code == 302
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Manual test: can log in, browse, log out in browser

---

## Sprint 3: Word Entry (Create)
**Goal**: Implement adding new words with duplicate detection

### Tasks
1. Create `app/templates/index.html` (dashboard):
   - Word entry form (prominent, top of page)
   - Large input field for word (easy to tap on mobile)
   - Optional category dropdown
   - Large submit button (min 44px height)
   - Display current total word count

2. In `app/routes.py`, create routes:
   - `GET /` - dashboard with word entry form
   - `POST /words/add` - handle new word submission

3. Implement duplicate detection in `app/utils.py`:
   - Case-insensitive check against existing words
   - Return existing word if duplicate found
   - Keep business logic separate from routes

4. On successful add:
   - Create Word record with current user and timestamp
   - Flash success message
   - Redirect back to dashboard

5. On duplicate:
   - Flash error message with the existing word shown
   - Do not add duplicate
   - Redirect back to dashboard

### Deliverables
- [ ] Dashboard displays with word entry form
- [ ] Word entry form is mobile-friendly (large inputs, touch targets)
- [ ] New words save to database with correct user_id and timestamp
- [ ] Duplicate detection prevents adding duplicates
- [ ] Duplicate check is case-insensitive
- [ ] Flash messages display for success and error

### Tests to Write and Pass
```python
# tests/test_words.py
def test_add_word_success(authenticated_client, seeded_db):
    """Can add a new word"""
    response = authenticated_client.post('/words/add', data={
        'word': 'hello'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Verify word in database
    word = Word.query.filter_by(word='hello').first()
    assert word is not None
    assert word.user_id is not None
    assert word.date_added is not None

def test_add_word_duplicate_rejected(authenticated_client, seeded_db):
    """Duplicate words are rejected"""
    # Add first word
    authenticated_client.post('/words/add', data={'word': 'hello'})
    # Try to add duplicate
    response = authenticated_client.post('/words/add', data={
        'word': 'hello'
    }, follow_redirects=True)
    # Should show error, not add second word
    assert Word.query.filter_by(word='hello').count() == 1

def test_duplicate_check_case_insensitive(authenticated_client, seeded_db):
    """Duplicate check ignores case"""
    authenticated_client.post('/words/add', data={'word': 'Hello'})
    response = authenticated_client.post('/words/add', data={
        'word': 'HELLO'
    }, follow_redirects=True)
    # Should reject as duplicate
    assert Word.query.count() == 1

def test_word_tracks_user(authenticated_client, seeded_db):
    """Word records which user added it"""
    authenticated_client.post('/words/add', data={'word': 'test'})
    word = Word.query.filter_by(word='test').first()
    assert word.user is not None

def test_dashboard_shows_word_count(authenticated_client, seeded_db):
    """Dashboard displays total word count"""
    # Add some words
    authenticated_client.post('/words/add', data={'word': 'one'})
    authenticated_client.post('/words/add', data={'word': 'two'})
    response = authenticated_client.get('/')
    assert b'2' in response.data  # Word count shown
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Manual test: add words on mobile viewport, verify UX

---

## Sprint 4: Word List (Read)
**Goal**: Display all words with sorting and filtering

### Tasks
1. Create `app/templates/words.html`:
   - Table/list of all words
   - Columns: Word, Date Added, Added By, Category, Actions
   - Sort controls (by word alphabetically, by date)
   - Filter by category dropdown
   - Filter by user dropdown

2. Create `app/templates/partials/word_list.html` (modular component):
   - Reusable word list display
   - Can be included in other templates later

3. Mobile-responsive design:
   - Card layout on small screens (instead of table)
   - Touch-friendly sort/filter controls
   - Adequate spacing between items

4. In `app/routes.py`:
   - `GET /words` - display word list
   - Handle query parameters: `sort`, `order`, `category`, `user`

5. Add navigation link to word list from dashboard

### Deliverables
- [ ] Word list page displays all words
- [ ] Sorting works (A-Z, Z-A, newest, oldest)
- [ ] Filtering by category works
- [ ] Filtering by user works
- [ ] Combined filter + sort works
- [ ] Mobile layout is usable (test at 375px width)
- [ ] Word list is a reusable partial template

### Tests to Write and Pass
```python
# tests/test_word_list.py
def test_word_list_displays(authenticated_client, seeded_db, sample_words):
    """Word list page shows all words"""
    response = authenticated_client.get('/words')
    assert response.status_code == 200
    for word in sample_words:
        assert word.word.encode() in response.data

def test_sort_alphabetical(authenticated_client, seeded_db, sample_words):
    """Words can be sorted A-Z"""
    response = authenticated_client.get('/words?sort=word&order=asc')
    # Verify order in response

def test_sort_by_date(authenticated_client, seeded_db, sample_words):
    """Words can be sorted by date"""
    response = authenticated_client.get('/words?sort=date&order=desc')
    assert response.status_code == 200

def test_filter_by_category(authenticated_client, seeded_db, sample_words):
    """Words can be filtered by category"""
    response = authenticated_client.get('/words?category=1')
    assert response.status_code == 200
    # Verify only matching words shown

def test_filter_by_user(authenticated_client, seeded_db, sample_words):
    """Words can be filtered by user who added them"""
    response = authenticated_client.get('/words?user=1')
    assert response.status_code == 200
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Manual test: verify mobile layout in browser dev tools

---

## Sprint 5: Word Edit and Delete
**Goal**: Implement updating and removing words

### Tasks
1. Create `app/templates/edit_word.html`:
   - Form pre-populated with word data
   - Fields: word text, category dropdown
   - Save and Cancel buttons (large, touch-friendly)
   - Delete button (visually distinct, requires confirmation)

2. In `app/routes.py`:
   - `GET /words/<id>/edit` - display edit form
   - `POST /words/<id>/edit` - save changes
   - `POST /words/<id>/delete` - delete word

3. Edit functionality:
   - Update word text (with duplicate check against OTHER words)
   - Update category
   - Update `updated_at` timestamp
   - Preserve original `date_added` and `user_id`

4. Delete functionality:
   - JavaScript confirmation dialog before delete
   - Flash success message after delete
   - Redirect to word list

5. Add Edit button to word list table/cards

### Deliverables
- [ ] Edit form displays with pre-populated data
- [ ] Can change word text (with duplicate validation)
- [ ] Can change category
- [ ] `updated_at` updates on save
- [ ] Delete shows confirmation dialog
- [ ] Delete removes word from database
- [ ] Edit/Delete buttons visible in word list

### Tests to Write and Pass
```python
# tests/test_word_edit.py
def test_edit_form_loads(authenticated_client, seeded_db, sample_words):
    """Edit form loads with word data"""
    word = sample_words[0]
    response = authenticated_client.get(f'/words/{word.id}/edit')
    assert response.status_code == 200
    assert word.word.encode() in response.data

def test_edit_word_text(authenticated_client, seeded_db, sample_words):
    """Can edit word text"""
    word = sample_words[0]
    response = authenticated_client.post(f'/words/{word.id}/edit', data={
        'word': 'updated_word',
        'category_id': word.category_id or ''
    }, follow_redirects=True)
    updated = Word.query.get(word.id)
    assert updated.word == 'updated_word'

def test_edit_updates_timestamp(authenticated_client, seeded_db, sample_words):
    """Editing word updates updated_at"""
    word = sample_words[0]
    original_updated = word.updated_at
    authenticated_client.post(f'/words/{word.id}/edit', data={
        'word': 'changed'
    })
    updated = Word.query.get(word.id)
    assert updated.updated_at > original_updated

def test_edit_duplicate_rejected(authenticated_client, seeded_db, sample_words):
    """Cannot edit word to duplicate another word"""
    word1, word2 = sample_words[0], sample_words[1]
    response = authenticated_client.post(f'/words/{word1.id}/edit', data={
        'word': word2.word  # Try to rename to existing word
    }, follow_redirects=True)
    # Should reject, word1 should be unchanged
    assert Word.query.get(word1.id).word != word2.word

def test_delete_word(authenticated_client, seeded_db, sample_words):
    """Can delete a word"""
    word = sample_words[0]
    word_id = word.id
    response = authenticated_client.post(f'/words/{word_id}/delete', 
                                         follow_redirects=True)
    assert Word.query.get(word_id) is None
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Manual test: edit and delete flow on mobile

---

## Sprint 6: Basic Analytics
**Goal**: Display word statistics and milestone comparison

### Tasks
1. Create `app/templates/stats.html`:
   - Total word count (large, prominent display)
   - Baby's current age (calculated from BABY_BIRTHDATE env var)
   - Milestone comparison section:
     - Table of age ranges and typical word counts
     - Visual highlight on current age range
     - Show baby's actual count vs expected range
   - Words added by month (table format):
     - Month/Year | Words Added | Running Total

2. In `app/routes.py`:
   - `GET /stats` - compile and display statistics

3. Create `app/utils.py` helper functions (keep logic modular):
   - `calculate_age_months(birthdate)` - baby's age in months
   - `get_milestone_for_age(months)` - return milestone data
   - `group_words_by_month(words)` - aggregate words by month
   - `get_monthly_stats()` - return list of {month, count, running_total}

4. Create `app/milestones.py` - milestone reference data:
   - Store CDC-based milestones as data structure
   - Function to look up expected range for age

5. Add navigation link to stats page

### Deliverables
- [ ] Stats page displays total word count prominently
- [ ] Baby's age displays correctly
- [ ] Milestone table shows all age ranges
- [ ] Current age range is visually highlighted
- [ ] Baby's count compared to expected range
- [ ] Monthly breakdown table is accurate
- [ ] Helper functions are in separate module (not in routes)

### Tests to Write and Pass
```python
# tests/test_stats.py
def test_stats_page_loads(authenticated_client, seeded_db):
    """Stats page loads"""
    response = authenticated_client.get('/stats')
    assert response.status_code == 200

def test_total_count_accurate(authenticated_client, seeded_db, sample_words):
    """Stats shows correct total word count"""
    response = authenticated_client.get('/stats')
    expected_count = str(len(sample_words))
    assert expected_count.encode() in response.data

# tests/test_utils.py
def test_calculate_age_months():
    """Age calculation is correct"""
    from app.utils import calculate_age_months
    from datetime import date
    # Test with known dates
    birthdate = date(2024, 1, 15)
    today = date(2024, 7, 15)
    assert calculate_age_months(birthdate, today) == 6

def test_get_milestone_for_age():
    """Milestone lookup returns correct range"""
    from app.milestones import get_milestone_for_age
    milestone = get_milestone_for_age(18)
    assert 'min_words' in milestone
    assert 'max_words' in milestone

def test_group_words_by_month(app, seeded_db, sample_words):
    """Words grouped by month correctly"""
    from app.utils import group_words_by_month
    grouped = group_words_by_month(sample_words)
    # Verify structure and counts
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Utility functions have unit tests independent of Flask

---

## Sprint 7: CSV Export
**Goal**: Allow downloading all word data as CSV

### Tasks
1. In `app/routes.py`:
   - `GET /export` - generate and return CSV file

2. Create `app/export.py` (modular export logic):
   - Function to generate CSV content from words
   - Handle proper CSV formatting

3. CSV format:
   - Headers: Word, Date Added, Added By, Category
   - One row per word
   - Sorted by date added (oldest first)
   - Filename: `emily_words_YYYY-MM-DD.csv`

4. Add export buttons:
   - On stats page (prominent)
   - On word list page

5. Ensure proper CSV handling:
   - Handle commas in words (proper quoting)
   - Handle special characters
   - UTF-8 encoding with BOM for Excel compatibility

### Deliverables
- [ ] Export route returns CSV file download
- [ ] CSV has correct headers
- [ ] All words included in export
- [ ] Words sorted by date (oldest first)
- [ ] Filename includes current date
- [ ] Opens correctly in Excel and Google Sheets
- [ ] Export buttons on stats and word list pages

### Tests to Write and Pass
```python
# tests/test_export.py
def test_export_returns_csv(authenticated_client, seeded_db, sample_words):
    """Export returns CSV file"""
    response = authenticated_client.get('/export')
    assert response.status_code == 200
    assert 'text/csv' in response.content_type

def test_export_filename(authenticated_client, seeded_db, sample_words):
    """Export has correct filename with date"""
    response = authenticated_client.get('/export')
    assert 'attachment' in response.headers.get('Content-Disposition', '')
    assert 'emily_words_' in response.headers.get('Content-Disposition', '')
    assert '.csv' in response.headers.get('Content-Disposition', '')

def test_export_contains_all_words(authenticated_client, seeded_db, sample_words):
    """Export includes all words"""
    response = authenticated_client.get('/export')
    csv_content = response.data.decode('utf-8')
    for word in sample_words:
        assert word.word in csv_content

def test_export_headers(authenticated_client, seeded_db, sample_words):
    """Export has correct CSV headers"""
    response = authenticated_client.get('/export')
    csv_content = response.data.decode('utf-8')
    first_line = csv_content.split('\n')[0]
    assert 'Word' in first_line
    assert 'Date Added' in first_line
    assert 'Added By' in first_line
    assert 'Category' in first_line

def test_export_handles_special_characters(authenticated_client, seeded_db):
    """Export handles commas and quotes in words"""
    # Add word with comma
    authenticated_client.post('/words/add', data={'word': 'uh-oh, no'})
    response = authenticated_client.get('/export')
    # Should be properly quoted in CSV
    assert response.status_code == 200
```

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Manual test: download and open in Excel/Sheets

---

## Sprint 8: UI Polish
**Goal**: Improve visual design and mobile experience

### Tasks
1. Create modular CSS structure in `app/static/`:
   - `style.css` - main stylesheet (imports others)
   - `layout.css` - grid, flexbox, responsive breakpoints
   - `components.css` - buttons, forms, cards, tables
   - `utilities.css` - spacing, colors, typography helpers

2. Design system:
   - Define color variables (CSS custom properties)
   - Define spacing scale
   - Define typography scale
   - Consistent border-radius, shadows

3. Mobile-first responsive design:
   - Base styles for mobile (375px)
   - Tablet breakpoint (~768px)
   - Desktop breakpoint (~1024px)
   - Touch targets minimum 44x44px

4. Component styling:
   - Forms: large inputs, clear labels, visible focus states
   - Buttons: distinct primary/secondary/danger styles
   - Cards: for word list on mobile
   - Tables: horizontal scroll on mobile, or convert to cards
   - Navigation: hamburger menu or simplified nav on mobile

5. Dashboard improvements:
   - Word entry form is visually prominent
   - Recent words preview (last 5 added)
   - Quick stats summary (total words, words this month)

6. Flash message styling:
   - Success: green theme
   - Error: red theme
   - Info: blue theme
   - Auto-dismiss or close button

### Deliverables
- [ ] CSS is organized into modular files
- [ ] Color and spacing variables defined
- [ ] All pages look good at 375px width
- [ ] All touch targets are 44px minimum
- [ ] Forms are easy to use on mobile
- [ ] Flash messages are styled and noticeable
- [ ] Dashboard shows recent words preview

### Tests to Write and Pass
```python
# tests/test_ui.py
def test_static_css_exists(client):
    """CSS files are served"""
    response = client.get('/static/style.css')
    assert response.status_code == 200

def test_dashboard_shows_recent_words(authenticated_client, seeded_db, sample_words):
    """Dashboard shows recent words preview"""
    response = authenticated_client.get('/')
    # Should show some recent words
    assert response.status_code == 200
    # At least one word visible
    assert any(w.word.encode() in response.data for w in sample_words[-5:])

def test_responsive_viewport_meta(authenticated_client, seeded_db):
    """Pages include viewport meta tag"""
    response = authenticated_client.get('/')
    assert b'viewport' in response.data
    assert b'width=device-width' in response.data
```

### Manual Testing Checklist (Required)
- [ ] Test on iPhone Safari (or Chrome DevTools iPhone emulation)
- [ ] Test on Android Chrome (or emulation)
- [ ] All buttons easily tappable with thumb
- [ ] Text readable without zooming
- [ ] Forms usable with on-screen keyboard
- [ ] No horizontal scrolling on any page

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Manual testing checklist complete

---

## Sprint 9: Railway Deployment
**Goal**: Deploy working application to Railway

### Tasks
1. Create deployment files:
   - `Procfile`: `web: gunicorn run:app`
   - `runtime.txt`: specify Python version (e.g., `python-3.11.x`)
   - `railway.json` (optional): Railway-specific config

2. Update `config.py` for production:
   - Handle Railway's DATABASE_URL format (may need `postgresql://` fix)
   - Secure session cookies in production
   - Debug = False in production

3. Create database initialization strategy:
   - Option A: Flask CLI command `flask init-db`
   - Option B: One-time `/init` route (protected, then removed)
   - Must seed users and categories

4. GitHub repository setup:
   - Initialize git repo
   - Verify .gitignore excludes: `.env`, `__pycache__`, `*.pyc`, `.pytest_cache`
   - Commit all code
   - Push to GitHub

5. Railway setup:
   - Create account (use GitHub OAuth)
   - Create new project → Deploy from GitHub repo
   - Add PostgreSQL database (click "New" → "Database" → "PostgreSQL")
   - Configure environment variables in Railway dashboard:
     - `SECRET_KEY` (generate secure random string)
     - `NICK_PASSWORD` (plaintext, app hashes it)
     - `WIFE_PASSWORD` (plaintext, app hashes it)
     - `BABY_BIRTHDATE` (format: YYYY-MM-DD)
     - `WIFE_DISPLAY_NAME` (e.g., "Sarah")
   - Note: `DATABASE_URL` is automatically set by Railway

6. Deploy and initialize:
   - Push triggers auto-deploy
   - Run database initialization
   - Verify app works at Railway URL

### Deliverables
- [ ] Procfile and deployment files created
- [ ] Config handles production settings
- [ ] Code pushed to GitHub (public repo)
- [ ] Railway project created and connected
- [ ] PostgreSQL database provisioned
- [ ] Environment variables configured
- [ ] App deployed and accessible
- [ ] Database initialized with users/categories
- [ ] Can log in and add words on live site

### Pre-Deployment Verification
```bash
# Run locally with production-like settings
export FLASK_ENV=production
export DATABASE_URL=postgresql://... # local postgres or use SQLite for test
python run.py

# Run full test suite
pytest -v

# Check for any hardcoded secrets or debug settings
grep -r "debug=True" .
grep -r "secret" . --include="*.py" | grep -v "environ"
```

### Post-Deployment Tests (Manual)
- [ ] App loads at Railway URL
- [ ] Login works for both users
- [ ] Can add a word
- [ ] Word persists after page refresh
- [ ] Can view word list
- [ ] Can export CSV
- [ ] Stats page calculates correctly
- [ ] Restart Railway service → data still present

### Definition of Done
- [ ] All deliverables checked off
- [ ] Full test suite passes locally
- [ ] Post-deployment manual tests pass
- [ ] App is live and functional

---

## Sprint 10: Charts (Enhancement)
**Goal**: Add visual charts for word growth

### Tasks
1. Add Chart.js via CDN in `base.html`:
   - Load from CDN in scripts block
   - Only load on pages that need it

2. Create `app/templates/partials/charts.html`:
   - Modular chart components
   - Line chart: cumulative words over time
   - Bar chart: words added per month

3. Create API endpoint for chart data:
   - `GET /api/chart-data` - return JSON
   - Response: `{ monthly: [...], cumulative: [...] }`

4. Update `app/templates/stats.html`:
   - Include chart partial
   - Chart containers with appropriate sizing
   - Responsive chart sizing

5. JavaScript for charts (in separate file or partial):
   - Fetch data from API
   - Initialize Chart.js charts
   - Handle responsive resizing

### Deliverables
- [ ] Chart.js loaded from CDN
- [ ] API endpoint returns correct JSON data
- [ ] Line chart shows cumulative growth
- [ ] Bar chart shows monthly additions
- [ ] Charts render correctly on mobile
- [ ] Charts update when page loads
- [ ] Chart code is modular/reusable

### Tests to Write and Pass
```python
# tests/test_charts.py
def test_chart_api_endpoint(authenticated_client, seeded_db, sample_words):
    """Chart API returns JSON data"""
    response = authenticated_client.get('/api/chart-data')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_chart_api_structure(authenticated_client, seeded_db, sample_words):
    """Chart API returns expected structure"""
    response = authenticated_client.get('/api/chart-data')
    data = response.get_json()
    assert 'monthly' in data
    assert 'cumulative' in data
    assert isinstance(data['monthly'], list)

def test_chart_data_accuracy(authenticated_client, seeded_db, sample_words):
    """Chart data matches actual word counts"""
    response = authenticated_client.get('/api/chart-data')
    data = response.get_json()
    # Last cumulative value should equal total words
    total_words = len(sample_words)
    if data['cumulative']:
        assert data['cumulative'][-1]['count'] == total_words
```

### Manual Testing Checklist
- [ ] Charts visible on stats page
- [ ] Charts render on mobile without overflow
- [ ] Data matches table data
- [ ] Charts load within 2 seconds

### Definition of Done
- [ ] All deliverables checked off
- [ ] All tests written and passing
- [ ] Manual testing checklist complete

---

## General Guidelines for All Sprints

### Before Starting a Sprint
1. Read the sprint requirements completely
2. Review related sections in SPEC.md
3. Understand the Definition of Done

### During a Sprint
1. Write tests first or alongside code (TDD encouraged)
2. Keep code modular - avoid large functions
3. Use meaningful variable/function names
4. Add docstrings to functions
5. Commit frequently with clear messages

### Completing a Sprint
1. Run `pytest -v` - all tests must pass
2. Check all deliverables are complete
3. Verify Definition of Done criteria
4. Do manual testing where specified
5. Commit with message: "Complete Sprint X: [Sprint Name]"

### Code Quality Standards
- Max function length: ~50 lines
- Max file length: ~300 lines (split if larger)
- No hardcoded secrets
- No debug code in commits
- All functions have docstrings

---

## Post-MVP Ideas (Not Sprinted)

These can be tackled after core app is stable:

- Word categorization bulk edit
- Notes field for words (context, funny story, etc.)
- Search functionality
- Date picker to backdate words
- Multiple children support
- Dark mode
- PWA for home screen installation

---

## Environment Variables Reference

```
# Required
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-here
NICK_PASSWORD=plaintext-password-here
WIFE_PASSWORD=plaintext-password-here
BABY_BIRTHDATE=2024-01-15
WIFE_DISPLAY_NAME=Sarah

# Optional
FLASK_ENV=development  # or 'production'
```

Note: Passwords in env vars are plaintext. The app hashes them when creating/verifying users. In Railway, set these in the Variables tab - never commit to git.

---

## Testing Quick Reference

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with coverage
pytest --cov=app

# Run and stop on first failure
pytest -x
```
