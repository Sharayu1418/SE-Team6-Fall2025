# 🎉 SmartCache AI - Getting Started

## ✅ Setup Complete!

Your SmartCache AI project is fully configured and ready to use!

---

## 📦 What's Been Set Up

### 1. Python Environment
- ✅ Python 3.13.9 installed
- ✅ Virtual environment created (`venv/`)
- ✅ All 73 dependencies installed (Django, AutoGen, Ollama, Celery, etc.)

### 2. Database
- ✅ SQLite database created
- ✅ 19 migrations applied
- ✅ 6 models configured:
  - `UserPreference` - User settings
  - `CommuteWindow` - Scheduled content preparation times
  - `ContentSource` - RSS feeds (20 sources loaded)
  - `ContentItem` - Individual content entries
  - `Subscription` - User-to-source relationships
  - `DownloadItem` - Prepared content for users
  - `EventLog` - User activity tracking

### 3. Content Sources
- ✅ 20 content sources loaded with real RSS feeds
- ✅ **Podcasts**: NPR News Now, The Daily (NYT), TED Talks Daily, BBC, Radiolab, Science Vs, etc.
- ✅ **News**: Reuters, The Guardian, BBC World News
- ✅ **Tech**: Hacker News, Ars Technica, TechCrunch, Wired
- ✅ **Science**: NASA, Scientific American

### 4. ETL Pipeline
- ✅ Content ingestion service configured
- ✅ Successfully tested (14 items ingested from NPR)
- ✅ Storage provider set to `none` (local development mode)

### 5. Configuration Files
- ✅ `.env` created with development settings
- ✅ Environment variables loaded
- ✅ Settings configured for local development

---

## 🚀 Quick Start Commands

### 1. Activate Virtual Environment (Do this FIRST every time!)
```bash
cd /Users/khushaliiishahh/Downloads/SE-Team6-Fall2025-anitej-etl-pipeline
source venv/bin/activate
```

Your prompt will show `(venv)` when activated.

### 2. Create Admin Account
```bash
python manage.py createsuperuser
```

### 3. Run the Development Server
```bash
python manage.py runserver
```

Then visit:
- **Homepage**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

---

## 📊 Using the ETL Pipeline

### Ingest Content from All Sources
```bash
python manage.py run_etl
```

Expected output:
```
✓ NPR News Now: 4 new items
✓ TED Talks Daily: 5 new items
✓ Hacker News Frontpage: 10 new items
...
Total: 87 new items from 20 source(s)
```

### Ingest from Specific Source
```bash
# By source ID
python manage.py run_etl --source 1

# By source name (partial match)
python manage.py run_etl --source-name "TED"
```

### View Ingested Content
```bash
python manage.py shell
```

```python
from core.models import ContentItem, ContentSource

# Count total items
print(f"Total content items: {ContentItem.objects.count()}")

# View latest 10 items
for item in ContentItem.objects.order_by('-discovered_at')[:10]:
    print(f"- {item.title}")
    print(f"  Source: {item.source.name}")
    print(f"  Published: {item.published_at}")
    print()

# View all sources
for source in ContentSource.objects.filter(is_active=True):
    item_count = source.contentitem_set.count()
    print(f"{source.name}: {item_count} items")
```

---

## 🤖 Using AutoGen Agents (Optional)

The AutoGen multi-agent system requires Ollama (a local LLM server).

### Step 1: Install Ollama
```bash
# Install via Homebrew
brew install ollama

# Or download from https://ollama.com/download
```

### Step 2: Start Ollama Server
```bash
# In a separate terminal
ollama serve
```

### Step 3: Download the llama3 Model
```bash
ollama pull llama3
```

This downloads a ~4GB model. It may take a few minutes.

### Step 4: Test AutoGen Agents
```bash
python manage.py shell
```

```python
from core.autogen_main import run_content_pipeline, run_discovery_task

# Example 1: Discovery task
result = run_discovery_task(user_id=1, content_type="podcast")
print(result)

# Example 2: Custom task
result = run_content_pipeline(
    user_id=1,
    task="Show me the latest tech podcasts and recommend 3 for download"
)
print(result)
```

**What the agents do:**
1. **Discovery Agent** - Finds and recommends content based on your subscriptions
2. **Download Agent** - Queues content for download
3. **Summarizer Agent** - Analyzes content quality (skeleton in Sprint 1)

---

## 🗂️ Project Structure

```
SE-Team6-Fall2025-anitej-etl-pipeline/
├── core/                          # Main Django app
│   ├── models.py                  # Database models
│   ├── views.py                   # Web views and API endpoints
│   ├── agents/                    # AutoGen agent definitions
│   │   ├── definitions.py         # Agent system messages and configs
│   │   └── groupchat.py           # Agent chat coordination
│   ├── tools/                     # Agent tools/functions
│   │   ├── content_discovery.py   # Discovery tools
│   │   ├── content_download.py    # Download tools
│   │   ├── content_recommendation.py  # Recommendation tools
│   │   └── llm_tools.py           # LLM-based tools
│   ├── services/                  # Low-level services
│   │   ├── content_ingestion.py   # ETL pipeline
│   │   ├── ollama_client.py       # Ollama LLM client
│   │   └── storage_service.py     # S3/Supabase storage
│   ├── management/commands/
│   │   ├── run_etl.py             # ETL management command
│   │   └── seed_defaults.py       # Seed sample data
│   └── autogen_main.py            # AutoGen entry point
├── smartcache/                    # Django project settings
│   ├── settings.py                # Configuration
│   ├── urls.py                    # URL routing
│   └── celery.py                  # Celery config
├── templates/                     # HTML templates
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (created)
├── db.sqlite3                     # SQLite database
└── manage.py                      # Django management CLI
```

