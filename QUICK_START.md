# SmartCache AI - Quick Start Reference

## ✅ Setup Complete!

Your environment is ready:
- ✅ Fresh virtual environment with Python 3.13
- ✅ All 33 packages installed successfully
- ✅ Database migrated (18 migrations applied)
- ✅ 7 sample content sources loaded
- ✅ Django system check passed

---

## 🚀 Start Developing Now!

### Step 1: Create Admin Account
```bash
cd /Users/anitejsrivastava/Documents/GitHub/SE-Team6-Fall2025
source venv/bin/activate
python manage.py createsuperuser
```

```bash
brew services restart redis
redis-cli
redis-cli ping
celery -A smartcache worker -l info
```

### Step 2: Run Server
```bash
python manage.py runserver
```

### Step 3: Open Browser
- **Homepage**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/

---

## 📝 Daily Workflow

```bash
# Activate venv (do this first every time)
source venv/bin/activate

# Run server
python manage.py runserver

# Open Django shell (for testing)
python manage.py shell

# Apply new migrations
python manage.py makemigrations
python manage.py migrate

# Test content preparation task
python manage.py shell -c "from core.tasks import nightly_prepare_content; nightly_prepare_content()"
```

---

## 🔑 Key Files to Explore

### Core Application
- `core/models.py` - 6 database models (start here!)
- `core/views.py` - Web pages and API endpoints
- `core/tasks.py` - Celery background tasks
- `core/admin.py` - Admin panel configuration

### Templates
- `templates/base.html` - Base template
- `templates/index.html` - Homepage
- `templates/commutes.html` - Commute management
- `templates/sources.html` - Content sources
- `templates/downloads.html` - Downloads list

### Configuration
- `smartcache/settings.py` - Django settings
- `smartcache/urls.py` - URL routing
- `requirements.txt` - Python packages

---

## 📊 Database Models Overview

1. **UserPreference** - User content preferences (topics, limits)
2. **CommuteWindow** - When user needs content ready
3. **ContentSource** - Available podcasts/article feeds
4. **Subscription** - Links users to sources they follow
5. **DownloadItem** - Prepared content for users
6. **EventLog** - User interaction tracking

---

## 🎯 Sample Data Included

7 content sources ready to explore:
- NPR News Now (podcast)
- TED Talks Daily (podcast)
- NASA Breaking News (podcast)
- BBC World (podcast)
- Hacker News Frontpage (article)
- Reddit API (article)
- Substack Crawler (article)

---

## 🐛 Common Commands

```bash
# Check for issues
python manage.py check

# See migration status
python manage.py showmigrations

# Create new app
python manage.py startapp <app_name>

# Collect static files
python manage.py collectstatic

# Open database shell
python manage.py dbshell

# Run tests (when you create them)
python manage.py test

# Change user password
python manage.py changepassword <username>
```

---

## 🔄 If You Need to Reset

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_defaults
python manage.py createsuperuser
```

### Reinstall Packages
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

---

## 📚 Learning Path (for Django beginners)

### Week 1: Understand the Basics
1. Read `core/models.py` - understand the data structure
2. Explore admin panel - create test data
3. Read `core/views.py` - see how requests are handled
4. Browse `templates/` - see how HTML is generated

### Week 2: Make Small Changes
1. Add a new field to a model
2. Create a migration and apply it
3. Update the admin panel to show the new field
4. Modify a template to display it

### Week 3: Add New Features
1. Create a new view function
2. Add a URL route for it
3. Create a new template
4. Test it in the browser

### Official Resources
- [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Django Models](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)

---

## ⚡ Pro Tips

1. **Always activate venv first**: `source venv/bin/activate`
2. **Use Django shell for testing**: `python manage.py shell`
3. **Check admin panel often**: Great way to inspect data
4. **Read error messages carefully**: Django has helpful error pages
5. **Make small changes**: Test frequently as you develop

---

## 🎉 You're Ready!

Everything is set up and working. Your next command:

```bash
python manage.py createsuperuser
```

Then start the server and explore! 🚀

---

*For detailed information, see `SETUP_GUIDE.md`*

