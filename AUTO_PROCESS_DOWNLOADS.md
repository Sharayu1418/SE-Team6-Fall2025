# Automatic Download Queue Processing

## Question
**Will we manually have to process the queue each time?**

## Answer: **No!** We now have **TWO options**:

---

## ✅ Option 1: Automatic Processing (Recommended)

**NEW:** Downloads are now **automatically processed** when items are queued!

### How It Works
When `queue_download()` creates a new `DownloadItem` with status `'queued'`, a Django signal automatically triggers the Celery download task.

### Implementation
- **File:** `core/signals.py` - Django signal handler
- **File:** `core/apps.py` - Signal registration
- **Trigger:** `post_save` signal on `DownloadItem` model

### Benefits
- ✅ **Zero manual steps** - Downloads start automatically
- ✅ **No agent changes needed** - Works with existing agent code
- ✅ **Configurable** - Can be disabled via settings

### Configuration
Add to `smartcache/settings.py` to disable auto-processing:
```python
AUTO_PROCESS_DOWNLOADS = False  # Default: True
```

### Example Flow
```python
# Agent calls:
queue_download(user_id=1, content_item_id=5479)

# What happens:
# 1. DownloadItem created with status='queued'
# 2. Signal fires automatically
# 3. Celery task download_content_file.delay() is triggered
# 4. File downloads in background
# ✅ No manual process_download_queue() call needed!
```

---

## ✅ Option 2: Agent-Initiated Processing (Still Works)

The Download Agent can still manually call `process_download_queue()` if needed.

### Updated Agent Instructions
The Download Agent's system message now emphasizes:
- **CRITICAL**: Always call `process_download_queue(user_id)` after queuing items
- This ensures downloads start even if signals are disabled

### When to Use
- If `AUTO_PROCESS_DOWNLOADS = False` in settings
- If you want explicit control over when processing starts
- For batch processing multiple users

---

## 🔄 How Both Options Work Together

### Scenario 1: Auto-Processing Enabled (Default)
```
queue_download() 
  → DownloadItem created
    → Signal fires automatically
      → Celery task starts
        → File downloads ✅
```

### Scenario 2: Auto-Processing Disabled
```
queue_download() 
  → DownloadItem created
    → Signal fires but does nothing (disabled)
      → Agent calls process_download_queue()
        → Celery tasks start
          → Files download ✅
```

---

## 📊 Comparison

| Feature | Auto-Processing | Manual Processing |
|---------|----------------|-------------------|
| **Setup** | Automatic | Agent must call `process_download_queue()` |
| **Speed** | Immediate | After agent call |
| **Control** | Less explicit | Full control |
| **Reliability** | Signal-based | Agent-dependent |
| **Use Case** | Default behavior | When disabled or batch processing |

---

## 🧪 Testing

### Test Auto-Processing
```python
from core.tools.content_download import queue_download
from core.models import DownloadItem
import time

# Queue a download
result = queue_download(user_id=1, content_item_id=5479)
print(result)

# Wait a moment
time.sleep(2)

# Check if task started automatically
item = DownloadItem.objects.latest('created_at')
print(f"Status: {item.status}")  # Should be 'downloading' or 'ready'
```

### Test Manual Processing
```python
# Disable auto-processing in settings
AUTO_PROCESS_DOWNLOADS = False

# Queue download
queue_download(user_id=1, content_item_id=5479)

# Manually process
from core.tools.content_download import process_download_queue
result = process_download_queue(user_id=1)
print(result)
```

---

## 🎯 Recommendation

**Use Auto-Processing (Option 1)** for:
- ✅ Normal agent workflows
- ✅ User-initiated downloads
- ✅ Simpler agent code

**Use Manual Processing (Option 2)** for:
- ⚙️ Batch operations
- ⚙️ When you need explicit control
- ⚙️ Testing/debugging

---

## 📝 Files Modified

1. **`core/signals.py`** (NEW) - Auto-processing signal handler
2. **`core/apps.py`** - Signal registration
3. **`core/agents/definitions.py`** - Enhanced agent instructions

---

## 🚀 Next Steps

1. **Test auto-processing:**
   ```bash
   python manage.py shell -c "
   from core.tools.content_download import queue_download
   result = queue_download(user_id=1, content_item_id=5479)
   print(result)
   "
   ```

2. **Check Celery logs** to see tasks start automatically

3. **Verify downloads** complete without manual `process_download_queue()` call

---

## 💡 Summary

**You no longer need to manually call `process_download_queue()`!**

Downloads are now automatically processed when items are queued via Django signals. The agent can still call it manually if needed, but it's no longer required. 🎉

