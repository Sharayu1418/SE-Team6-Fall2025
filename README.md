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

- **Backend**: Django 5.1, Django REST Framework, Django Channels
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL (SQLite fallback for local dev)
- **Frontend**: React 18 + Vite, Tailwind CSS (Modern SPA with WebSocket support)
- **AI Agents**: AutoGen multi-agent system with Ollama LLM
- **Deployment**: Docker + Gunicorn + Daphne + Whitenoise

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

### Backend (Django)
| URL | Description |
|-----|-------------|
| http://localhost:8000 | Django backend API |
| http://localhost:8000/admin | Admin panel (superuser required) |
| http://localhost:8000/api/ | REST API root |
| ws://localhost:8000/ws/agents/ | WebSocket for agent execution |

### Frontend (React)
| URL | Description |
|-----|-------------|
| http://localhost:5173 | React frontend (Vite dev server) |
| http://localhost:5173/login | User login |
| http://localhost:5173/register | User registration |
| http://localhost:5173/downloads | Downloads management |
| http://localhost:5173/preferences | User preferences |

---

## 🔧 Common Commands

### Backend Commands
```bash
# Development server (ASGI with Channels support)
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

# Run Celery worker (required for downloads)
celery -A smartcache worker --loglevel=info

# Run Celery beat scheduler (optional)
celery -A smartcache beat --loglevel=info
```

### Frontend Commands
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
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
| `/api/auth/register/` | POST | Register new user with preferences |
| `/api/auth/login/` | POST | Login user (session-based) |
| `/api/auth/logout/` | POST | Logout user |
| `/api/auth/me/` | GET | Get current authenticated user |
| `/api/sources/` | GET, POST, PUT, DELETE | Content sources |
| `/api/subscriptions/` | GET, POST, PUT, DELETE | User subscriptions |
| `/api/commute/` | GET, POST, PUT, DELETE | Commute windows |
| `/api/downloads/` | GET, POST, PUT, DELETE | Download items |
| `/api/downloads/:id/file/` | GET | Download file for authenticated user |
| `/api/preferences/` | GET, POST, PATCH | User preferences |

### WebSocket Endpoints

| Endpoint | Protocol | Description |
|----------|----------|-------------|
| `/ws/agents/` | WebSocket | Real-time agent execution updates |

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
| **[frontend/README.md](frontend/README.md)** | React frontend documentation | Frontend development, setup |
| **[AUTOGEN_STATUS.md](AUTOGEN_STATUS.md)** | AutoGen agent system status | Understanding multi-agent workflow |
| **[ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md)** | ETL pipeline documentation | Content ingestion workflow |

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

---

## 🎨 React Frontend

SmartCache AI now includes a modern React single-page application with real-time agent execution capabilities!

### Quick Start

```bash
# Terminal 1: Start Django backend
python manage.py runserver

# Terminal 2: Start Celery worker
celery -A smartcache worker --loglevel=info

# Terminal 3: Start Redis
redis-server

# Terminal 4: Start React frontend
cd frontend
npm install  # First time only
npm run dev
```

Visit http://localhost:5173 to use the React frontend.

### Features

- **User Registration**: Sign up with personalized content preferences (topics, limits)
- **Authentication**: Session-based login with Django backend
- **Agent Execution**: Click a button to trigger RoundRobinGroupChat agents via WebSocket
- **Real-time Updates**: Watch agent activity live as they discover and queue content
- **Downloads Management**: View, filter, and download your content
- **Preferences Editor**: Update your topics and limits anytime

### How It Works

1. **Register** at `/register` with your preferences (topics, daily limits, storage)
2. **Dashboard** shows your stats and the "Discover & Download Content" button
3. **Click the button** to connect via WebSocket and trigger the multi-agent system
4. **Watch in real-time** as:
   - Discovery Agent finds content based on your subscriptions
   - Download Agent queues downloads (automatically processed via Django signals)
   - Summarizer Agent provides quality assessment
5. **View Downloads** page to see status and download ready files
6. **Update Preferences** anytime to change your content discovery settings

For detailed frontend documentation, see **[frontend/README.md](frontend/README.md)**.

---

*Last updated: November 10, 2025 | Sprint 2 - React Frontend + AutoGen Agents*
