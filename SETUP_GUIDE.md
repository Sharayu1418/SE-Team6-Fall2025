# SmartCache AI - Setup Guide for macOS

## 🎉 Quick Start (Already Done!)

Your environment is now set up! Here's what was completed:

✅ Virtual environment created (`venv/`)  
✅ All Python dependencies installed  
✅ Database migrations applied  
✅ Sample content sources loaded  

---

## 🚀 Next Steps

### 1. Create an Admin Account

```bash
source venv/bin/activate
python manage.py createsuperuser
```

Follow the prompts to create your admin username, email, and password.

### 2. Run the Development Server

```bash
python manage.py runserver
```

Then open your browser to: **http://localhost:8000**

### 3. Explore the App

- **Homepage**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin (login with superuser)
- **API**: http://localhost:8000/api/
- **Commutes**: http://localhost:8000/commutes/
- **Sources**: http://localhost:8000/sources/
- **Downloads**: http://localhost:8000/downloads/

---

## 🔧 What Was Fixed

### Issue 1: SSL Certificate Verification Error

**Problem**: Python 3.13 on macOS couldn't verify SSL certificates when connecting to PyPI.

**Solution Applied**:
- Used `--trusted-host` flags during installation
- Updated `requirements.txt` to use Python 3.13-compatible packages

**Permanent Fix** (Recommended):

Run this command once to install Python's SSL certificates:

```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

After this, you won't need `--trusted-host` flags anymore.

### Issue 2: psycopg2-binary Compatibility

**Problem**: `psycopg2-binary==2.9.9` doesn't support Python 3.13 yet.

**Solution Applied**:
- Updated `requirements.txt` to use `psycopg[binary]>=3.1.0` for Python 3.13+
- Kept `psycopg2-binary` for older Python versions
- Made version constraints more flexible

---

## 📦 Updated requirements.txt

The file now includes:

```txt
Django>=5.0.6,<5.2
djangorestframework>=3.15.1
celery>=5.3.4
redis>=5.0.1
psycopg2-binary>=2.9.9; python_version < '3.13'
psycopg[binary]>=3.1.0; python_version >= '3.13'
gunicorn>=21.2.0
whitenoise>=6.6.0
dj-database-url>=2.1.0
python-dotenv>=1.0.0
feedparser>=6.0.11
requests>=2.31.0
django-cors-headers>=4.3.1
```

Key changes:
- ✅ Conditional PostgreSQL adapter based on Python version
- ✅ Flexible version ranges for better compatibility
- ✅ Future-proof for Python version updates

---

## 🔄 Daily Development Workflow

### Starting Your Day

```bash
# 1. Navigate to project
cd /Users/anitejsrivastava/Documents/GitHub/SE-Team6-Fall2025

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run the server
python manage.py runserver
```

### Making Model Changes

```bash
# 1. Edit models in core/models.py

# 2. Create migration
python manage.py makemigrations

# 3. Apply migration
python manage.py migrate
```

### Viewing Logs

Django will show logs in your terminal where `runserver` is running.

---

## 🎯 Optional: Background Tasks (Celery + Redis)

For automated content preparation, you need Redis and Celery:

### Install Redis

```bash
brew install redis
brew services start redis
```

### Run Celery (in separate terminals)

**Terminal 1**: Django server
```bash
python manage.py runserver
```

**Terminal 2**: Celery worker (processes tasks)
```bash
celery -A smartcache worker --loglevel=info
```

**Terminal 3**: Celery beat (schedules tasks)
```bash
celery -A smartcache beat --loglevel=info
```

### Test Content Preparation Manually

```bash
python manage.py shell
>>> from core.tasks import nightly_prepare_content
>>> nightly_prepare_content()
```

---

## 📁 Key Files to Know

### Django Project Structure

```
SE-Team6-Fall2025/
├── manage.py              # Django CLI tool
├── requirements.txt       # Python dependencies (UPDATED)
├── setup.sh              # Automated setup script (NEW)
│
├── smartcache/           # Project settings
│   ├── settings.py       # Configuration
│   ├── urls.py           # Root URL routing
│   └── celery.py         # Celery config
│
├── core/                 # Main app
│   ├── models.py         # Database models (6 models)
│   ├── views.py          # View functions & API
│   ├── tasks.py          # Celery background tasks
│   ├── admin.py          # Admin panel config
│   └── management/
│       └── commands/
│           └── seed_defaults.py
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── commutes.html
│   ├── sources.html
│   └── downloads.html
│
├── static/              # Static files (CSS, JS)
│   └── sw.js            # Service worker
│
└── db.sqlite3           # SQLite database (created after migrate)
```

---

## 🐛 Troubleshooting

### "Module not found" errors

Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

### SSL errors when installing packages

Run the certificate installer:
```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

