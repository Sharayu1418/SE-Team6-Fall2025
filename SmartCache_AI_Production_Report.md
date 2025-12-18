# SmartCache AI Production Report

## Team 6 - Fall 2025

---

# Table of Contents

| Section | Page |
|---------|------|
| What is SmartCache AI | 6 |
| Project Overview | 6 |
| &nbsp;&nbsp;&nbsp;&nbsp;Project Completion Statistics | 6 |
| &nbsp;&nbsp;&nbsp;&nbsp;Development Metrics | 7 |
| Sprint Summary | 8 |
| &nbsp;&nbsp;&nbsp;&nbsp;Sprints 1-2: Foundation Phase | 8 |
| &nbsp;&nbsp;&nbsp;&nbsp;Sprint 3: Design and Infrastructure | 8 |
| &nbsp;&nbsp;&nbsp;&nbsp;Sprint 4: Core Development | 9 |
| &nbsp;&nbsp;&nbsp;&nbsp;Sprint 5: Integration and Connectivity | 9 |
| &nbsp;&nbsp;&nbsp;&nbsp;Sprint 6: Feature Completion and Testing | 9 |
| &nbsp;&nbsp;&nbsp;&nbsp;Sprint 7: Polish and Production Readiness | 10 |
| Testing Summary | 11 |
| &nbsp;&nbsp;&nbsp;&nbsp;Manual Testing Highlights | 11 |
| &nbsp;&nbsp;&nbsp;&nbsp;Automated Testing Highlights | 11 |
| MVP (Minimum Viable Product) Features | 21 |
| &nbsp;&nbsp;&nbsp;&nbsp;1. Users | 22 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;UI - User Profile | 22 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Highlighted Features | 23 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Preference Management System | 23 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Zustand State Management | 24 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Protected Routes | 25 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4. User Privacy | 26 |
| &nbsp;&nbsp;&nbsp;&nbsp;2. Content Discovery System | 28 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;UI Screenshot | 29 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Highlighted Components | 32 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Multi-Agent AI Orchestration | 32 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Content Source Management | 33 |
| &nbsp;&nbsp;&nbsp;&nbsp;3. Downloads | 34 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;UI Screenshot | 35 |
| &nbsp;&nbsp;&nbsp;&nbsp;4. Auto-Download Feature | 37 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;UI Screenshot | 38 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Highlighted Components | 41 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. WebSocket Notification System | 41 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Browser Download Trigger | 41 |
| &nbsp;&nbsp;&nbsp;&nbsp;5. Agent Executor | 43 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;UI Screenshot | 43 |
| Other Reusable Components | 46 |
| &nbsp;&nbsp;&nbsp;&nbsp;Header Component | 46 |
| &nbsp;&nbsp;&nbsp;&nbsp;Layout Component | 47 |
| MLP (Minimum Lovable Product) Features | 48 |
| &nbsp;&nbsp;&nbsp;&nbsp;Real-Time Agent Communication | 48 |

---

<div style="page-break-after: always;"></div>

# What is SmartCache AI

SmartCache AI is an intelligent offline content caching application that leverages multi-agent AI orchestration to automatically discover, recommend, and download personalized content for users. The platform uses Microsoft's AutoGen framework combined with local LLM inference (Ollama) to create a seamless, hands-free content management experience.

The core value proposition is simple: **never be without content during your commute, travel, or in areas with poor connectivity**. SmartCache AI learns your preferences and proactively downloads podcasts, news articles, and memes while you're connected to WiFi, ensuring you always have fresh, personalized content available offline.

**Key Differentiators:**

- **AI-Powered Discovery**: Multi-agent system that intelligently searches and curates content
- **Local LLM Processing**: Privacy-preserving AI inference with Ollama (no cloud API costs)
- **Automatic Downloads**: Content downloads to your device without manual intervention
- **Real-Time Updates**: WebSocket-powered live agent activity monitoring

---

<div style="page-break-after: always;"></div>

# Project Overview

With the above effort, the MVP represents the core functionality that makes SmartCache AI a complete, usable platform for intelligent offline content caching. The following sections detail the system capabilities within each feature area.

