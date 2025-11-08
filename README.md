# SmartCache AI

**Intelligent Offline Content Curator for Subway Riders**

> Django 5 web application that automatically curates podcasts, articles, and news based on user preferences and commute schedules.

---

## 🚀 Quick Start (Already Set Up?)

**If your environment is already configured, jump straight to development:**

👉 **[QUICK_START.md](QUICK_START.md)** - Commands, workflows, and daily development reference

```bash
source venv/bin/activate
python manage.py runserver
# Visit http://localhost:8000
```

---

## 📚 First Time Here? New to Django?

**Complete setup guide with explanations and Django tutorials:**

👉 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Comprehensive walkthrough for beginners

This guide includes:
- ✅ What was fixed during setup
- ✅ Django concepts explained
- ✅ Project structure walkthrough
- ✅ Learning resources
- ✅ Troubleshooting

---

## 📦 Installing New Packages?

👉 **[PACKAGE_MANAGEMENT.md](PACKAGE_MANAGEMENT.md)** - Package installation guide

Quick command:
```bash
pip install <package> --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
# Then manually add to requirements.txt
```

---

## ⚡ Ultra-Quick Setup (Fresh Clone)

```bash
# Run automated setup script
./setup.sh

# Create admin account
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## 🎯 Project Overview

### Features (Sprint 1)

- ⏰ **Commute Windows** - Define when you need content ready
- 📡 **Content Sources** - Subscribe to podcasts and articles
- 📱 **Download Management** - Track content preparation status
- 🔄 **Automated Scheduling** - Celery-based content preparation
- 📱 **PWA Ready** - Service worker and manifest for offline capability
- 🔐 **Admin Interface** - Full Django admin for content management

### Tech Stack

- **Backend**: Django 5.1, Django REST Framework
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL (SQLite fallback for local dev)
- **Frontend**: Bootstrap 5 + HTMX
- **Deployment**: Docker + Gunicorn + Whitenoise

---

## 📋 Project Structure

```
SE-Team6-Fall2025/
│
├── README.md              ← You are here
├── QUICK_START.md         ← Daily development reference
├── SETUP_GUIDE.md         ← Comprehensive setup & learning guide
├── PACKAGE_MANAGEMENT.md  ← How to install packages
├── setup.sh               ← Automated setup script
│
├── manage.py              ← Django CLI tool
├── requirements.txt       ← Python dependencies
├── db.sqlite3             ← SQLite database (local dev)
│
├── smartcache/            ← Django project settings
│   ├── settings.py        ← Configuration
│   ├── urls.py            ← Root URL routing
│   └── celery.py          ← Celery config
│
├── core/                  ← Main Django app
│   ├── models.py          ← 6 database models
│   ├── views.py           ← Web pages & API endpoints
│   ├── tasks.py           ← Background tasks
│   ├── admin.py           ← Admin panel config
│   ├── serializers.py     ← REST API serializers
│   └── management/        ← Custom commands
│       └── commands/
│           └── seed_defaults.py
│
├── templates/             ← HTML templates
│   ├── base.html
│   ├── index.html
│   ├── commutes.html
│   ├── sources.html
│   └── downloads.html
│
└── static/                ← Static files (CSS, JS)
    └── sw.js              ← Service worker
```

---

## 🗄️ Database Models

1. **UserPreference** - User content preferences (topics, limits)
2. **CommuteWindow** - When user needs content ready (e.g., Mon-Fri 8-9 AM)
3. **ContentSource** - Available podcasts/article feeds (7 pre-loaded)
4. **Subscription** - Links users to sources they follow
5. **DownloadItem** - Prepared content for users
6. **EventLog** - User interaction tracking (for future ML)

---

## 🌐 Key URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Homepage/Dashboard |
| http://localhost:8000/admin | Admin panel (superuser required) |
| http://localhost:8000/api/ | REST API root |
| http://localhost:8000/commutes/ | Commute window management |
| http://localhost:8000/sources/ | Content sources & subscriptions |
| http://localhost:8000/downloads/ | Prepared downloads |

---

## 🔧 Common Commands

```bash
# Development server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Django shell
python manage.py shell

