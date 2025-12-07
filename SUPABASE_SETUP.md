# 🔐 Supabase Storage Permissions Fix

## The Problem
Your Supabase bucket `smartcache-media` has Row-Level Security (RLS) enabled, which blocks uploads from the ETL pipeline.

**Error:** `new row violates row-level security policy`

## ✅ Quick Fix (Recommended for Testing)

### Step 1: Go to Storage Policies
Open: https://supabase.com/dashboard/project/lcmbhljqjmnvidqzfrfk/storage/policies

### Step 2: Add Upload Policy

1. Click **"New Policy"** button
2. Choose **"For full customization"** (bottom option)
3. Fill in:
   - **Policy name**: `Allow public uploads and access`
   - **Allowed operations**: Check all boxes:
     - ☑ SELECT (read)
     - ☑ INSERT (upload)
     - ☑ UPDATE (modify)
     - ☑ DELETE (remove)
   - **Policy definition**: 
     ```sql
     bucket_id = 'smartcache-media'
     ```
   - **WITH CHECK expression**:
     ```sql
     bucket_id = 'smartcache-media'
     ```
4. Click **"Review"** → **"Save policy"**

### Step 3: Make Bucket Public

1. Go to: https://supabase.com/dashboard/project/lcmbhljqjmnvidqzfrfk/storage/buckets
2. Find `smartcache-media`
3. Click **⋮** (three dots menu)
4. Click **"Edit bucket"**
5. Toggle **"Public bucket"** to **ON**
6. Click **"Save"**

---

## Alternative: Disable RLS Entirely (Easier for Dev)

If you just want to test quickly:

1. Go to: https://supabase.com/dashboard/project/lcmbhljqjmnvidqzfrfk/database/tables
2. Find table: `storage.objects`
3. Click **⋮** → **"Edit table"**
4. Find **"Enable Row Level Security"**
5. Toggle it **OFF**
6. Confirm

⚠️ **Note**: Only do this for development/testing. In production, use proper policies.

---

## After Fixing Permissions

Run this command to test the upload:

```bash
python manage.py run_etl --source-name "NPR News Now" --provider supabase
```

You should see:
```
✓ Uploaded media to supabase: https://lcmbhljqjmnvidqzfrfk.supabase.co/storage/v1/object/public/smartcache-media/...
✓ NPR News Now: X new items
```

---

## Verify Uploads

After successful upload, check:

1. **Supabase Dashboard**: https://supabase.com/dashboard/project/lcmbhljqjmnvidqzfrfk/storage/buckets/smartcache-media
   - You should see folders: `podcasts/npr-news-now/`
   - With audio files: `abc123.mp3`, etc.

2. **Django Shell**:
```bash
python manage.py shell
```

```python
from core.models import ContentItem

# Check Supabase items
items = ContentItem.objects.filter(storage_provider='supabase')
print(f"Items in Supabase: {items.count()}")

# View storage URLs
for item in items[:3]:
    print(f"{item.title}")
    print(f"Storage URL: {item.storage_url}")
    print()
```

---

## Troubleshooting

### Still getting 403 errors?
- Make sure the bucket is **PUBLIC**
- Make sure you added the **policy for all operations**
- Try refreshing the Supabase dashboard

### Can't find the policy settings?
- Make sure you're in the right project
- Storage policies are under: Storage → Policies (in left sidebar)

### Files not appearing?
- Check the Storage browser in Supabase
- Look for folders: `podcasts/` and `articles/`

---

**Once you've fixed the permissions, reply "fixed" and I'll re-run the ETL pipeline!**

