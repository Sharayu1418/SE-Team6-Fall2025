# AWS S3 Setup Guide

**Goal:** Switch from Supabase Storage to AWS S3 for media storage

---

## 📋 Prerequisites

- AWS Account (free tier is sufficient)
- AWS Access Key ID and Secret Access Key
- S3 Bucket (we'll create one)

---

## 🚀 Step-by-Step Setup

### Step 1: Create AWS S3 Bucket

1. **Go to AWS S3 Console:**
   - Visit: https://s3.console.aws.amazon.com/s3/

2. **Click "Create bucket"**

3. **Configure bucket:**
   - **Bucket name:** `smartcache-media-yourname` (must be globally unique)
   - **AWS Region:** `us-east-1` (or your preferred region)
   - **Block Public Access settings:**
     - ⚠️ **Uncheck** "Block all public access"
     - Check the box: "I acknowledge that the current settings..."
   - Click **"Create bucket"**

4. **Set Bucket Policy (for public read access):**
   - Click on your newly created bucket
   - Go to **Permissions** tab
   - Scroll to **Bucket policy** section
   - Click **Edit**
   - Paste this policy (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

   - Click **Save changes**

---

### Step 2: Create AWS Access Keys

1. **Go to IAM Console:**
   - Visit: https://console.aws.amazon.com/iam/

2. **Navigate to Users:**
   - Click **Users** in the left sidebar
   - Click your username (or create a new user)

3. **Create Access Key:**
   - Click **Security credentials** tab
   - Scroll to **Access keys** section
   - Click **Create access key**
   - Choose **"Application running outside AWS"**
   - Click **Next**
   - (Optional) Add description tag
   - Click **Create access key**

4. **Save Credentials:**
   - ⚠️ **IMPORTANT:** Copy both:
     - **Access key ID** (e.g., `AKIAIOSFODNN7EXAMPLE`)
     - **Secret access key** (e.g., `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
   - Download the CSV or save them securely
   - You **cannot** view the secret key again after closing this dialog!

---

### Step 3: Configure IAM Permissions

Your IAM user needs S3 permissions. Attach this policy:

1. In **IAM** → **Users** → Your user
2. Click **Add permissions** → **Attach policies directly**
3. Search for and attach: **`AmazonS3FullAccess`**
   - Or create a custom policy for just your bucket:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR-BUCKET-NAME",
                "arn:aws:s3:::YOUR-BUCKET-NAME/*"
            ]
        }
    ]
}
```

---

### Step 4: Update Your `.env` File

Open your `.env` file in the project root and update:

```bash
# ============================================
# STORAGE CONFIGURATION
# ============================================

# Change from 'supabase' to 's3'
STORAGE_PROVIDER=s3

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET_NAME=smartcache-media-yourname
AWS_REGION=us-east-1

# You can keep Supabase settings (they won't be used)
# SUPABASE_URL=https://...
# SUPABASE_KEY=...
# SUPABASE_BUCKET=smartcache-media
```

**Replace with your actual values!**

---

### Step 5: Test S3 Connection

Run the test script to verify everything works:

```bash
cd /Users/khushaliiishahh/Downloads/SE-Team6-Fall2025-anitej-etl-pipeline
source venv/bin/activate
python test_s3_connection.py
```

**Expected output:**
```
✓ Successfully connected to S3!
✓ Bucket exists: smartcache-media-yourname
✓ Region: us-east-1
✓ Test file uploaded
✓ Test file deleted
✅ AWS S3 IS READY!
```

---

### Step 6: Run ETL with S3

Now run the ETL pipeline to upload content to S3:

```bash
# Ingest a specific source
python manage.py run_etl --source-name "NPR News Now"

# Or ingest all sources
python manage.py run_etl
```

**What happens:**
1. Fetches RSS feeds
2. Downloads podcast/article media
3. **Uploads to AWS S3** (instead of Supabase)
4. Stores public S3 URLs in database

---

## 🔍 Verify S3 Upload

### Check in AWS Console:

1. Go to https://s3.console.aws.amazon.com/s3/
2. Click your bucket name
3. You should see folders like:
   - `podcasts/npr-news-now/`
   - `podcasts/the-daily-nyt/`
   - `podcasts/bbc-global-news/`

### Check in Database:

```bash
python manage.py shell
```

```python
from core.models import ContentItem

# Find items with S3 storage
s3_items = ContentItem.objects.filter(storage_provider='s3')
print(f"Items in S3: {s3_items.count()}")

# Show first item
if s3_items.exists():
    item = s3_items.first()
    print(f"Title: {item.title}")
    print(f"S3 URL: {item.storage_url}")
    print(f"File size: {item.file_size_bytes / (1024*1024):.2f} MB")
```

---

## 📊 Comparing S3 vs Supabase

| Feature | AWS S3 | Supabase Storage |
|---------|--------|------------------|
| **Free Tier** | 5 GB, 20K requests/month | 1 GB free |
| **Pricing** | Pay as you go | $0.021/GB/month |
| **Speed** | Very fast (AWS CDN) | Fast (global CDN) |
| **Setup** | More complex | Simpler |
| **Reliability** | 99.99% SLA | 99.9% SLA |
| **Integration** | Industry standard | Supabase ecosystem |

---

## 🎯 URL Format Comparison

### Supabase:
```
https://lcmbhljqjmnvidqzfrfk.supabase.co/storage/v1/object/public/smartcache-media/podcasts/npr-news-now/file.mp3
```

### AWS S3:
```
https://smartcache-media-yourname.s3.us-east-1.amazonaws.com/podcasts/npr-news-now/file.mp3
```

Both work exactly the same way in your application!

---

## 🔧 Switching Back to Supabase

If you want to switch back:

```bash
# In .env file:
STORAGE_PROVIDER=supabase
```

Then run ETL again:
```bash
python manage.py run_etl
```

---

## 💰 Cost Estimation

For a typical podcast app with **100 episodes** at **50 MB each**:

**Monthly Storage:**
- Total size: 5 GB
- S3 cost: **FREE** (within free tier)
- Over free tier: ~$0.12/month

**Monthly Bandwidth:**
- 1,000 downloads: **FREE**
- 10,000 downloads: ~$0.90/month

**Your current usage (46 files @ 160 MB):**
- Storage: **FREE** ✓
- Bandwidth: **FREE** ✓ (under 20K requests)

---

## 🛟 Troubleshooting

### Error: "NoSuchBucket"
**Solution:** Bucket name is wrong or doesn't exist
- Check `AWS_S3_BUCKET_NAME` in .env
- Create bucket in AWS console

### Error: "InvalidAccessKeyId"
**Solution:** Access key is incorrect
- Check `AWS_ACCESS_KEY_ID` in .env
- Generate new access key in IAM

### Error: "SignatureDoesNotMatch"
**Solution:** Secret key is incorrect
- Check `AWS_SECRET_ACCESS_KEY` in .env
- Make sure no extra spaces

### Error: "AccessDenied"
**Solution:** IAM user lacks permissions
- Attach `AmazonS3FullAccess` policy
- Or check custom bucket policy

### Upload works but URLs return 403
**Solution:** Bucket not configured for public access
- Go to bucket → Permissions
- Add bucket policy (see Step 1)

---

## 🎉 Success Checklist

- [ ] S3 bucket created
- [ ] Bucket policy allows public read
- [ ] IAM access keys generated
- [ ] IAM user has S3 permissions
- [ ] `.env` file updated with credentials
- [ ] `STORAGE_PROVIDER=s3` in .env
- [ ] `python test_s3_connection.py` passes ✓
- [ ] ETL pipeline uploads to S3
- [ ] S3 URLs are accessible in browser

---

## 🚀 Next Steps

1. **Test with one source:**
   ```bash
   python manage.py run_etl --source-name "NPR News Now"
   ```

2. **Verify in browser:**
   - Copy an S3 URL from the database
   - Paste in browser
   - Should play/download the media file

3. **Run full ETL:**
   ```bash
   python manage.py run_etl
   ```

4. **Check costs (optional):**
   - AWS Console → Billing Dashboard
   - Should see $0.00 (within free tier)

---

**Your SmartCache AI now uses AWS S3 for industrial-grade media storage!** 🎊