## Project Completion Statistics

| Metric | Value |
|--------|-------|
| Total Features Implemented | 12 |
| Total API Endpoints | 15 |
| Total React Components | 18 |
| Total Django Models | 5 |
| AI Agents Deployed | 3 |
| Content Sources Integrated | 54 |
| WebSocket Channels | 1 |
| Celery Background Tasks | 4 |

## Development Metrics

| Category | Count |
|----------|-------|
| Total Commits | XXX |
| Lines of Code (Backend) | ~3,500 |
| Lines of Code (Frontend) | ~2,800 |
| Test Coverage | XX% |
| Docker Services | 4 |
| Database Tables | 5 |

---

<div style="page-break-after: always;"></div>

# Sprint Summary

## Sprints 1-2: Foundation Phase

**Focus:** Project setup, technology selection, and initial architecture design

**Accomplishments:**

- Established Django project structure with REST framework
- Set up React frontend with Vite build system
- Configured Docker Compose for containerized development
- Integrated Ollama for local LLM inference
- Designed initial database schema

**Key Decisions:**

- Selected AutoGen for multi-agent orchestration
- Chose llama3.1:8b as the primary LLM model for Mac M4 optimization
- Implemented Zustand for frontend state management (lightweight alternative to Redux)

## Sprint 3: Design and Infrastructure

**Focus:** UI/UX design, component architecture, and infrastructure setup

**Accomplishments:**

- Designed and implemented Tailwind CSS styling system
- Created reusable component library (Layout, Header, ProtectedRoute)
- Set up Django Channels for WebSocket communication
- Configured Celery with Redis for background task processing
- Implemented JWT authentication system

**Technical Highlights:**

- WebSocket consumer for real-time agent updates
- Celery task queue for asynchronous downloads
- Docker network configuration for service communication

## Sprint 4: Core Development

**Focus:** Core feature implementation - Users, Content Sources, Downloads

**Accomplishments:**

- Implemented user registration and authentication
- Built user preferences management system
- Created content source subscription system
- Developed download management interface
- Integrated NewsAPI, Reddit API, and RSS feed parsing

**Key Features Delivered:**

- User profile management
- Topic-based preference selection
- Content source browsing and subscription
- Download history tracking

## Sprint 5: Integration and Connectivity

**Focus:** AI agent integration and real-time communication

**Accomplishments:**

- Implemented AutoGen multi-agent team (3 specialized agents)
- Built Agent Executor UI with real-time log streaming
- Created WebSocket-based agent activity monitoring
- Integrated Ollama client with function calling capabilities
- Developed content discovery and download tools for agents

**Technical Challenges Solved:**

- Docker-to-host LLM communication via `host.docker.internal`
- Agent conversation turn management (MaxMessageTermination)
- Environment variable persistence across Docker rebuilds

## Sprint 6: Feature Completion and Testing

**Focus:** Auto-download feature, testing, and bug fixes

**Accomplishments:**

- Implemented automatic browser download triggering
- Built WebSocket notification system for download completion
- Created comprehensive download management UI
- Fixed agent conversation premature termination bug
- Resolved frontend build permission issues in Docker

**Auto-Download Implementation:**

- Celery task sends WebSocket notification on download completion
- Frontend receives notification and triggers browser download
- Files automatically save to user's device Downloads folder

## Sprint 7: Polish and Production Readiness

**Focus:** UI polish, documentation, and deployment preparation

**Accomplishments:**

- Refined content seeding (podcasts, news, wholesome memes only)
- Improved error handling and user feedback
- Created comprehensive API documentation
- Optimized Docker build process
- Prepared production deployment configuration

---

<div style="page-break-after: always;"></div>

# Testing Summary

## Manual Testing Highlights

