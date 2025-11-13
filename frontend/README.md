# SmartCache AI - Sprint 1 Web Pilot

Intelligent Offline Content Curator with initial focus on subway riders.

## Overview

SmartCache AI is a Django 5 web application that helps users prepare personalized offline content for their commutes. The system automatically curates podcasts, articles, and news based on user preferences and commute schedules.

## Features (Sprint 1)

- ⏰ **Commute Windows**: Define when you need content ready
- 📡 **Content Sources**: Subscribe to podcasts and articles
- 📱 **Download Management**: Track content preparation status
- 🔄 **Automated Scheduling**: Celery-based content preparation
- 📱 **PWA Ready**: Service worker and manifest for offline capability
- 🔐 **Admin Interface**: Full Django admin for content management

## Tech Stack

- **Backend**: Django 5, Django REST Framework
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL (SQLite fallback)
- **Frontend**: Bootstrap 5 + HTMX
- **Deployment**: Docker + Gunicorn + Whitenoise

## Local Development

### Prerequisites

- Python 3.11+
- Redis (optional for basic preview)
- PostgreSQL (optional, SQLite fallback available)

### Setup

1. **Clone and setup virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database setup:**
   ```bash
   python manage.py migrate
   python manage.py seed_defaults
   python manage.py createsuperuser
   ```

3. **Run development server:**
   ```bash
   python manage.py runserver
   ```

4. **Optional: Run Celery (separate terminals):**
   ```bash
   # Worker
   celery -A smartcache worker --loglevel=info
   
   # Beat scheduler
   celery -A smartcache beat --loglevel=info
   ```

### Test Content Preparation

```bash
# Manually trigger content preparation
python manage.py shell -c "from core.tasks import nightly_prepare_content; nightly_prepare_content()"
```

## API Endpoints

Base URL: `/api/`

- `GET/POST/PUT/DELETE /api/sources/` - Content sources
- `GET/POST/PUT/DELETE /api/subscriptions/` - User subscriptions  
- `GET/POST/PUT/DELETE /api/commute/` - Commute windows
- `GET/POST/PUT/DELETE /api/downloads/` - Download items
- `GET/POST /api/preferences/` - User preferences

## Admin Interface

Access at `/admin/` with superuser credentials.

Pre-configured models:
- User Preferences
- Commute Windows  
- Content Sources
- Subscriptions
- Download Items
- Event Logs

## Environment Variables

Create `.env` file (see `.env.example`):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost/smartcache
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Docker Deployment

```bash
# Build image
docker build -t smartcache .

# Run container
docker run -p 8000:8000 smartcache
```

## Project Structure

```
smartcache/
├── core/                   # Main Django app
│   ├── models.py          # Data models
│   ├── views.py           # Views and API endpoints
│   ├── tasks.py           # Celery tasks
│   ├── admin.py           # Admin configuration
│   └── management/        # Custom commands
├── templates/             # HTML templates
├── static/               # Static assets + PWA files
├── smartcache/           # Django project settings
└── requirements.txt      # Python dependencies
```

## Sprint 1 Acceptance Criteria ✅

- [x] App boots without Redis/PostgreSQL (SQLite fallback)
- [x] All models + admin + migrations created
- [x] `seed_defaults` command populates sample sources
- [x] REST API endpoints under `/api/`
- [x] Celery configured with content preparation stubs
- [x] Bootstrap 5 + HTMX frontend templates
- [x] PWA manifest + service worker placeholders
- [x] Docker configuration for deployment

## Next Steps (Future Sprints)

- Implement actual content scraping logic
- Add user authentication improvements
- Mobile-responsive optimizations
- Advanced content filtering and ML recommendations
- Real-time sync capabilities
- Enhanced offline PWA features

## Support

For development questions or issues, check the Django admin interface and logs for debugging information.