---

## 📝 Environment Variables Explained

Your `.env` file contains:

```bash
# Django
SECRET_KEY=dev-secret-key-change-in-production-12345678
DEBUG=True

# Storage Provider
STORAGE_PROVIDER=none  # Options: 'aws_s3', 'supabase', 'none'
```

### Storage Options:

#### Option 1: Local Development (Current)
```bash
STORAGE_PROVIDER=none
```
- ✅ No cloud credentials needed
- ✅ Great for testing
- ⚠️ Media files are NOT downloaded or stored
- ⚠️ Only metadata (title, description, URLs) is saved

#### Option 2: AWS S3 (Production)
```bash
STORAGE_PROVIDER=aws_s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET_NAME=smartcache-media
AWS_REGION=us-east-1
```
- ✅ Downloads and stores podcast/video files
- ✅ Provides storage URLs for offline access
- 💰 Requires AWS account

#### Option 3: Supabase Storage (Alternative)
```bash
STORAGE_PROVIDER=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=media
```
- ✅ Downloads and stores files
- ✅ Free tier available
- 💰 Requires Supabase account

---

## 🔄 Daily Workflow

### Starting Your Day
```bash
# 1. Navigate to project
cd /Users/khushaliiishahh/Downloads/SE-Team6-Fall2025-anitej-etl-pipeline

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run server
python manage.py runserver
```

### Running ETL Pipeline
```bash
# Fetch new content from all sources
python manage.py run_etl

# Or ingest specific sources
python manage.py run_etl --source-name "NPR"
```

### Using AutoGen Agents (If Ollama is running)
```bash
# Start Ollama in background (one-time per session)
ollama serve &

# Open Django shell
python manage.py shell
```

```python
from core.autogen_main import run_content_pipeline

result = run_content_pipeline(
    user_id=1,
    task="Find me tech podcasts and download the latest episodes"
)
print(result)
```

---

## 🎯 Next Steps

### 1. Create Your Admin Account
```bash
python manage.py createsuperuser
```

### 2. Explore the Admin Panel
- Visit http://localhost:8000/admin
- View ContentSources, ContentItems, etc.
- Create test users, subscriptions

### 3. Run the ETL Pipeline
```bash
python manage.py run_etl
```

### 4. Test the Web Interface
- Homepage: http://localhost:8000
- Sources: http://localhost:8000/sources/
- Downloads: http://localhost:8000/downloads/
- Commutes: http://localhost:8000/commutes/

### 5. (Optional) Set Up Ollama for AutoGen
- Install: `brew install ollama`
- Start: `ollama serve`
- Pull model: `ollama pull llama3`
- Test agents: See [ETL_PIPELINE_GUIDE.md](./ETL_PIPELINE_GUIDE.md)

### 6. (Optional) Set Up Cloud Storage
- See `.env.example` for AWS S3 or Supabase configuration
- Update `.env` with your credentials
- Run ETL with storage: `python manage.py run_etl`

---

## 📚 Documentation Files

- **QUICK_START.md** - Quick reference guide
- **SETUP_GUIDE.md** - Detailed setup instructions
- **ETL_PIPELINE_GUIDE.md** - Complete ETL and AutoGen guide
- **PACKAGE_MANAGEMENT.md** - How to add new packages
- **GETTING_STARTED.md** - This file

---

## 🐛 Troubleshooting

### Virtual Environment Not Activated
**Symptom:** `ModuleNotFoundError` or wrong Python version

**Solution:**
```bash
source venv/bin/activate
python --version  # Should show Python 3.13.9
```

### Database Errors
**Symptom:** `no such table` errors

**Solution:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Ollama Connection Error
**Symptom:** `Failed to connect to Ollama`

**Solution:**
```bash
# Start Ollama
ollama serve

# In another terminal, test it
curl http://localhost:11434/api/tags
```

### Port Already in Use
**Symptom:** `Error: That port is already in use`

**Solution:**
```bash
# Use a different port
python manage.py runserver 8080

# Or find and kill the process
lsof -ti:8000 | xargs kill -9
```

---

## ✅ Verification Checklist

- [ ] Virtual environment activates successfully
- [ ] `python --version` shows Python 3.13.9
- [ ] `python manage.py check` passes with no errors
- [ ] Admin panel loads at http://localhost:8000/admin
- [ ] ETL pipeline runs: `python manage.py run_etl`
- [ ] Content items are visible in Django shell
- [ ] (Optional) Ollama is running and agents work

---

## 🎉 You're All Set!

Your SmartCache AI project is fully configured and ready for development!

**First command to run:**
```bash
python manage.py createsuperuser
```

**Then start the server:**
```bash
python manage.py runserver
```

**Happy coding!** 🚀

---

*For detailed information, see `ETL_PIPELINE_GUIDE.md`*
*Last updated: November 4, 2025*

