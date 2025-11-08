#!/usr/bin/env python
"""
Test AWS S3 connection and configuration.

This script verifies that your S3 credentials are correct and the bucket is accessible.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')
django.setup()

from django.conf import settings

print("="*70)
print("🔧 AWS S3 CONNECTION TEST")
print("="*70)
print()

# Check settings
print("1. Checking environment variables...")
print("-"*70)
print(f"   STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
print(f"   AWS_ACCESS_KEY_ID: {'✓ Set' if settings.AWS_ACCESS_KEY_ID else '✗ Not set'}")
print(f"   AWS_SECRET_ACCESS_KEY: {'✓ Set' if settings.AWS_SECRET_ACCESS_KEY else '✗ Not set'}")
print(f"   AWS_S3_BUCKET_NAME: {settings.AWS_S3_BUCKET_NAME}")
print(f"   AWS_REGION: {settings.AWS_REGION}")
print()

if settings.STORAGE_PROVIDER != 's3':
    print("⚠️  WARNING: STORAGE_PROVIDER is not set to 's3'")
    print("   Update your .env file: STORAGE_PROVIDER=s3")
    print()

if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
    print("❌ ERROR: AWS credentials not found!")
    print()
    print("Please add to your .env file:")
    print("   AWS_ACCESS_KEY_ID=your_access_key_here")
    print("   AWS_SECRET_ACCESS_KEY=your_secret_key_here")
    print("   AWS_S3_BUCKET_NAME=your-bucket-name")
    print("   AWS_REGION=us-east-1")
    exit(1)

# Test S3 connection
print("2. Testing S3 connection...")
print("-"*70)

try:
    import boto3
    from botocore.exceptions import ClientError
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    
    # Try to access the bucket
    response = s3_client.head_bucket(Bucket=settings.AWS_S3_BUCKET_NAME)
    print(f"   ✓ Successfully connected to S3!")
    print(f"   ✓ Bucket exists: {settings.AWS_S3_BUCKET_NAME}")
    print(f"   ✓ Region: {settings.AWS_REGION}")
    print()
    
    # List some objects (if any)
    print("3. Checking bucket contents...")
    print("-"*70)
    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            MaxKeys=10
        )
        
        if 'Contents' in response and response['Contents']:
            count = response.get('KeyCount', 0)
            total = response.get('KeyCount', 0)
            print(f"   ✓ Found {count} objects (showing first 10)")
            for obj in response['Contents'][:10]:
                size_mb = obj['Size'] / (1024 * 1024)
                print(f"      - {obj['Key']} ({size_mb:.2f} MB)")
        else:
            print("   ℹ️  Bucket is empty (ready for uploads)")
        print()
        
    except ClientError as e:
        print(f"   ⚠️  Could not list objects: {e}")
        print()
    
    # Test upload
    print("4. Testing file upload...")
    print("-"*70)
    
    # Create a small test file
    test_content = b"SmartCache AI - S3 Test File"
    test_key = "test/connection_test.txt"
    
    try:
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain',
        )
        print(f"   ✓ Test file uploaded: {test_key}")
        
        # Generate public URL
        url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{test_key}"
        print(f"   ✓ Public URL: {url}")
        print()
        
        # Clean up test file
        s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=test_key
        )
        print(f"   ✓ Test file deleted")
        print()
        
    except ClientError as e:
        print(f"   ✗ Upload failed: {e}")
        print()
    
    print("="*70)
    print("✅ AWS S3 IS READY!")
    print("="*70)
    print()
    print("🚀 Next steps:")
    print("   1. Run ETL: python manage.py run_etl --storage-provider s3")
    print("   2. Or set in .env: STORAGE_PROVIDER=s3")
    print()
    
except ClientError as e:
    error_code = e.response.get('Error', {}).get('Code', 'Unknown')
    error_msg = e.response.get('Error', {}).get('Message', str(e))
    
    print(f"   ✗ S3 Error ({error_code}): {error_msg}")
    print()
    
    if error_code == 'NoSuchBucket':
        print("   💡 Bucket does not exist. Create it:")
        print(f"      1. Go to https://s3.console.aws.amazon.com/s3/")
        print(f"      2. Click 'Create bucket'")
        print(f"      3. Name: {settings.AWS_S3_BUCKET_NAME}")
        print(f"      4. Region: {settings.AWS_REGION}")
        print(f"      5. Uncheck 'Block all public access' (for public URLs)")
    
    elif error_code == 'InvalidAccessKeyId':
        print("   💡 Invalid Access Key ID")
        print("      Check your AWS_ACCESS_KEY_ID in .env")
    
    elif error_code == 'SignatureDoesNotMatch':
        print("   💡 Invalid Secret Access Key")
        print("      Check your AWS_SECRET_ACCESS_KEY in .env")
    
    elif error_code in ['AccessDenied', '403']:
        print("   💡 Access denied. Check:")
        print("      1. IAM user has S3 permissions")
        print("      2. Bucket policy allows access")
    
    print()
    exit(1)

except ImportError:
    print("   ✗ boto3 not installed!")
    print("   Run: pip install boto3")
    print()
    exit(1)

except Exception as e:
    print(f"   ✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    print()
    exit(1)