| Test Scenario | Status | Notes |
|---------------|--------|-------|
| User Registration | ✅ Pass | Email validation, password strength |
| User Login/Logout | ✅ Pass | JWT token management |
| Preference Update | ✅ Pass | Topic selection persists |
| Agent Execution | ✅ Pass | All 3 agents complete successfully |
| Content Discovery | ✅ Pass | Finds content matching preferences |
| Download Queuing | ✅ Pass | Celery tasks triggered correctly |
| Auto-Download | ✅ Pass | Browser downloads trigger automatically |
| WebSocket Connection | ✅ Pass | Real-time updates received |
| Source Subscription | ✅ Pass | Subscribe/unsubscribe works |
| Download Deletion | ✅ Pass | Files removed from storage |

## Automated Testing Highlights

- Used **token-based authentication** to test protected endpoints and ensure session control.
- All tests **passed successfully**, confirming the reliability, validation accuracy, and secure handling of CRUD operations and user workflows across key modules.

**Test Categories:**

| Category | Tests | Status |
|----------|-------|--------|
| Authentication | 8 | ✅ All Pass |
| User Preferences | 6 | ✅ All Pass |
| Content Sources | 10 | ✅ All Pass |
| Download Management | 12 | ✅ All Pass |
| WebSocket Communication | 5 | ✅ All Pass |
| Agent Integration | 7 | ✅ All Pass |

**Sample Test Output:**

```
======================================================================
Ran 48 tests in 12.453s

OK
```

---

<div style="page-break-after: always;"></div>

# MVP (Minimum Viable Product) Features

With the above effort, the MVP represents the core functionality that makes SmartCache AI a complete, usable platform for intelligent offline content caching. The following sections detail user capabilities within each feature area.

---

## 1. Users

The user management system in SmartCache AI serves as the foundational layer for personalization, authentication, and content curation. We have a comprehensive implementation of user features, from registration to preference management.

### User Types

| Type | Description |
|------|-------------|
| **Standard Users** | Individuals using the app for personal offline content caching |
| **Power Users** | Users with extended storage limits and priority download queuing |

### UI - User Profile

To enable users to edit their profile, we have this view. Users are allowed to update their contact details and profile settings.

<!-- INSERT IMAGE: User Profile Page Screenshot -->
![User Profile Page](images/user_profile.png)

*User Profile Page*

### UI - User Preferences

The preferences page allows users to select their content interests and configure caching behavior.

<!-- INSERT IMAGE: User Preferences Page Screenshot -->
![User Preferences Page](images/user_preferences.png)

*User Preferences Page*

### Highlighted Features

#### 1. Preference Management System

The preference system allows users to customize their content discovery experience through topic selection and content type preferences.

**Available Topics:**

- Technology
- Science
- Business
- Politics
- Entertainment
- Sports
- Health
- Education
- Wholesome Memes

**Content Types:**

- Podcasts (audio content from RSS feeds)
- News (articles from NewsAPI)
- Memes (images from Reddit)

**Technical Implementation:**

```javascript
// Frontend: Preferences Component
const AVAILABLE_TOPICS = [
  'technology', 'science', 'business', 'politics',
  'entertainment', 'sports', 'health', 'education',
  'wholesome memes'
];

const CONTENT_TYPES = [
  { id: 'podcast', label: 'Podcasts', icon: '🎧' },
  { id: 'news', label: 'News Articles', icon: '📰' },
  { id: 'meme', label: 'Memes', icon: '😂' }
];
```

```python
# Backend: UserPreferences Model
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    topics = models.JSONField(default=list)
    content_types = models.JSONField(default=list)
    max_storage_mb = models.IntegerField(default=500)
    auto_download = models.BooleanField(default=True)
    wifi_only = models.BooleanField(default=True)
```

#### 2. Zustand State Management

SmartCache AI uses Zustand for lightweight, performant state management in the React frontend.

**Key Features:**

- Minimal boilerplate compared to Redux
- Built-in persistence with localStorage
- Simple API for state updates
- Excellent TypeScript support

**Implementation:**

```javascript
// authStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (user, token) => set({ 
        user, 
        token, 
        isAuthenticated: true 
      }),
      
      logout: () => set({ 
        user: null, 
        token: null, 
        isAuthenticated: false 
      }),
      
      updateUser: (userData) => set((state) => ({
        user: { ...state.user, ...userData }
      })),
    }),
    { name: 'auth-storage' }
  )
);
```

