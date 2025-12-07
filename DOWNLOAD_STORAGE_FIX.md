# Download Storage Fix

## Issue Summary

The download agent was attempting to download content from the original source URLs instead of from the S3/Supabase storage URLs where files were cached during the ETL pipeline.

## Root Cause

1. **ETL Pipeline Failures**: The ETL pipeline was getting `403 Forbidden` errors when trying to download from many original sources (e.g., `https://sphinx.acast.com/...`)

2. **Incomplete ContentItems**: When downloads fail during ETL, ContentItems are created with:
   - ✓ `media_url` (original URL)
   - ✗ `storage_url` (NULL - because download failed)

3. **Recommendation Issue**: The `recommend_content_for_download` tool was recommending ALL content, including items without `storage_url`

4. **Download Failures**: When Download Agent queued these items, the Celery task attempted to download from the original URLs again, hitting the same 403 errors

## Statistics

- **Total ContentItems**: 5,595
- **Items with storage_url**: 5 (0.09%)
- **Items without storage_url**: 5,590 (99.91%)

Most content failed to cache during ETL due to source restrictions (403 Forbidden).

## Solution Implemented

### 1. Filter Recommendations (content_recommendation.py)

```python
# Only recommend items that are cached in S3/Supabase
available_items = ContentItem.objects.filter(
    source_id__in=source_ids,
    storage_url__isnull=False,  # MUST have storage URL
).exclude(
    storage_url=''  # Exclude empty strings
)
```

**Impact**: Discovery Agent will only recommend content that can actually be downloaded.

### 2. Validate Queue Downloads (content_download.py)

```python
# Validate that content is cached in storage
if not content_item.storage_url:
    return (
        f"❌ Cannot queue download for '{content_item.title}'\n\n"
        f"This content is not cached in storage (S3/Supabase).\n"
        ...
    )
```

**Impact**: Prevents queuing downloads for uncached content.

### 3. Enhanced Download Task Logging (tasks.py)

```python
# Log whether we're downloading from storage or original source
if 's3.amazonaws.com' in download_item.media_url or 'supabase' in download_item.media_url:
    logger.info(f"✓ Downloading from cached storage...")
else:
    logger.warning(f"⚠️  Downloading from ORIGINAL source (not cached)...")
```

**Impact**: Clear visibility into where downloads are coming from.

## Verification Steps

1. **Check Recommended Content**:
   ```python
   from core.tools.content_recommendation import recommend_content_for_download
   result = recommend_content_for_download(user_id=1, max_items=5)
   print(result)
   ```
   
   Should only return items with valid S3 URLs.

2. **Run AutoGen Team**:
   ```bash
   python test_full_pipeline.py
   ```
   
   Should successfully recommend and download cached content.

3. **Verify Downloads**:
   ```python
   from core.models import DownloadItem
   items = DownloadItem.objects.filter(status='ready')
   print(f"Successfully downloaded: {items.count()}")
   ```

## Next Steps

### Short Term
- ✅ Filter recommendations to only include cached content
- ✅ Add validation to queue_download
- ✅ Improve logging

### Medium Term
- [ ] Investigate why ETL pipeline gets 403 errors
  - Check if sources require user-agent headers
  - Check if sources require authentication
  - Check if sources have rate limiting
- [ ] Implement retry logic with exponential backoff for ETL downloads
- [ ] Add monitoring/alerting for ETL download failures

### Long Term
- [ ] Implement alternative download strategies:
  - Use browser automation (Selenium/Playwright) for protected content
  - Implement session management for authenticated sources
  - Add proxy support for geo-restricted content
- [ ] Add a "cache status" indicator in the UI
- [ ] Allow users to manually trigger cache for specific items

## Related Files

- `core/tools/content_recommendation.py` - Recommendation logic
- `core/tools/content_download.py` - Queue download logic
- `core/tasks.py` - Celery download task
- `core/services/content_ingestion.py` - ETL pipeline

## Impact on User Experience

**Before Fix**:
- ❌ Users would get recommendations for content that couldn't be downloaded
- ❌ Download queue would fill with failed items
- ❌ Confusing error messages about 403 Forbidden

**After Fix**:
- ✅ Users only see content that's actually available for download
- ✅ All queued downloads use cached S3 URLs
- ✅ Clear error messages if content isn't cached

## Testing

Run the full pipeline test:
```bash
python test_full_pipeline.py
```

Expected behavior:
1. ETL pipeline runs (may show 403 errors for uncached content)
2. Discovery Agent recommends only cached content (5 items available)
3. Download Agent queues and downloads from S3 URLs
4. Downloads complete successfully

