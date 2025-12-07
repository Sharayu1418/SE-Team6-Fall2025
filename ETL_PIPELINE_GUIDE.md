# 🚀 SmartCache AI - ETL Pipeline & AutoGen Agents Guide

## Overview

This project has **two main systems**:

1. **ETL Pipeline** - Traditional data pipeline that fetches RSS feeds
2. **AutoGen Multi-Agent System** - AI agents for intelligent content management

---

## 📋 Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Running the ETL Pipeline](#2-running-the-etl-pipeline)
3. [Setting Up Ollama (for AutoGen)](#3-setting-up-ollama)
4. [Running AutoGen Agents](#4-running-autogen-agents)
5. [Cloud Storage Setup (Optional)](#5-cloud-storage-setup-optional)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Environment Setup

### Step 1.1: Create Environment File

The `.env` file has been created for you with local development defaults.

```bash
# Verify .env exists
cat .env
```

**Key Settings:**
- `STORAGE_PROVIDER=none` - No cloud storage (good for local testing)
- `OLLAMA_BASE_URL=http://localhost:11434` - Local Ollama server
- `OLLAMA_MODEL=llama3` - Default LLM model

### Step 1.2: Activate Virtual Environment

```bash
cd /Users/khushaliiishahh/Downloads/SE-Team6-Fall2025-anitej-etl-pipeline
source venv/bin/activate
```

---

## 2. Running the ETL Pipeline

The ETL pipeline fetches content from RSS feeds and stores it in the database.

### 2.1: Test the Pipeline (Without Cloud Storage)

```bash
# Ingest content from all active sources
python manage.py run_etl

# Ingest from a specific source by ID
python manage.py run_etl --source 1

# Ingest from sources matching a name
python manage.py run_etl --source-name "NPR"
```

**What happens:**
1. ✅ Fetches RSS feeds from 20 pre-configured sources
2. ✅ Parses entries (title, description, media URL)
3. ✅ Creates `ContentItem` records in the database
4. ⚠️ Skips media download (because STORAGE_PROVIDER=none)

**Expected Output:**
```
🔄 Starting ETL pipeline for 20 active source(s)...

✓ NPR News Now: 5 new items
✓ TED Talks Daily: 3 new items
✓ Hacker News Frontpage: 10 new items
...

============================================================
ETL Pipeline Complete
============================================================
Sources Processed: 20
Total New Items: 87
Errors: 0
```

### 2.2: View Ingested Content

```bash
# Open Django shell
python manage.py shell
```

```python
from core.models import ContentItem

# Count total items
print(f"Total content items: {ContentItem.objects.count()}")

# View latest items
for item in ContentItem.objects.all()[:5]:
    print(f"- {item.title} (Source: {item.source.name})")
```

### 2.3: Set Up Automated ETL (Optional)

Use Celery to run the ETL pipeline automatically:

```bash
# Terminal 1: Start Celery worker
celery -A smartcache worker --loglevel=info

# Terminal 2: Start Celery beat (scheduler)
celery -A smartcache beat --loglevel=info
```

**Note:** Requires Redis:
```bash
brew install redis
brew services start redis
```

---

## 3. Setting Up Ollama

Ollama is required for the **AutoGen agents** to work.

### 3.1: Install Ollama

```bash
# Install via Homebrew
brew install ollama
```

Or download from: https://ollama.com/download

### 3.2: Start Ollama Server

```bash
# Start Ollama (in a separate terminal or background)
ollama serve
```

This starts the Ollama API server on `http://localhost:11434`

### 3.3: Download the llama3 Model

```bash
# Pull the model (this may take a few minutes)
ollama pull llama3

# Verify it's working
ollama run llama3 "Hello, world!"
```

**Alternative Models:**
```bash
ollama pull llama3.1    # Larger, more capable
ollama pull mistral     # Faster, smaller
ollama pull codellama   # Better for code tasks
```

To use a different model, update `.env`:
```bash
OLLAMA_MODEL=llama3.1
```

### 3.4: Verify Ollama is Running

```bash
# Test the API
curl http://localhost:11434/api/tags
```

Should return JSON with available models.

---

## 4. Running AutoGen Agents

The AutoGen system consists of 3 AI agents:

1. **Content Discovery Agent** - Recommends content based on preferences
2. **Content Download Agent** - Queues downloads
3. **Content Summarizer Agent** - Analyzes content quality (skeleton)

### 4.1: Test from Django Shell

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
    task="Show me my top 5 recommended podcasts and queue them for download"
)
print(result)
```

### 4.2: What the Agents Do

**Workflow Example:**

1. **User**: "Find me tech podcasts and download the latest episodes"

2. **Discovery Agent** calls:
   ```python
   discover_new_sources(content_type="podcast")
   get_user_subscriptions_info(user_id=1)
   recommend_content_for_download(user_id=1, max_items=5)
   ```
   Returns: Content IDs [123, 124, 125]

3. **Download Agent** calls:
   ```python
   queue_download(user_id=1, content_item_id=123)
   queue_download(user_id=1, content_item_id=124)
   queue_download(user_id=1, content_item_id=125)
   ```
   
4. **Result**: 3 items queued for download

### 4.3: Test Individual Tools

```python
# Test discovery tools
from core.tools.content_discovery import discover_new_sources, get_user_subscriptions_info

sources = discover_new_sources(content_type="podcast")
print(sources)

# Test download tools
from core.tools.content_download import queue_download

result = queue_download(user_id=1, content_item_id=123)
print(result)
```

### 4.4: Run Standalone AutoGen Script

```bash
# Run the example script
python core/autogen_main.py
```

This will:
- ✅ Set up Django
- ✅ Initialize agents
- ✅ Run example discovery tasks
- ✅ Display agent conversations

---

## 5. Cloud Storage Setup (Optional)

For production or to test media caching, configure cloud storage.

### Option A: AWS S3

1. **Create S3 Bucket**:
   - Go to https://console.aws.amazon.com/s3/
   - Create bucket: `smartcache-media`
   - Region: `us-east-1`

2. **Create IAM User**:
   - Go to https://console.aws.amazon.com/iam/
   - Create user with S3 permissions
   - Save Access Key ID and Secret Key

3. **Update `.env`**:
   ```bash
   STORAGE_PROVIDER=aws_s3
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_S3_BUCKET_NAME=smartcache-media
   AWS_REGION=us-east-1
   ```

4. **Run ETL with Storage**:
   ```bash
   python manage.py run_etl --provider aws_s3
   ```

### Option B: Supabase

1. **Create Supabase Project**:
   - Go to https://app.supabase.com/
   - Create new project
   - Go to Settings → API

2. **Create Storage Bucket**:
   - Go to Storage
   - Create bucket: `media`
   - Set to public or private

3. **Update `.env`**:
   ```bash
   STORAGE_PROVIDER=supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_BUCKET=media
   ```

4. **Run ETL with Storage**:
   ```bash
   python manage.py run_etl --provider supabase
   ```

---

## 6. Troubleshooting

### Problem: Ollama Connection Error

```
Error: Failed to connect to Ollama at http://localhost:11434
```

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# In another terminal, pull the model
ollama pull llama3
```

### Problem: No Content Items Found

```
Warning: No entries found in feed
```

**Solution:**
- Check internet connection
- Verify RSS feeds are active:
  ```python
  from core.models import ContentSource
  for source in ContentSource.objects.filter(is_active=True)[:3]:
      print(f"{source.name}: {source.feed_url}")
  ```

### Problem: Storage Upload Fails

```
Failed to initialize storage service
```

**Solution:**
- For local testing, use `STORAGE_PROVIDER=none`
- For cloud storage, verify credentials:
  ```bash
  # Test AWS credentials
  aws s3 ls

  # Test Supabase
  curl https://your-project.supabase.co/storage/v1/bucket
  ```

### Problem: Agent Not Responding

```
Agent conversation stuck or no response
```

**Solution:**
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Verify model is downloaded: `ollama list`
3. Check logs: `tail -f logs/django.log`
4. Try simpler task: `run_discovery_task(user_id=1)`

### Problem: Redis Connection Error

```
Error: Redis connection refused
```

**Solution:**
```bash
# Start Redis
brew services start redis

# Or run manually
redis-server
```

---

## 🎯 Complete End-to-End Test

Here's a complete workflow to test everything:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Create a superuser (if not done)
python manage.py createsuperuser

# 3. Run ETL pipeline
python manage.py run_etl

# 4. Start Django server (Terminal 1)
python manage.py runserver

# 5. Start Ollama (Terminal 2)
ollama serve

# 6. Test AutoGen (Terminal 3)
python manage.py shell
```

```python
# In Django shell:
from core.autogen_main import run_content_pipeline

# Run a complete task
result = run_content_pipeline(
    user_id=1,
    task="Find me 3 tech podcasts, queue them for download, and summarize them"
)
print(result)
```

**Expected Result:**
- ✅ Discovery Agent finds content
- ✅ Download Agent queues 3 items
- ✅ Summarizer Agent analyzes (stub in Sprint 1)
- ✅ Conversation completes with summary

---

## 📚 Additional Resources

- **AutoGen Documentation**: https://microsoft.github.io/autogen/
- **Ollama Documentation**: https://ollama.com/docs
- **Django Celery**: https://docs.celeryproject.org/en/stable/django/
- **RSS Feed Parser**: https://feedparser.readthedocs.io/

---

## 🔄 Daily Workflow

```bash
# 1. Start your day
cd /Users/khushaliiishahh/Downloads/SE-Team6-Fall2025-anitej-etl-pipeline
source venv/bin/activate

# 2. Start Ollama (if using AutoGen)
ollama serve &

# 3. Run Django server
python manage.py runserver

# 4. Run ETL (manually or via Celery)
python manage.py run_etl

# 5. Test agents
python manage.py shell
```

---

*Last updated: November 4, 2025*