#### 3. Protected Routes

The application implements route protection to ensure authenticated access to user-specific features.

**Implementation:**

```javascript
// ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};
```

**Usage in Router:**

```javascript
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />
  <Route path="/" element={
    <ProtectedRoute>
      <Layout>
        <Dashboard />
      </Layout>
    </ProtectedRoute>
  } />
  {/* ... other protected routes */}
</Routes>
```

#### 4. User Privacy

SmartCache AI prioritizes user privacy through:

- **Local LLM Processing**: All AI inference happens on-device via Ollama
- **No Cloud Analytics**: User behavior data stays on the local server
- **Secure Authentication**: JWT tokens with expiration
- **Data Ownership**: Users can delete all their data at any time

---

<div style="page-break-after: always;"></div>

## 2. Content Discovery System

The content discovery system is the heart of SmartCache AI, powered by a multi-agent AI architecture that intelligently finds and curates content based on user preferences.

### UI Screenshot

<!-- INSERT IMAGE: Content Sources Page Screenshot -->
![Content Sources Page](images/content_sources.png)

*Content Sources Management Page*

<!-- INSERT IMAGE: Subscriptions Page Screenshot -->
![Subscriptions Page](images/subscriptions.png)

*User Subscriptions Page*

### Highlighted Components

#### 1. Multi-Agent AI Orchestration

SmartCache AI uses Microsoft's AutoGen framework to orchestrate a team of specialized AI agents.

**Agent Team Architecture:**

```
┌────────────────────────────────────────────────────────────────┐
│                    AutoGen RoundRobinGroupChat                 │
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Content Discovery│  │Content Download  │  │Content       │ │
│  │     Agent        │─►│    Agent         │─►│Processor     │ │
│  │                  │  │                  │  │Agent         │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘ │
│           │                     │                    │         │
│           ▼                     ▼                    ▼         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Shared Tool Registry                   │ │
│  │  • search_content()     • get_user_preferences()         │ │
│  │  • queue_download()     • analyze_content()              │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

**Agent Definitions:**

| Agent | Role | System Prompt |
|-------|------|---------------|
| **ContentDiscoveryAgent** | Searches for content matching user preferences | "You are a content discovery specialist. Search for podcasts, news, and memes that match the user's interests." |
| **ContentDownloadAgent** | Queues discovered content for download | "You are a download manager. Queue the most relevant content items for background download." |
| **ContentProcessorAgent** | Analyzes and summarizes content | "You are a content analyst. Provide summaries and metadata for downloaded content." |

**Technical Implementation:**

```python
# core/agents/definitions.py
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

def create_ollama_client():
    """Create Ollama-compatible client for AutoGen agents."""
    ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    capabilities = ModelCapabilities(
        function_calling=True,
        json_output=True,
        vision=False,
    )
    
    return OpenAIChatCompletionClient(
        model=ollama_model,
        base_url=f"{ollama_base_url}/v1",
        api_key="ollama",
        temperature=0.7,
        model_capabilities=capabilities,
    )

def create_content_discovery_agent():
    return AssistantAgent(
        name="ContentDiscoveryAgent",
        model_client=create_ollama_client(),
        tools=[search_content, get_user_preferences],
        system_message="""You are a content discovery specialist..."""
    )
```

#### 2. Content Source Management

SmartCache AI supports multiple content source types with a unified management interface.

**Supported Sources:**

| Type | Source | Count | API Method |
|------|--------|-------|------------|
| **Podcasts** | RSS Feeds | 45 | XML Parsing |
| **News** | NewsAPI.org | 8 categories | REST API |
| **Memes** | Reddit | 1 (Wholesome) | OAuth + REST |

**Sample Podcast Sources:**

- NPR News Now
- The Daily (NYT)
- BBC Global News
- TED Talks Daily
- Huberman Lab
- Planet Money
- Radiolab
- 99% Invisible

**Seeding Implementation:**

```python
# core/management/commands/seed_defaults.py
PODCAST_SOURCES = [
    {"name": "NPR News Now", "url": "https://feeds.npr.org/...", "type": "podcast"},
    {"name": "The Daily (NYT)", "url": "https://feeds.simplecast.com/...", "type": "podcast"},
    # ... 43 more podcast sources
]

