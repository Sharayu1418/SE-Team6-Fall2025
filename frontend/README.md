<<<<<<< HEAD
# SmartCache AI - React Frontend

A modern React frontend for SmartCache AI, providing an intuitive interface for content discovery and management using AI agents.

## Features

- **User Authentication**: Session-based authentication with Django backend
- **User Registration**: Sign up with personalized content preferences
- **Agent Execution**: Trigger RoundRobinGroupChat agents via WebSocket for real-time content discovery
- **Downloads Management**: View, filter, and download content items
- **Preferences Management**: Customize topics, daily limits, and storage constraints
- **Real-time Updates**: WebSocket integration for live agent activity monitoring

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **WebSocket** - Real-time communication with Django Channels

## Prerequisites

- Node.js 16+ and npm
- Django backend running on `http://localhost:8000`
- Redis server running (for Django Channels)

## Installation

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Ensure the Django backend is running:

```bash
# From project root
python manage.py runserver
```

3. Ensure Redis is running:

```bash
redis-server
```

4. Ensure Celery is running (for background downloads):

```bash
# From project root
celery -A smartcache worker --loglevel=info
```

## Development

Start the Vite development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### Proxy Configuration

Vite is configured to proxy requests:
- `/api/*` → `http://localhost:8000/api/*` (REST API)
- `/ws/*` → `ws://localhost:8000/ws/*` (WebSocket)

This allows the frontend to communicate with the Django backend without CORS issues during development.

## Build

Create a production build:

```bash
npm run build
```

The build artifacts will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # Axios instance with CSRF handling
│   ├── components/
│   │   ├── AgentExecutor.jsx  # WebSocket agent execution UI
│   │   ├── Layout.jsx         # App layout with navigation
│   │   └── ProtectedRoute.jsx # Route guard component
│   ├── hooks/
│   │   ├── useAuth.js         # Authentication hook
│   │   └── useWebSocket.js    # WebSocket connection hook
│   ├── pages/
│   │   ├── Dashboard.jsx      # Main dashboard with stats
│   │   ├── Downloads.jsx      # Downloads list and management
│   │   ├── Login.jsx          # Login page
│   │   ├── Preferences.jsx    # User preferences editor
│   │   └── Register.jsx       # Registration with preferences
│   ├── store/
│   │   └── authStore.js       # Zustand auth state store
│   ├── App.jsx                # Main app with routing
│   ├── index.css              # Tailwind CSS imports
│   └── main.jsx               # App entry point
├── public/
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

## Key Components

### AgentExecutor

The `AgentExecutor` component provides the interface for triggering the multi-agent system:

- Connect to WebSocket at `/ws/agents/`
- Send trigger message with `max_items` parameter
- Display real-time agent messages
- Show download queue status
- Display execution summary

### Authentication Flow

1. **Login**: POST to `/api/auth/login/` with credentials
2. **Register**: POST to `/api/auth/register/` with user data and preferences
3. **Session**: Django session cookies are automatically included in requests
4. **Current User**: GET `/api/auth/me/` to fetch authenticated user data

### WebSocket Integration

The WebSocket connection at `/ws/agents/` supports:

**Client → Server Messages:**
```json
{
  "type": "trigger_agents",
  "max_items": 5
}
```

**Server → Client Messages:**
- `connection_established`: Connection successful
- `execution_started`: Agent execution began
- `agent_message`: Agent activity update
- `download_queued`: Item added to download queue
- `execution_complete`: All agents finished (includes summary)
- `error`: Error occurred

## API Endpoints Used

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/me/` - Get current user
- `GET /api/preferences/` - Get user preferences
- `PATCH /api/preferences/:id/` - Update preferences
- `GET /api/downloads/` - Get user downloads
- `GET /api/downloads/:id/file/` - Download file
- `WS /ws/agents/` - WebSocket for agent execution

## Environment Variables

No environment variables required for development. The Vite proxy handles backend communication.

For production, you may need to configure:
- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL

## Troubleshooting

### CSRF Token Issues

If you encounter CSRF errors:
1. Ensure cookies are being sent (`withCredentials: true`)
2. Check that `CSRF_TRUSTED_ORIGINS` in Django settings includes `http://localhost:5173`
3. Verify the CSRF token is being read from cookies correctly

### WebSocket Connection Issues

1. Ensure Redis is running
2. Verify Django Channels is properly configured
3. Check that Daphne is serving the ASGI application
4. Confirm user is authenticated before connecting

### Download Not Starting

1. Ensure Celery worker is running
2. Check that `AUTO_PROCESS_DOWNLOADS=True` in Django settings
3. Verify Django signals are registered (check `core/apps.py`)

## License

This project is part of the SmartCache AI system.
=======
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
>>>>>>> 820001f5a3b6155cab5c38c4b8560f46ac27405e