Or use trusted hosts temporarily:
```bash
pip install <package> --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

### Database errors

Delete the database and recreate:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_defaults
python manage.py createsuperuser
```

### Port already in use (8000)

Use a different port:
```bash
python manage.py runserver 8080
```

---

## 📚 Learning Resources

### Django Beginner Tutorials

- [Official Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Django for Beginners](https://djangoforbeginners.com/)
- [Django Girls Tutorial](https://tutorial.djangogirls.org/)

### Key Django Concepts

1. **Models**: Define your database structure (`core/models.py`)
2. **Views**: Handle HTTP requests (`core/views.py`)
3. **Templates**: HTML with dynamic content (`templates/`)
4. **URLs**: Route URLs to views (`urls.py`)
5. **Admin**: Built-in admin interface (`/admin/`)
6. **Migrations**: Database version control

### Useful Commands Reference

```bash
# Server
python manage.py runserver              # Start dev server
python manage.py runserver 0.0.0.0:8000 # Make accessible on network

# Database
python manage.py makemigrations         # Create new migrations
python manage.py migrate                # Apply migrations
python manage.py dbshell                # Open database shell

# Users
python manage.py createsuperuser        # Create admin user
python manage.py changepassword <username>  # Change password

# Django Shell (interactive Python)
python manage.py shell                  # Open Django shell
python manage.py shell -c "from core.models import ContentSource; print(ContentSource.objects.all())"

# Utilities
python manage.py check                  # Check for problems
python manage.py showmigrations         # Show migration status
python manage.py collectstatic          # Collect static files (for production)
```

---

## 🎓 Project-Specific Tips

### Understanding the Data Flow

1. **User creates account** → Django's built-in `User` model
2. **User sets commute windows** → `CommuteWindow` model
3. **User subscribes to sources** → `Subscription` links `User` + `ContentSource`
4. **Celery task runs nightly** → `nightly_prepare_content()` in `tasks.py`
5. **Task fetches RSS feeds** → Creates `DownloadItem` records
6. **User sees content** → `/downloads/` page shows `DownloadItem` list

### Testing the System

1. Log into admin panel: `/admin/`
2. Create a `CommuteWindow` for your user
3. Create a `Subscription` to a source (e.g., "NPR News Now")
4. Manually run: `python manage.py shell -c "from core.tasks import nightly_prepare_content; nightly_prepare_content()"`
5. Check `/downloads/` to see prepared content

### Sample Data Included

After running `seed_defaults`, you have:

- **Podcasts**: NPR News Now, TED Talks Daily, NASA Breaking News, BBC World
- **Articles**: Hacker News Frontpage, Reddit API, Substack Crawler

All with real RSS feed URLs!

---

## 🚀 Ready to Code!

You're all set! Here's your first task:

1. Create a superuser: `python manage.py createsuperuser`
2. Run the server: `python manage.py runserver`
3. Log into the admin: http://localhost:8000/admin
4. Explore the models and create some test data
5. Browse the frontend pages

**Need help?** Ask questions or check the Django documentation!

---

## 📝 Future Setup (After Fresh Clone)

If you clone this repo on another machine, just run:

```bash
./setup.sh
```

This automated script will:
- Create virtual environment
- Install all dependencies
- Run migrations
- Seed sample data

Then just create a superuser and you're ready!

---

*Last updated: October 19, 2025*