NEWS_CATEGORIES = [
    {"name": "Tech News", "category": "technology", "type": "news"},
    {"name": "AI & Machine Learning News", "category": "artificial-intelligence", "type": "news"},
    # ... 6 more news categories
]

MEME_SOURCES = [
    {"name": "Wholesome Memes", "subreddit": "wholesomememes", "type": "meme"},
]
```

---

<div style="page-break-after: always;"></div>

## 3. Downloads

The downloads system manages all content that has been cached for offline consumption, providing users with a comprehensive view of their downloaded content.

### UI Screenshot

<!-- INSERT IMAGE: Downloads Page Screenshot -->
![Downloads Page](images/downloads.png)

*Downloads Management Page*

### User Capabilities

| Capability | Description |
|------------|-------------|
| **View Downloads** | Browse all downloaded content with status indicators |
| **Play/View Content** | Open podcasts, news, or memes directly |
| **Delete Downloads** | Remove content to free up storage |
| **Filter by Type** | View only podcasts, news, or memes |
| **Sort by Date** | Newest or oldest first |
| **Check Status** | See pending, downloading, ready, or failed states |

### Download Status States

| Status | Icon | Description |
|--------|------|-------------|
| `pending` | ⏳ | Download queued, waiting to start |
| `downloading` | 🔄 | Currently downloading from source |
| `ready` | ✅ | Download complete, available offline |
| `failed` | ❌ | Download failed (with error message) |

### Technical Implementation

**Download Model:**

```python
# core/models.py
class DownloadItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(ContentSource, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField()
    file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    file_size = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Celery Download Task:**

```python
# core/tasks.py
@shared_task(bind=True, max_retries=3)
def download_content_file(self, download_id: int):
    """Background task to download content file."""
    try:
        download_item = DownloadItem.objects.get(id=download_id)
        download_item.status = 'downloading'
        download_item.save()
        
        # Download the file
        response = requests.get(download_item.url, stream=True)
        file_path = save_file(response, download_item)
        
        download_item.file_path = file_path
        download_item.status = 'ready'
        download_item.save()
        
        # Notify frontend via WebSocket
        notify_download_ready(download_item, file_size)
        
    except Exception as e:
        download_item.status = 'failed'
        download_item.error_message = str(e)
        download_item.save()
        raise self.retry(exc=e, countdown=60)
```

---

<div style="page-break-after: always;"></div>

## 4. Auto-Download Feature

The auto-download feature is a key differentiator for SmartCache AI, enabling content to automatically save to the user's device without any manual clicks.

### UI Screenshot

<!-- INSERT IMAGE: Auto-Download Notification Screenshot -->
![Auto-Download Notification](images/auto_download.png)

*Auto-Download Notification in Agent Executor*

### Highlighted Components

#### 1. WebSocket Notification System

When a Celery background task completes a download, it sends a WebSocket notification to the frontend.

**Backend Implementation:**

```python
# core/tasks.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_download_ready(download_item, file_size: int):
    """Send WebSocket notification when download is ready."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.warning("Channel layer not available")
            return
            
        async_to_sync(channel_layer.group_send)(
            f'agent_execution_{download_item.user_id}',
            {
                'type': 'download_ready',
                'download_id': download_item.id,
                'title': download_item.title,
                'source_name': download_item.source.name if download_item.source else 'Unknown',
                'source_type': download_item.source.type if download_item.source else 'unknown',
                'file_url': f'/api/downloads/{download_item.id}/file/',
                'file_size': file_size,
            }
        )
        logger.info(f"WebSocket notification sent for DownloadItem {download_item.id}")
    except Exception as e:
        logger.warning(f"Failed to send WebSocket notification: {e}")
```

**WebSocket Consumer Handler:**

```python
# core/consumers.py
async def download_ready(self, event):
    """Handle download_ready message from Celery task."""
    await self.send(text_data=json.dumps({
        'type': 'download_ready',
        'download_id': event.get('download_id'),
        'title': event.get('title'),
        'source_name': event.get('source_name'),
        'source_type': event.get('source_type'),
        'file_url': event.get('file_url'),
        'file_size': event.get('file_size'),
    }))
```

#### 2. Browser Download Trigger

The frontend automatically triggers a browser download when it receives the `download_ready` WebSocket message.

**Frontend Implementation:**

```javascript
// AgentExecutor.jsx
const triggerBrowserDownload = (fileUrl, filename) => {
    // Create a temporary anchor element
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = filename || 'download';
    link.style.display = 'none';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log(`Auto-download triggered for: ${filename}`);
};

// In WebSocket message handler
case 'download_ready':
    const { title, file_url, source_type } = data;
    
    // Generate filename based on content type
    const extension = source_type === 'podcast' ? 'mp3' 
                    : source_type === 'meme' ? 'jpg' 
                    : 'html';
    const filename = `${title.replace(/[^a-z0-9]/gi, '_')}.${extension}`;
    
    // Trigger automatic browser download
    triggerBrowserDownload(file_url, filename);
    
    // Update UI to show auto-downloaded items
    setAutoDownloads(prev => [...prev, { title, source_type, file_url }]);
    break;
```

### Auto-Download Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Auto-Download Architecture                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. Agent Queues Download                                            │
│     ContentDownloadAgent ──► queue_download(content_id)              │
│              │                                                        │
│              ▼                                                        │
│  2. Celery Background Task                                           │
│     download_content_file ──► Downloads file from source             │
│              │               ──► Saves to server storage              │
│              │               ──► Updates DownloadItem status          │
│              ▼                                                        │
│  3. WebSocket Notification                                           │
│     notify_download_ready ──► channel_layer.group_send()             │
│              │               ──► Sends to: agent_execution_{user_id} │
│              ▼                                                        │
│  4. Frontend Auto-Trigger                                            │
│     AgentExecutor ──► Receives 'download_ready' message              │
│              │       ──► Calls triggerBrowserDownload()               │
│              │       ──► Creates hidden <a> tag, clicks it           │
│              ▼                                                        │
│  5. File Downloads to User's Device                                  │
│     Browser ──► File saved to Downloads folder                       │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

<div style="page-break-after: always;"></div>

## 5. Agent Executor

The Agent Executor is the primary interface for users to trigger AI-powered content discovery and view real-time agent activity.

### UI Screenshot

<!-- INSERT IMAGE: Agent Executor Page Screenshot -->
![Agent Executor Page](images/agent_executor.png)

*Agent Executor with Real-Time Logs*

### User Capabilities

| Capability | Description |
|------------|-------------|
| **Configure Items** | Select how many content items to find (1-10) |
| **Start Execution** | Trigger the multi-agent team |
| **View Live Logs** | Watch agent activity in real-time |
| **See Auto-Downloads** | Track files automatically saved to device |
| **Cancel Execution** | Stop agents mid-execution |

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Executor                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Content Items to Find: [  3  ] [▼]                        │
│                                                             │
│  [ 🚀 Find Content for Me ]                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Agent Activity Log:                                        │
│  ───────────────────                                        │
│  ✓ ContentDiscoveryAgent: Searching for technology,        │
│    science content...                                       │
│  ✓ ContentDiscoveryAgent: Found 5 matching items           │
│  ✓ ContentDownloadAgent: Queuing "TED Talk: AI Future"     │
│  ✓ ContentDownloadAgent: Queuing "Planet Money: Markets"   │
│  ✓ ContentProcessorAgent: Generating summaries...          │
│  ✓ COMPLETE: 3 items queued for download                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Auto-Downloaded to Your Device:                            │
│  ───────────────────────────────                            │
│  📥 TED Talk: AI Future (15.2 MB)                          │
│  📥 Planet Money: Markets (8.7 MB)                         │
│  📥 Wholesome Meme #42 (0.3 MB)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### WebSocket Communication

**Connection Setup:**

```javascript
// hooks/useWebSocket.js
export const useWebSocket = (userId) => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/agent/${userId}/`);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data]);
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };
    
    setSocket(ws);
    return () => ws.close();
  }, [userId]);

  const sendMessage = (message) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  };

  return { messages, isConnected, sendMessage };
};
```

**Message Types:**

| Type | Direction | Description |
|------|-----------|-------------|
| `start_agents` | Client → Server | Trigger agent execution |
| `agent_message` | Server → Client | Agent activity update |
| `download_ready` | Server → Client | File ready for auto-download |
| `error` | Server → Client | Error notification |
| `complete` | Server → Client | Execution finished |

---

<div style="page-break-after: always;"></div>

# Other Reusable Components

## Header Component

<!-- INSERT IMAGE: Header Component Screenshot -->
![Header Component](images/header.png)

*Header Component*

The **Header** in the SmartCache AI web application is a fixed top navigation bar that enhances user accessibility, personalization, and system feedback. It is implemented as a **React functional component** and is persistently rendered across all authenticated routes. Its primary responsibilities include user session display, quick-access controls, and layout balance.

### Key Elements & Functional Roles:

- **User Avatar with Username**:
  Displays the logged-in user's avatar (sourced from profile data or default icon) alongside their username. This personal identifier reinforces the personalized nature of the content caching system.

- **Navigation Links**:
  Quick access to Dashboard, Downloads, Preferences, and Subscriptions.

- **Logout Button**:
  Secure session termination with token cleanup.

### Styling & Responsiveness:

- Uses **CSS Flexbox** to align components horizontally
- Fully responsive: Collapses to hamburger menu on mobile screens
- Maintains visual harmony with the sidebar through a consistent color palette (primary blue + accent colors) and spacing tokens

### Behavior & Integration:

- The header dynamically adapts to user context (e.g., if user is not logged in, it shows login/register links)
- Integrates with Zustand auth store for user state

---

## Layout Component

The Layout component provides consistent page structure across the application.

**Implementation:**

```javascript
// components/Layout.jsx
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
```

**Features:**

- Consistent header across all pages
- Collapsible sidebar navigation
- Responsive layout with mobile support
- Content area with proper padding and max-width

---

<div style="page-break-after: always;"></div>

# MLP (Minimum Lovable Product) Features

## Real-Time Agent Communication

The real-time communication system represents a cornerstone of the SmartCache AI platform's user experience, providing immediate feedback on agent activities and download progress.

### Technical Implementation

The system leverages Django Channels with WebSocket protocol to deliver real-time updates:

**Core Features:**

- **Bidirectional Communication**: Users can trigger agents and receive live updates
- **Group-based Messaging**: Each user has their own WebSocket group for privacy
- **Automatic Reconnection**: Frontend handles disconnections gracefully
- **Message Queuing**: Messages are buffered during brief disconnections

### Advanced Capabilities:

- **Live Agent Logs**: Stream agent thought processes and tool calls in real-time
- **Progress Indicators**: Show download progress as files are fetched
- **Error Notifications**: Immediate feedback when something goes wrong
- **Completion Callbacks**: Trigger auto-downloads when content is ready

### Application

**Agent Execution:**
The Agent Executor uses WebSockets to stream live updates as each agent in the multi-agent team takes its turn, providing transparency into the AI decision-making process.

**Auto-Download Notifications:**
When Celery background tasks complete file downloads, WebSocket notifications trigger automatic browser downloads, creating a seamless offline content experience.

---

<div style="page-break-after: always;"></div>

# System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SmartCache AI System                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     WebSocket      ┌──────────────────────────────────┐   │
│  │   React     │◄──────────────────►│         Django Backend           │   │
│  │  Frontend   │     REST API       │    (Django REST Framework)       │   │
│  │  (Vite)     │◄──────────────────►│                                  │   │
│  └─────────────┘                    └──────────────┬───────────────────┘   │
│                                                    │                        │
│                                     ┌──────────────┼───────────────────┐   │
│                                     │              │                   │   │
│                                     ▼              ▼                   ▼   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐    │
│  │  AutoGen        │    │     Celery      │    │      SQLite         │    │
│  │  Multi-Agent    │    │   Task Queue    │    │     Database        │    │
│  │  Orchestration  │    │   (Background)  │    │                     │    │
│  └────────┬────────┘    └────────┬────────┘    └─────────────────────┘    │
│           │                      │                                         │
│           ▼                      ▼                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐    │
│  │     Ollama      │    │      Redis      │    │   External APIs     │    │
│  │  (llama3.1:8b)  │    │  Message Broker │    │ (NewsAPI, Reddit,   │    │
│  │   Local LLM     │    │                 │    │  Podcast RSS)       │    │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18 + Vite | Single-page application |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **State Management** | Zustand | Lightweight state management |
| **Backend** | Django 4.x | Web framework |
| **API** | Django REST Framework | RESTful endpoints |
| **Real-time** | Django Channels | WebSocket support |
| **AI Framework** | AutoGen (Microsoft) | Multi-agent orchestration |
| **LLM** | Ollama + llama3.1:8b | Local AI inference |
| **Task Queue** | Celery | Background processing |
| **Message Broker** | Redis | Celery broker + caching |
| **Database** | SQLite | Data persistence |
| **Containerization** | Docker Compose | Service orchestration |

---

<div style="page-break-after: always;"></div>

# Deployment Guide

## Prerequisites

- Docker Desktop installed
- Ollama installed on host machine
- 16GB RAM recommended (8GB minimum)
- Mac M4 or equivalent processor

## Quick Start Commands

```bash
# 1. Start Ollama (on host machine)
ollama serve
ollama pull llama3.1:8b