# Load sample data
python manage.py seed_defaults

# Check for issues
python manage.py check

# Run Celery worker (optional)
celery -A smartcache worker --loglevel=info

# Run Celery beat scheduler (optional)
celery -A smartcache beat --loglevel=info
```

---

## 🎓 For Django Beginners

### Recommended Learning Path

1. **Read [SETUP_GUIDE.md](SETUP_GUIDE.md)** - Understand Django basics
2. **Explore the admin panel** - http://localhost:8000/admin
3. **Read `core/models.py`** - Understand the data structure
4. **Read `core/views.py`** - See how requests are handled
5. **Check templates/** - See how HTML is generated
6. **Make small changes** - Add a field, update a template

### Official Django Resources

- [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Django Models Guide](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)

---

## 🔄 API Endpoints

Base URL: `/api/`

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/sources/` | GET, POST, PUT, DELETE | Content sources |
| `/api/subscriptions/` | GET, POST, PUT, DELETE | User subscriptions |
| `/api/commute/` | GET, POST, PUT, DELETE | Commute windows |
| `/api/downloads/` | GET, POST, PUT, DELETE | Download items |
| `/api/preferences/` | GET, POST | User preferences |

---

## 🐛 Troubleshooting

### Common Issues

**Module not found errors**
```bash
# Make sure venv is activated
source venv/bin/activate
```

**Database errors**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py seed_defaults
```

**Port already in use**
```bash
# Use different port
python manage.py runserver 8080
```

**SSL certificate errors (when installing packages)**
```bash
# Use trusted host flags (see PACKAGE_MANAGEMENT.md)
pip install <package> --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

---

## 📦 Sample Data

After running `seed_defaults`, you'll have 7 content sources:

**Podcasts:**
- NPR News Now
- TED Talks Daily
- NASA Breaking News
- BBC World

**Articles:**
- Hacker News Frontpage
- Reddit API
- Substack Crawler

All with real RSS feed URLs ready for testing!

---

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t smartcache .

# Run container
docker run -p 8000:8000 smartcache
```

### Environment Variables

Create `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost/smartcache
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## ✅ Sprint 1 Acceptance Criteria

- [x] App boots without Redis/PostgreSQL (SQLite fallback)
- [x] All models + admin + migrations created
- [x] `seed_defaults` command populates sample sources
- [x] REST API endpoints under `/api/`
- [x] Celery configured with content preparation stubs
- [x] Bootstrap 5 + HTMX frontend templates
- [x] PWA manifest + service worker placeholders
- [x] Docker configuration for deployment

---

## 🎯 Next Steps (Future Sprints)

- [ ] Implement actual content scraping logic
- [ ] Add user authentication improvements
- [ ] Mobile-responsive optimizations
- [ ] Advanced content filtering and ML recommendations
- [ ] Real-time sync capabilities
- [ ] Enhanced offline PWA features

---

## 📖 Documentation Index

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **README.md** (this file) | Project overview & navigation | First entry point |
| **[QUICK_START.md](QUICK_START.md)** | Daily development reference | Already set up, need commands |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Comprehensive setup guide | First-time setup, learning Django |
| **[PACKAGE_MANAGEMENT.md](PACKAGE_MANAGEMENT.md)** | Package installation guide | Installing new dependencies |

---

## 🤝 Contributing

This is a team project for SE-Team6-Fall2025. The repository is private and accessible to team members and the TA.

---

## 📝 Notes

- **Python Version**: 3.13+ (3.11+ also supported)
- **Database**: SQLite for local dev (no PostgreSQL required)
- **Redis**: Optional (only needed for Celery background tasks)
- **SSL Certificates**: Installed via `/Applications/Python 3.13/Install Certificates.command`

---

## 🎉 Ready to Start?

1. **Already set up?** → [QUICK_START.md](QUICK_START.md)
2. **First time?** → [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. **Installing packages?** → [PACKAGE_MANAGEMENT.md](PACKAGE_MANAGEMENT.md)

**Questions?** Check the guides above or explore the Django admin panel!

---

*Last updated: October 19, 2025 | Sprint 1*
