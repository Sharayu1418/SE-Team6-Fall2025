# SmartCache AI

**Intelligent Offline Content Curator for Commuters**

SmartCache AI is a full-stack web application that automatically curates podcasts, articles, videos, and news based on user preferences and commute schedules. The system uses a multi-agent AI architecture powered by AutoGen and Ollama to discover, recommend, and download content for offline consumption.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Architecture](#architecture)
   - [High-Level System Architecture](#high-level-system-architecture)
   - [Component Interaction Flow](#component-interaction-flow)
5. [ETL Pipeline Architecture](#etl-pipeline-architecture)
   - [ETL Pipeline Flow Diagram](#etl-pipeline-flow-diagram)
   - [ETL Source Type Handlers](#etl-source-type-handlers)
   - [ETL Celery Tasks](#etl-celery-tasks)
6. [AI Multi-Agent Architecture](#ai-multi-agent-architecture)
   - [Agent Team Architecture](#agent-team-architecture)
   - [Agent Execution Sequence](#agent-execution-sequence)
7. [Prerequisites](#prerequisites)
8. [Installation](#installation)
   - [Option 1: Local Development Setup](#option-1-local-development-setup)
   - [Option 2: Docker Setup](#option-2-docker-setup)
9. [Running the Application](#running-the-application)
10. [Project Structure](#project-structure)
11. [Database Models](#database-models)
12. [API Reference](#api-reference)
13. [WebSocket Integration](#websocket-integration)
14. [AI Agent System](#ai-agent-system)
15. [Data Flow Diagrams](#data-flow-diagrams)
16. [Environment Variables](#environment-variables)
17. [Troubleshooting](#troubleshooting)
---

## Overview

SmartCache AI helps users prepare personalized offline content for their daily commutes. The system:

- Discovers content from various sources (podcasts, news articles, videos, memes)
- Uses AI agents to recommend content based on user preferences
- Downloads and caches content for offline access
- Provides real-time updates via WebSocket during content discovery
- Supports cloud storage integration (AWS S3, Supabase)

---

## Features

### Core Features

- **User Authentication**: Session-based authentication with registration and login
- **Commute Windows**: Define when you need content ready (e.g., Mon-Fri 8-9 AM)
- **Content Sources**: Subscribe to podcasts, articles, videos, and news feeds
- **Download Management**: Track content preparation and download status
- **User Preferences**: Customize topics, daily limits, and storage constraints

### AI-Powered Features

- **Multi-Agent System**: AutoGen-based agents for content discovery and management
- **Content Discovery Agent**: Finds and recommends content based on subscriptions
- **Download Agent**: Manages download queues and file processing
- **Summarizer Agent**: Assesses content quality (in development)
- **Real-time Execution**: Watch agent activity live via WebSocket

### Technical Features

- **Automated Scheduling**: Celery-based background task processing
- **Cloud Storage**: AWS S3 and Supabase integration for media storage
- **PWA Ready**: Service worker and manifest for offline capability
- **REST API**: Full CRUD operations for all resources
- **Admin Interface**: Django admin panel for content management

---

## Tech Stack

### Backend

| Component | Technology |
|-----------|------------|
| Framework | Django 5.1 |
| REST API | Django REST Framework |
| WebSocket | Django Channels |
| Task Queue | Celery |
| Message Broker | Redis |
| ASGI Server | Daphne |
| Database | PostgreSQL (SQLite for development) |

### Frontend

| Component | Technology |
|-----------|------------|
| Framework | React 19 |
| Build Tool | Vite 7 |
| Routing | React Router 7 |
| State Management | Zustand |
| HTTP Client | Axios |
| Styling | Tailwind CSS |

### AI/ML

| Component | Technology |
|-----------|------------|
| Agent Framework | AutoGen (pyautogen 0.4+) |
| LLM Backend | Ollama (local LLM server) |
| Default Model | Llama 3.1 |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Containerization | Docker + Docker Compose |
| Static Files | Whitenoise |
| Cloud Storage | AWS S3 / Supabase |

---

## Architecture

### High-Level System Architecture

```
+-----------------------------------------------------------------------------------+
|                                   CLIENT LAYER                                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|    +-------------------------+              +---------------------------+         |
|    |    React Frontend       |              |    Django Admin Panel     |         |
|    |    (Vite + Tailwind)    |              |    /admin/                |         |
|    |    localhost:5173       |              |    localhost:8000/admin   |         |
|    +------------+------------+              +-------------+-------------+         |
|                 |                                         |                       |
|                 |  HTTP REST API                          |                       |
|                 |  WebSocket (ws://...)                   |                       |
|                 |                                         |                       |
+-----------------------------------------------------------------------------------+
                  |                                         |
                  v                                         v
+-----------------------------------------------------------------------------------+
|                                APPLICATION LAYER                                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|    +-------------------------------------------------------------------------+   |
|    |                     Django Backend (Daphne ASGI)                        |   |
|    |                         localhost:8000                                  |   |
|    +-------------------------------------------------------------------------+   |
|    |                                                                         |   |
|    |   +-------------------+   +-------------------+   +------------------+  |   |
|    |   |   REST API        |   |   WebSocket       |   |   Django Views   |  |   |
|    |   |   /api/*          |   |   /ws/agents/     |   |   Templates      |  |   |
|    |   |   DRF ViewSets    |   |   Channels        |   |   Admin          |  |   |
|    |   +-------------------+   +-------------------+   +------------------+  |   |
|    |                                                                         |   |
|    |   +-------------------+   +-------------------+   +------------------+  |   |
|    |   |   Authentication  |   |   Serializers     |   |   Signals        |  |   |
|    |   |   Session-based   |   |   JSON transform  |   |   Auto-triggers  |  |   |
|    |   +-------------------+   +-------------------+   +------------------+  |   |
|    |                                                                         |   |
|    +-------------------------------------------------------------------------+   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
                  |                           |                       |
                  v                           v                       v
+-----------------------------------------------------------------------------------+
|                                  SERVICE LAYER                                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   +------------------------+  +------------------------+  +--------------------+ |
|   |   AI Agent System      |  |   ETL Pipeline         |  |   Download Service | |
|   |                        |  |                        |  |                    | |
|   |   - Discovery Agent    |  |   - RSS Feed Parser    |  |   - Queue Manager  | |
|   |   - Download Agent     |  |   - YouTube Ingester   |  |   - File Downloader| |
|   |   - Summarizer Agent   |  |   - News API Client    |  |   - Status Tracker | |
|   |   - AutoGen Teams      |  |   - Meme API Client    |  |                    | |
|   |                        |  |   - Media Uploader     |  |                    | |
|   +----------+-------------+  +----------+-------------+  +---------+----------+ |
|              |                           |                          |            |
+-----------------------------------------------------------------------------------+
               |                           |                          |
               v                           v                          v
+-----------------------------------------------------------------------------------+
|                               INFRASTRUCTURE LAYER                                 |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   +------------------+  +------------------+  +------------------+                |
|   |                  |  |                  |  |                  |                |
|   |   Ollama LLM     |  |   Redis          |  |   Celery         |                |
|   |   localhost:11434|  |   localhost:6379 |  |   Worker/Beat    |                |
|   |                  |  |                  |  |                  |                |
|   |   Models:        |  |   - Message      |  |   - Background   |                |
|   |   - llama3.1     |  |     Broker       |  |     Tasks        |                |
|   |   - mistral      |  |   - Channel      |  |   - Scheduled    |                |
|   |   - codellama    |  |     Layer        |  |     Jobs         |                |
|   |                  |  |   - Cache        |  |                  |                |
|   +------------------+  +------------------+  +------------------+                |
|                                                                                   |
+-----------------------------------------------------------------------------------+
               |                           |                          |
               v                           v                          v
+-----------------------------------------------------------------------------------+
|                                  DATA LAYER                                        |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   +------------------+       +------------------+       +---------------------+   |
|   |                  |       |                  |       |                     |   |
|   |   PostgreSQL     |       |   AWS S3         |       |   Local Filesystem  |   |
|   |   (Production)   |       |   Supabase       |       |   /media/downloads/ |   |
|   |                  |       |                  |       |                     |   |
|   |   SQLite         |       |   Cloud Media    |       |   Cached Files      |   |
|   |   (Development)  |       |   Storage        |       |   for Offline Use   |   |
|   |                  |       |                  |       |                     |   |
|   +------------------+       +------------------+       +---------------------+   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### Component Interaction Flow

```
User Request Flow:
==================

[User] --> [React Frontend] --> [Django REST API] --> [Database]
                |                       |
                |                       +--> [Celery Task] --> [Redis] --> [Worker]
                |                                                              |
                +--(WebSocket)--------> [Django Channels] <--------------------+
                                              |
                                              +--> Real-time Updates to Frontend


AI Agent Flow:
==============

[User clicks "Discover Content"]
         |
         v
[WebSocket Connection] --> [AgentExecutionConsumer]
         |
         v
[Create Agent Team] --> [RoundRobinGroupChat / SelectorGroupChat]
         |
         +---> [Discovery Agent] ---> Ollama LLM ---> recommend_content_for_download()
         |            |
         |            v
         +---> [Download Agent] ---> queue_download() ---> Celery Task
         |            |
         |            v
         +---> [Summarizer Agent] ---> assess_quality() ---> Update ContentItem
         |
         v
[WebSocket sends real-time updates to frontend]
         |
         v
[Download complete notification triggers auto-download in browser]
```

---

## ETL Pipeline Architecture

The ETL (Extract, Transform, Load) pipeline is responsible for fetching content from external sources
and populating the content pool. This runs independently of the AI agents as a scheduled background job.

### ETL Pipeline Flow Diagram

```
+-----------------------------------------------------------------------------------+
|                              ETL PIPELINE OVERVIEW                                 |
+-----------------------------------------------------------------------------------+

                           TRIGGER MECHANISMS
                           ==================
     +----------------+    +----------------+    +------------------+
     | Celery Beat    |    | Manual API     |    | Management       |
     | (Hourly)       |    | POST /api/etl/ |    | Command          |
     | Scheduled      |    | trigger/       |    | run_etl          |
     +-------+--------+    +-------+--------+    +--------+---------+
             |                     |                      |
             +---------------------+----------------------+
                                   |
                                   v
+-----------------------------------------------------------------------------------+
|                                  EXTRACT PHASE                                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   ContentSource.objects.filter(is_active=True)                                    |
|                                                                                   |
|   For each source, route to appropriate extractor:                                |
|                                                                                   |
|   +------------------+  +------------------+  +------------------+  +------------+|
|   | RSS Feed Parser  |  | YouTube         |  | NewsAPI          |  | Meme API   ||
|   | (feedparser)     |  | (yt-dlp)        |  | (requests)       |  | (requests) ||
|   |                  |  |                  |  |                  |  |            ||
|   | - Podcasts       |  | - Channels       |  | - Top headlines  |  | - r/memes  ||
|   | - Articles       |  | - Playlists      |  | - Topic search   |  | - r/dank   ||
|   | - Blogs          |  | - Search results |  | - Breaking news  |  | - Custom   ||
|   +--------+---------+  +--------+---------+  +--------+---------+  +-----+------+|
|            |                     |                     |                  |       |
+-----------------------------------------------------------------------------------+
             |                     |                     |                  |
             v                     v                     v                  v
+-----------------------------------------------------------------------------------+
|                                TRANSFORM PHASE                                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   For each extracted item:                                                        |
|                                                                                   |
|   1. Parse metadata (title, description, URL, publish date)                       |
|   2. Generate unique GUID (hash of URL or RSS GUID)                               |
|   3. Check for duplicates: ContentItem.objects.filter(guid=guid).exists()         |
|   4. Extract media URL from enclosures or media:content tags                      |
|   5. Download media file to temporary storage (if cache_allowed policy)           |
|   6. Generate storage object key: {type}s/{source_slug}/{guid}.{ext}              |
|                                                                                   |
|   +-------------------------------------------------------------------------+     |
|   |                     DATA TRANSFORMATION                                 |     |
|   +-------------------------------------------------------------------------+     |
|   |                                                                         |     |
|   |   Raw Feed Entry                    Transformed ContentItem             |     |
|   |   ===============                   =====================               |     |
|   |                                                                         |     |
|   |   entry.title        -->            title (max 500 chars)               |     |
|   |   entry.summary      -->            description (max 2000 chars)        |     |
|   |   entry.link         -->            url                                 |     |
|   |   entry.guid         -->            guid (unique identifier)            |     |
|   |   entry.published    -->            published_at (timezone aware)       |     |
|   |   entry.enclosures   -->            media_url                           |     |
|   |   [downloaded file]  -->            storage_url (S3/Supabase URL)       |     |
|   |   [file stats]       -->            file_size_bytes                     |     |
|   |                                                                         |     |
|   +-------------------------------------------------------------------------+     |
|                                                                                   |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                                   LOAD PHASE                                       |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   1. Upload media to cloud storage (if cache_allowed):                            |
|                                                                                   |
|      +------------------------+        +------------------------+                 |
|      |      AWS S3            |   OR   |      Supabase          |                 |
|      |      Bucket            |        |      Storage           |                 |
|      +------------------------+        +------------------------+                 |
|      |                        |        |                        |                 |
|      | boto3.upload_file()    |        | supabase.storage       |                 |
|      |                        |        | .upload()              |                 |
|      | Returns:               |        |                        |                 |
|      | https://bucket.s3     |        | Returns:               |                 |
|      | .amazonaws.com/...     |        | https://project        |                 |
|      |                        |        | .supabase.co/...       |                 |
|      +------------------------+        +------------------------+                 |
|                                                                                   |
|   2. Create ContentItem record in database:                                       |
|                                                                                   |
|      ContentItem.objects.create(                                                  |
|          source=source,                                                           |
|          title=item_data['title'],                                                |
|          description=item_data['description'],                                    |
|          url=item_data['url'],                                                    |
|          media_url=item_data['media_url'],                                        |
|          storage_url=storage_url,           # Cloud storage URL                   |
|          storage_provider='aws_s3',         # or 'supabase' or 'none'             |
|          file_size_bytes=file_size_bytes,                                         |
|          published_at=item_data['published_at'],                                  |
|          guid=item_data['guid'],                                                  |
|      )                                                                            |
|                                                                                   |
|   3. Clean up temporary files                                                     |
|                                                                                   |
|   4. Return ingestion statistics                                                  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                              INGESTION RESULTS                                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   {                                                                               |
|       "sources_processed": 7,                                                     |
|       "total_items_added": 45,                                                    |
|       "errors": 0,                                                                |
|       "details": {                                                                |
|           "NPR News Now": 10,                                                     |
|           "TED Talks Daily": 8,                                                   |
|           "Tech News": 12,                                                        |
|           "Memes": 15,                                                            |
|           ...                                                                     |
|       }                                                                           |
|   }                                                                               |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### ETL Source Type Handlers

| Source Type | Handler Method | External API/Tool | Data Extracted |
|-------------|----------------|-------------------|----------------|
| `podcast` | `_ingest_rss_feed()` | feedparser | RSS entries with audio enclosures |
| `article` | `_ingest_rss_feed()` | feedparser | RSS entries with article links |
| `video` | `_ingest_youtube_channel()` | yt-dlp | YouTube video metadata + optional download |
| `meme` | `_ingest_memes()` | meme-api.com | Reddit meme images from subreddits |
| `news` | `_ingest_newsapi()` | NewsAPI.org | Breaking news articles by topic |

### ETL Celery Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `ingest_content_sources` | Every hour (Celery Beat) | Fetch content from all active sources |
| `manual_ingest_source` | On-demand | Ingest a specific source by ID |
| `cleanup_old_content` | Daily | Remove content older than 30 days |
| `download_content_file` | On-demand | Download file from storage to local filesystem |

### Storage Policies

| Policy | Behavior |
|--------|----------|
| `metadata_only` | Store only metadata (title, URL, description). No media download. |
| `cache_allowed` | Download media files and upload to S3/Supabase for offline access. |

---

## AI Multi-Agent Architecture

The AI system uses AutoGen to orchestrate multiple specialized agents working together.

### Agent Team Architecture

```
+-----------------------------------------------------------------------------------+
|                           MULTI-AGENT SYSTEM                                       |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   +-----------------------------------------------------------------------+       |
|   |                    TEAM ORCHESTRATION                                 |       |
|   |              (RoundRobinGroupChat or SelectorGroupChat)               |       |
|   +-----------------------------------------------------------------------+       |
|   |                                                                       |       |
|   |   Team Types:                                                         |       |
|   |   - RoundRobinGroupChat: Agents take turns in fixed order             |       |
|   |   - SelectorGroupChat: LLM selects which agent speaks next            |       |
|   |                                                                       |       |
|   |   Termination: MaxMessageTermination(max_messages=10)                 |       |
|   |                                                                       |       |
|   +-----------------------------------------------------------------------+       |
|                                      |                                            |
|          +---------------------------+---------------------------+                |
|          |                           |                           |                |
|          v                           v                           v                |
|   +---------------+           +---------------+           +---------------+       |
|   |   DISCOVERY   |           |   DOWNLOAD    |           |   SUMMARIZER  |       |
|   |   AGENT       |           |   AGENT       |           |   AGENT       |       |
|   +---------------+           +---------------+           +---------------+       |
|   |               |           |               |           |               |       |
|   | Role:         |           | Role:         |           | Role:         |       |
|   | Find content  |           | Queue and     |           | Assess        |       |
|   | based on user |           | process       |           | quality and   |       |
|   | preferences   |           | downloads     |           | summarize     |       |
|   |               |           |               |           |               |       |
|   | Tools:        |           | Tools:        |           | Tools:        |       |
|   | - discover_   |           | - queue_      |           | - summarize_  |       |
|   |   new_sources |           |   download    |           |   content     |       |
|   | - get_user_   |           | - check_      |           | - assess_     |       |
|   |   subscriptions|          |   download_   |           |   quality     |       |
|   | - recommend_  |           |   status      |           |               |       |
|   |   content     |           | - process_    |           |               |       |
|   | - get_content_|           |   download_   |           |               |       |
|   |   item_details|           |   queue       |           |               |       |
|   |               |           |               |           |               |       |
|   +-------+-------+           +-------+-------+           +-------+-------+       |
|           |                           |                           |               |
|           +---------------------------+---------------------------+               |
|                                       |                                           |
|                                       v                                           |
|                        +------------------------------+                           |
|                        |         OLLAMA LLM           |                           |
|                        |     (OpenAI-compatible)      |                           |
|                        +------------------------------+                           |
|                        |                              |                           |
|                        | Model: llama3.1 (default)    |                           |
|                        | Temperature: 0.7             |                           |
|                        | Capabilities:                |                           |
|                        |   - function_calling: true   |                           |
|                        |   - json_output: true        |                           |
|                        |                              |                           |
|                        +------------------------------+                           |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### Agent Execution Sequence

```
STEP 1: User Triggers Agent Execution
======================================
[Frontend] --> WebSocket --> { "type": "trigger_agents", "max_items": 5 }
                                    |
                                    v
                        [AgentExecutionConsumer]
                                    |
                                    v
                        [Create RoundRobinGroupChat Team]


STEP 2: Discovery Agent Recommends Content
==========================================
[Discovery Agent]
        |
        +--> recommend_content_for_download(user_id=1, max_items=5)
        |           |
        |           v
        |    [Query user subscriptions]
        |    [Query ContentItem pool]
        |    [Filter by user preferences]
        |    [Return top 5 recommendations with Content IDs]
        |
        v
[Agent Output]:
"I found 5 great items for you! Here are my recommendations:
 1. 'How AI Works' from TED Talks (Content ID: 123)
 2. 'Daily News Update' from NPR (Content ID: 124)
 ...
 Download Agent: Please queue Content IDs [123, 124, 125, 126, 127]"


STEP 3: Download Agent Queues Downloads
=======================================
[Download Agent]
        |
        +--> For each Content ID:
        |        queue_download(user_id=1, content_item_id=123)
        |        queue_download(user_id=1, content_item_id=124)
        |        ...
        |
        +--> process_download_queue(user_id=1)
        |           |
        |           v
        |    [Trigger Celery tasks for each queued item]
        |    [download_content_file.delay(download_item_id)]
        |
        v
[Agent Output]:
"Queued 5 items successfully! Download IDs: [501, 502, 503, 504, 505]
 Started 5 background download tasks.
 Files will be downloaded to /media/downloads/user_1/"


STEP 4: Summarizer Agent Assesses Quality
==========================================
[Summarizer Agent]
        |
        +--> assess_quality(content_item_id=123)
        |           |
        |           v
        |    [Analyze content metadata]
        |    [Calculate quality score]
        |    [Update ContentItem.quality_score]
        |
        v
[Agent Output]:
"Quality assessment complete:
 - 'How AI Works': Score 8.5/10 (Highly relevant to user interests)
 - 'Daily News Update': Score 7.2/10 (Good match for news preference)
 ..."


STEP 5: Background Download Processing
=======================================
[Celery Worker]
        |
        +--> download_content_file(download_item_id=501)
        |           |
        |           v
        |    [Fetch from storage_url (S3/Supabase)]
        |    [Stream download to /media/downloads/user_1/]
        |    [Update DownloadItem.status = 'ready']
        |    [Update DownloadItem.local_file_path]
        |
        +--> notify_download_ready(download_item, file_size)
        |           |
        |           v
        |    [WebSocket push to frontend]
        |    { "type": "download_ready", "download_id": 501, ... }
        |
        v
[Frontend auto-downloads file to user's device]
```

---

## Prerequisites

### Required

- **Python 3.11+** (Python 3.13 supported)
- **Node.js 18+** and npm
- **Git**

### Optional (for full functionality)

- **Redis**: Required for Celery background tasks and Django Channels
- **Ollama**: Required for AI agent functionality
- **Docker**: For containerized deployment
- **PostgreSQL**: For production database (SQLite works for development)

---

## Installation

### Option 1: Local Development Setup

#### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/SE-Team6-Fall2025.git
cd SE-Team6-Fall2025
```

#### Step 2: Backend Setup

**Windows (PowerShell):**

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**macOS/Linux (Bash):**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Database Setup

```bash
# Run database migrations
python manage.py migrate

# Load sample content sources
python manage.py seed_defaults

# Create admin superuser
python manage.py createsuperuser
```

#### Step 4: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

#### Step 5: Install Redis (Optional but Recommended)

**Windows:**
Download and install from https://github.com/microsoftarchive/redis/releases

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

#### Step 6: Install Ollama (Optional - for AI Agents)

Download from https://ollama.ai and install for your platform.

```bash
# Pull the default model
ollama pull llama3.1
```

---

### Option 2: Docker Setup

#### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/SE-Team6-Fall2025.git
cd SE-Team6-Fall2025
```

#### Step 2: Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (see Environment Variables section)
```

#### Step 3: Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

This will start:
- **Backend**: Django + Daphne on http://localhost:8000
- **Frontend**: React + Nginx on http://localhost:5173
- **Redis**: Message broker on localhost:6379
- **Celery Worker**: Background task processing

#### Step 4: Initialize Database (First Time Only)

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Load sample data
docker-compose exec backend python manage.py seed_defaults

# Create admin user
docker-compose exec backend python manage.py createsuperuser
```

---

## Running the Application

### Local Development (Full Stack)

You need to run multiple services. Open separate terminal windows for each:

**Terminal 1 - Django Backend:**
```bash
# Activate virtual environment first
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

python manage.py runserver
```

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Redis (if not running as service):**
```bash
redis-server
```

**Terminal 4 - Celery Worker (for background downloads):**
```bash
# Activate virtual environment first
celery -A smartcache worker --loglevel=info
```

**Terminal 5 - Ollama (for AI agents):**
```bash
ollama serve
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| React Frontend | http://localhost:5173 | Main user interface |
| Django Backend | http://localhost:8000 | Backend API |
| Django Admin | http://localhost:8000/admin | Admin panel |
| API Root | http://localhost:8000/api/ | REST API endpoints |

### Minimal Setup (Without AI/Background Tasks)

For basic testing without Redis, Celery, or Ollama:

```bash
# Terminal 1 - Backend
python manage.py runserver

# Terminal 2 - Frontend
cd frontend && npm run dev
```

Note: Background downloads and AI agents will not function without Redis and Ollama.

---

## Project Structure

```
SE-Team6-Fall2025/
|
|-- manage.py                 # Django CLI entry point
|-- requirements.txt          # Python dependencies
|-- docker-compose.yml        # Docker orchestration
|-- Dockerfile                # Backend Docker image
|-- setup.sh                  # Automated setup script (Unix)
|-- db.sqlite3                # SQLite database (development)
|
|-- smartcache/               # Django project configuration
|   |-- settings.py           # Application settings
|   |-- urls.py               # Root URL routing
|   |-- celery.py             # Celery configuration
|   |-- asgi.py               # ASGI application (WebSocket support)
|   |-- wsgi.py               # WSGI application
|
|-- core/                     # Main Django application
|   |-- models.py             # Database models (7 models)
|   |-- views.py              # Views and API endpoints
|   |-- serializers.py        # REST API serializers
|   |-- tasks.py              # Celery background tasks
|   |-- consumers.py          # WebSocket consumers
|   |-- admin.py              # Admin panel configuration
|   |-- signals.py            # Django signals
|   |-- routing.py            # WebSocket routing
|   |-- authentication.py     # Custom authentication
|   |-- pagination.py         # API pagination
|   |
|   |-- agents/               # AutoGen AI agents
|   |   |-- definitions.py    # Agent definitions
|   |   |-- groupchat.py      # Multi-agent orchestration
|   |
|   |-- tools/                # Agent tools (functions)
|   |   |-- content_discovery.py
|   |   |-- content_download.py
|   |   |-- content_recommendation.py
|   |   |-- llm_tools.py
|   |
|   |-- services/             # Business logic services
|   |   |-- content_ingestion.py
|   |   |-- storage_service.py
|   |   |-- ollama_client.py
|   |
|   |-- management/commands/  # Custom Django commands
|       |-- seed_defaults.py
|       |-- run_etl.py
|       |-- add_news_sources.py
|       |-- add_youtube_sources.py
|
|-- frontend/                 # React frontend application
|   |-- package.json          # Node.js dependencies
|   |-- vite.config.js        # Vite configuration
|   |-- tailwind.config.js    # Tailwind CSS configuration
|   |-- Dockerfile            # Frontend Docker image
|   |-- nginx.conf            # Nginx configuration
|   |
|   |-- src/
|       |-- main.jsx          # Application entry point
|       |-- App.jsx           # Main App component with routing
|       |-- index.css         # Global styles (Tailwind)
|       |
|       |-- api/
|       |   |-- client.js     # Axios instance with CSRF handling
|       |
|       |-- components/
|       |   |-- Layout.jsx        # App layout with navigation
|       |   |-- AgentExecutor.jsx # WebSocket agent execution UI
|       |   |-- ProtectedRoute.jsx
|       |
|       |-- pages/
|       |   |-- Dashboard.jsx     # Main dashboard
|       |   |-- Login.jsx         # Login page
|       |   |-- Register.jsx      # Registration with preferences
|       |   |-- Downloads.jsx     # Download management
|       |   |-- Preferences.jsx   # User preferences editor
|       |   |-- Subscriptions.jsx # Subscription management
|       |
|       |-- hooks/
|       |   |-- useAuth.js        # Authentication hook
|       |   |-- useWebSocket.js   # WebSocket connection hook
|       |
|       |-- store/
|           |-- authStore.js      # Zustand auth state
|
|-- templates/                # Django HTML templates (legacy)
|-- static/                   # Static files
|-- content_pool/             # Content collection scripts
|-- downloader_service/       # Microservice for downloads
```

---

## Database Models

### UserPreference

Stores user content preferences.

| Field | Type | Description |
|-------|------|-------------|
| user | OneToOne(User) | Link to Django User |
| topics | JSONField | List of preferred topics |
| max_daily_items | Integer | Maximum items per day (default: 10) |
| max_storage_mb | Integer | Maximum storage in MB (default: 500) |

### CommuteWindow

Defines when users need content ready.

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey(User) | Link to Django User |
| label | CharField | Name (e.g., "Morning Commute") |
| start_time | TimeField | Start time |
| end_time | TimeField | End time |
| days_of_week | JSONField | List of days (e.g., ["Mon", "Tue"]) |
| is_active | Boolean | Whether the window is active |

### ContentSource

Available content sources for subscription.

| Field | Type | Description |
|-------|------|-------------|
| name | CharField | Source name |
| type | CharField | Type: podcast, article, video, meme, news |
| feed_url | URLField | RSS/API feed URL |
| policy | CharField | metadata_only or cache_allowed |
| is_active | Boolean | Whether source is active |

### ContentItem

Individual content items discovered from sources.

| Field | Type | Description |
|-------|------|-------------|
| source | ForeignKey(ContentSource) | Parent source |
| title | CharField | Content title |
| description | TextField | Content description |
| url | URLField | Original content URL |
| media_url | URLField | Direct media URL |
| storage_url | URLField | Cloud storage URL (S3/Supabase) |
| published_at | DateTimeField | Publication date |
| quality_score | Float | AI-assessed quality score |
| topics | JSONField | Extracted topics |
| guid | CharField | Unique identifier (prevents duplicates) |

### Subscription

Links users to content sources they follow.

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey(User) | Subscriber |
| source | ForeignKey(ContentSource) | Subscribed source |
| priority | Integer | Priority level (higher = more important) |
| is_active | Boolean | Whether subscription is active |

### DownloadItem

Tracks content prepared for offline use.

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey(User) | Owner |
| source | ForeignKey(ContentSource) | Content source |
| title | CharField | Content title |
| description | TextField | Content description |
| original_url | URLField | Original content URL |
| media_url | URLField | Media file URL |
| local_file_path | CharField | Path to downloaded file |
| file_size_bytes | BigInteger | File size |
| status | CharField | queued, downloading, ready, failed |
| error_message | TextField | Error details if failed |

### EventLog

Tracks user interactions for analytics.

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey(User) | User |
| item | ForeignKey(DownloadItem) | Related download |
| event_type | CharField | view, play, finish, save, skip |
| duration_sec | Integer | Duration in seconds |
| context | JSONField | Additional context data |

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user with preferences |
| POST | `/api/auth/login/` | Login user (session-based) |
| GET | `/api/auth/login/` | Get CSRF cookie |
| POST | `/api/auth/logout/` | Logout user |
| GET | `/api/auth/me/` | Get current authenticated user |

### Resource Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET, POST | `/api/sources/` | List/create content sources |
| GET, PUT, DELETE | `/api/sources/:id/` | Retrieve/update/delete source |
| GET, POST | `/api/subscriptions/` | List/create subscriptions |
| GET, PUT, DELETE | `/api/subscriptions/:id/` | Retrieve/update/delete subscription |
| GET, POST | `/api/commute/` | List/create commute windows |
| GET, PUT, DELETE | `/api/commute/:id/` | Retrieve/update/delete window |
| GET, POST | `/api/downloads/` | List/create downloads |
| GET, PUT, DELETE | `/api/downloads/:id/` | Retrieve/update/delete download |
| GET | `/api/downloads/:id/file/` | Download file content |
| GET, PATCH | `/api/preferences/` | Get/update user preferences |

### ETL Pipeline Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/etl/trigger/` | Manually trigger content ingestion |
| POST | `/api/etl/clear/` | Clear content pool |
| GET | `/api/etl/status/` | Get ETL pipeline status |

### Request/Response Examples

**Register User:**

```json
POST /api/auth/register/

Request:
{
  "username": "johndoe",
  "password": "securepassword123",
  "email": "john@example.com",
  "preferences": {
    "topics": ["technology", "science", "news"],
    "max_daily_items": 15,
    "max_storage_mb": 1000
  },
  "subscriptions": [1, 2, 3]
}

Response:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "subscriptions_created": 3,
  "message": "User registered successfully"
}
```

**Get Current User:**

```json
GET /api/auth/me/

Response:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "preferences": {
    "id": 1,
    "topics": ["technology", "science", "news"],
    "max_daily_items": 15,
    "max_storage_mb": 1000
  },
  "stats": {
    "subscriptions": 3,
    "downloads": 12
  }
}
```

---

## WebSocket Integration

### Connection

Connect to the WebSocket endpoint for real-time agent execution:

```
ws://localhost:8000/ws/agents/
```

Authentication is handled via Django session cookies. Users must be logged in.

### Client to Server Messages

**Trigger Agent Execution:**

```json
{
  "type": "trigger_agents",
  "max_items": 5
}
```

### Server to Client Messages

| Type | Description |
|------|-------------|
| `connection_established` | WebSocket connected successfully |
| `execution_started` | Agent execution has begun |
| `agent_message` | Real-time update from an agent |
| `download_queued` | Content item added to download queue |
| `download_ready` | File downloaded and ready for access |
| `execution_complete` | All agents finished (includes summary) |
| `error` | Error occurred during execution |

**Example: execution_complete message:**

```json
{
  "type": "execution_complete",
  "message": "Agent execution completed successfully!",
  "summary": {
    "total_downloads": 5,
    "queued": 0,
    "downloading": 2,
    "ready": 3,
    "failed": 0
  }
}
```

---

## AI Agent System

SmartCache uses a multi-agent architecture powered by AutoGen and Ollama for intelligent content discovery and management.

### Agent Overview

| Agent | Role | Primary Function |
|-------|------|------------------|
| Content Discovery Agent | Scout | Find and recommend content based on user subscriptions and preferences |
| Content Download Agent | Executor | Queue downloads and trigger background processing |
| Content Summarizer Agent | Analyst | Assess content quality and generate summaries |

### Agent Tools Reference

**Content Discovery Agent Tools:**

| Tool | Parameters | Description |
|------|------------|-------------|
| `discover_new_sources` | `content_type`, `topic` | Find new content sources to subscribe to |
| `get_user_subscriptions_info` | `user_id` | Get list of user's current subscriptions |
| `recommend_content_for_download` | `user_id`, `max_items` | Generate personalized content recommendations |
| `get_content_item_details` | `content_item_id` | Get detailed info about a specific content item |

**Content Download Agent Tools:**

| Tool | Parameters | Description |
|------|------------|-------------|
| `queue_download` | `user_id`, `content_item_id` | Add content to user's download queue |
| `check_download_status` | `download_item_id` | Check status of a specific download |
| `process_download_queue` | `user_id` | Trigger Celery tasks for all queued items |

**Content Summarizer Agent Tools:**

| Tool | Parameters | Description |
|------|------------|-------------|
| `summarize_content` | `content_item_id` | Generate a summary of the content |
| `assess_quality` | `content_item_id` | Rate content quality and relevance (0-10) |

### Team Configurations

**RoundRobinGroupChat** (Default):
- Agents take turns in a fixed order: Discovery -> Download -> Summarizer
- Predictable execution flow
- Best for structured workflows

**SelectorGroupChat** (Advanced):
- LLM dynamically selects which agent speaks next
- More flexible conversation flow
- Better for complex multi-step tasks

### LLM Configuration

Agents use Ollama as the LLM backend with OpenAI-compatible API:

```bash
# Environment Variables
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

**Supported Models:**

| Model | Size | Best For |
|-------|------|----------|
| `llama3.1` | 8B | General purpose (default) |
| `llama3.1:70b` | 70B | Higher quality responses |
| `mistral` | 7B | Fast inference |
| `codellama` | 7B | Code-related tasks |

### Running Ollama

```bash
# Start Ollama server (Terminal 1)
ollama serve

# Pull the default model (Terminal 2)
ollama pull llama3.1

# Verify installation
curl http://localhost:11434/api/tags
```

### Docker Configuration for Ollama

When running in Docker, Ollama runs on the host machine. Configure the backend to reach it:

```bash
# In docker-compose.yml or .env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

---

## Data Flow Diagrams

### User Registration Flow

```
[User fills registration form]
           |
           v
[Frontend: Register.jsx]
           |
           | POST /api/auth/register/
           | { username, password, email, preferences, subscriptions }
           |
           v
[Django: register_user() view]
           |
           +--> [Create User object]
           |
           +--> [Create UserPreference object]
           |         - topics: ["technology", "news"]
           |         - max_daily_items: 10
           |         - max_storage_mb: 500
           |
           +--> [Create Subscription objects]
           |         - Link user to selected ContentSources
           |
           +--> [Auto-login user (set session cookie)]
           |
           v
[Response: { id, username, message: "User registered successfully" }]
           |
           v
[Frontend: Redirect to Dashboard]
```

### Content Discovery and Download Flow

```
[User clicks "Discover & Download Content" button]
           |
           v
[Frontend: AgentExecutor.jsx]
           |
           | WebSocket: ws://localhost:8000/ws/agents/
           | { "type": "trigger_agents", "max_items": 5 }
           |
           v
[Django Channels: AgentExecutionConsumer]
           |
           +--> [Authenticate user from session]
           |
           +--> [Create Agent Team (RoundRobinGroupChat)]
           |
           v
[Agent Team Execution]
           |
           +--> [Discovery Agent]
           |         |
           |         +--> recommend_content_for_download(user_id, max_items)
           |         |         |
           |         |         +--> Query Subscription.objects.filter(user=user)
           |         |         +--> Query ContentItem.objects.filter(source__in=subscribed_sources)
           |         |         +--> Filter by UserPreference.topics
           |         |         +--> Return top N recommendations with Content IDs
           |         |
           |         +--> [Send WebSocket message: agent_message]
           |
           +--> [Download Agent]
           |         |
           |         +--> For each Content ID:
           |         |         queue_download(user_id, content_item_id)
           |         |               |
           |         |               +--> Create DownloadItem(status='queued')
           |         |               +--> Return download_item_id
           |         |
           |         +--> process_download_queue(user_id)
           |                   |
           |                   +--> For each queued DownloadItem:
           |                           download_content_file.delay(download_item_id)
           |                                  |
           |                                  +--> [Celery Task in Background]
           |
           +--> [Summarizer Agent]
                     |
                     +--> assess_quality(content_item_id)
                     +--> [Update ContentItem.quality_score]
           |
           v
[WebSocket: execution_complete]
{ "type": "execution_complete", "summary": { "total_downloads": 5, ... } }


[Meanwhile, in Celery Worker...]
           |
           v
[download_content_file(download_item_id)]
           |
           +--> [Fetch DownloadItem from database]
           |
           +--> [Update status to 'downloading']
           |
           +--> [Stream download from storage_url (S3/Supabase)]
           |         |
           |         +--> [Save to /media/downloads/user_{id}/{filename}]
           |
           +--> [Update DownloadItem]
           |         - status = 'ready'
           |         - local_file_path = '/media/downloads/...'
           |         - file_size_bytes = 12345678
           |
           +--> [notify_download_ready(download_item, file_size)]
                     |
                     v
           [WebSocket push to frontend]
           { "type": "download_ready", "download_id": 501, "file_url": "/api/downloads/501/file/" }
                     |
                     v
           [Frontend auto-triggers browser download]
```

### ETL Content Ingestion Flow

```
[Trigger: Celery Beat (hourly) OR Manual API call OR Management command]
           |
           v
[ingest_content_sources() task]
           |
           +--> ContentSource.objects.filter(is_active=True)
           |
           v
[For each ContentSource...]
           |
           +--> [Route by source.type]
                     |
    +----------------+----------------+----------------+----------------+
    |                |                |                |                |
    v                v                v                v                v
[podcast]       [article]        [video]          [meme]           [news]
    |                |                |                |                |
    v                v                v                v                v
[feedparser]    [feedparser]     [yt-dlp]      [meme-api.com]    [NewsAPI]
    |                |                |                |                |
    +----------------+----------------+----------------+----------------+
                     |
                     v
           [For each entry/item...]
                     |
                     +--> [Generate GUID (hash of URL or RSS ID)]
                     |
                     +--> [Check: ContentItem.filter(guid=guid).exists()?]
                     |         |
                     |         +--> [Yes] --> Skip (duplicate)
                     |         |
                     |         +--> [No] --> Continue
                     |
                     +--> [Parse metadata: title, description, url, published_at]
                     |
                     +--> [Extract media_url from enclosures]
                     |
                     +--> [If source.policy == 'cache_allowed']
                     |         |
                     |         +--> [Download media to temp file]
                     |         |
                     |         +--> [Upload to S3/Supabase]
                     |         |         |
                     |         |         +--> storage_url = "https://bucket.s3..."
                     |         |
                     |         +--> [Delete temp file]
                     |
                     +--> [Create ContentItem record]
                               |
                               +--> source, title, description, url
                               +--> media_url, storage_url, storage_provider
                               +--> published_at, guid, file_size_bytes
           |
           v
[Return ingestion statistics]
{
    "sources_processed": 7,
    "total_items_added": 45,
    "errors": 0,
    "details": { "NPR News Now": 10, "TED Talks": 8, ... }
}
```

### File Download Serving Flow

```
[User clicks download button in Downloads page]
           |
           v
[Frontend: GET /api/downloads/{id}/file/]
           |
           v
[Django: download_file() view]
           |
           +--> [Authenticate user from session]
           |
           +--> [Query DownloadItem.objects.get(id=id, user=request.user)]
           |
           +--> [Verify download.status == 'ready']
           |
           +--> [Verify file exists: os.path.exists(download.local_file_path)]
           |
           +--> [Determine content type from file extension]
           |         .mp3 --> 'audio/mpeg'
           |         .mp4 --> 'video/mp4'
           |         .pdf --> 'application/pdf'
           |
           +--> [Create FileResponse]
           |         - Open file in binary mode
           |         - Set Content-Disposition header
           |         - Set Content-Length header
           |
           v
[Stream file to browser]
           |
           v
[Browser saves/plays file]
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=postgres://user:password@localhost/smartcache

# Redis (required for Celery and Channels)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Ollama (AI Agents)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Cloud Storage (optional)
STORAGE_PROVIDER=none  # Options: aws_s3, supabase, none

# AWS S3 (if using S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET_NAME=smartcache-media
AWS_REGION=us-east-1

# Supabase (if using Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key
SUPABASE_BUCKET=media

# News API (for news sources)
NEWSAPI_KEY=your-newsapi-key

# Frontend (for Docker/production)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## Troubleshooting

### Module Not Found Errors

Ensure the virtual environment is activated:

```bash
# Windows
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### Database Errors

Reset the database:

```bash
# Delete SQLite database
rm db.sqlite3  # or del db.sqlite3 on Windows

# Re-run migrations
python manage.py migrate

# Reload sample data
python manage.py seed_defaults
```

### Port Already in Use

Use a different port:

```bash
# Django on port 8080
python manage.py runserver 8080

# Vite on port 3000
cd frontend && npm run dev -- --port 3000
```

### SSL Certificate Errors (pip install)

Use trusted host flags:

```bash
pip install package-name --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

### WebSocket Connection Issues

1. Ensure Redis is running: `redis-cli ping` should return `PONG`
2. Verify Django Channels is configured correctly
3. Check that the user is authenticated before connecting
4. Ensure Daphne is running (not Django's default runserver for production)

### Celery Worker Not Processing Tasks

1. Check Redis connection: `redis-cli ping`
2. Verify Celery is running: `celery -A smartcache worker --loglevel=info`
3. Check for errors in Celery output
4. Ensure `CELERY_BROKER_URL` is correct in settings

### Ollama/AI Agent Issues

1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Ensure the model is downloaded: `ollama list`
3. Check `OLLAMA_BASE_URL` environment variable
4. For Docker, use `http://host.docker.internal:11434`

### CORS Errors in Frontend

1. Verify `CORS_ALLOWED_ORIGINS` includes `http://localhost:5173`
2. Check `CSRF_TRUSTED_ORIGINS` in Django settings
3. Ensure cookies are being sent with requests (`withCredentials: true`)

---

## Sample Data

After running `python manage.py seed_defaults`, the following content sources are available:

**Podcasts:**
- NPR News Now
- TED Talks Daily
- NASA Breaking News
- BBC World

**Articles:**
- Hacker News Frontpage
- Reddit API
- Substack Crawler

All sources include real RSS feed URLs for testing.

---

## Management Commands

| Command | Description |
|---------|-------------|
| `python manage.py seed_defaults` | Load sample content sources |
| `python manage.py run_etl` | Manually run content ingestion |
| `python manage.py add_news_sources` | Add NewsAPI sources |
| `python manage.py add_youtube_sources` | Add YouTube sources |
| `python manage.py add_meme_sources` | Add meme sources |
| `python manage.py cleanup_sources` | Remove inactive sources |
| `python manage.py fix_preferences` | Fix user preference issues |

---

## Contributing

This is a team project for SE-Team6-Fall2025. The repository follows standard Git workflow practices.

### Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Run linting: `npm run lint` (frontend) 
4. Test your changes locally
5. Submit a pull request for review

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript/React**: ESLint configuration provided
- **Commits**: Use descriptive commit messages

---