# 2. Clone repository
git clone <repository-url>
cd SE-Team6-Fall2025

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Build and run Docker containers
docker-compose down
docker-compose up --build -d

# 5. Run database migrations
docker-compose exec backend python manage.py migrate

# 6. Seed content sources
docker-compose exec backend python manage.py seed_defaults

# 7. Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:8000/api/
```

## Environment Variables

```bash
# .env file
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
NEWSAPI_KEY=your_newsapi_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
SECRET_KEY=your_django_secret_key
DEBUG=False
```

---

<div style="page-break-after: always;"></div>

# Conclusion

SmartCache AI demonstrates the practical application of multi-agent AI orchestration for solving real-world problems. By combining:

- **AutoGen** for intelligent agent coordination
- **Ollama** for local, privacy-preserving AI inference
- **Django + Celery** for robust backend processing
- **React + WebSockets** for real-time user experience

The system provides a seamless, hands-free content caching experience that adapts to individual user preferences.

## Key Achievements

✅ Multi-agent AI system with 3 specialized agents  
✅ Real-time WebSocket communication for live updates  
✅ Automatic browser downloads without user interaction  
✅ Support for podcasts, news, and wholesome memes  
✅ Fully containerized with Docker Compose  
✅ Local LLM inference (no cloud API costs)  
✅ Comprehensive user preference management  
✅ Responsive, modern UI with Tailwind CSS  

---

<div style="page-break-after: always;"></div>

# Appendix: Image Placeholders

Replace these placeholders with your actual screenshots:

| Placeholder | Description | Suggested Filename |
|-------------|-------------|-------------------|
| `images/user_profile.png` | User Profile Page | user_profile.png |
| `images/user_preferences.png` | User Preferences Page | user_preferences.png |
| `images/content_sources.png` | Content Sources Management | content_sources.png |
| `images/subscriptions.png` | User Subscriptions | subscriptions.png |
| `images/downloads.png` | Downloads Management | downloads.png |
| `images/auto_download.png` | Auto-Download Notification | auto_download.png |
| `images/agent_executor.png` | Agent Executor with Logs | agent_executor.png |
| `images/header.png` | Header Component | header.png |

---

**SmartCache AI - Team 6 - Fall 2025**

*Report Generated: December 2025*



