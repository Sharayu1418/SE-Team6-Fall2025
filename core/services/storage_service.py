"""
Storage service abstraction for uploading media to cloud storage.

This module provides a common interface for uploading content to different
storage providers (AWS S3, Supabase Storage). The ETL pipeline uses this
service to store downloaded media files.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional
from datetime import timedelta

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """Abstract base class for storage providers."""
    
    @abstractmethod
    def upload_file(self, file_path: str, object_key: str) -> str:
        """
        Upload a file to storage.
        
        Args:
            file_path: Local path to the file to upload
            object_key: Key/path for the object in storage (e.g., 'podcasts/123.mp3')
            
        Returns:
            Public URL to access the uploaded file
        """
        pass
    
    @abstractmethod
    def get_download_url(self, object_key: str, expiry_hours: int = 24) -> str:
        """
        Get a download URL for an object.
        
        Args:
            object_key: Key/path of the object in storage
            expiry_hours: Hours until the URL expires (for presigned URLs)
            
        Returns:
            URL to download the file
        """
        pass


class S3StorageService(StorageService):
    """AWS S3 storage implementation."""
    
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: str = 'us-east-1',
    ):
        """
        Initialize S3 storage service.
        
        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key (uses env var if None)
            aws_secret_access_key: AWS secret key (uses env var if None)
            region: AWS region
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            self.bucket_name = bucket_name
            self.region = region
            self.ClientError = ClientError
            
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region,
            )
            
            logger.info(f"Initialized S3StorageService for bucket: {bucket_name}")
            
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise
    
    def upload_file(self, file_path: str, object_key: str) -> str:
        """
        Upload a file to S3.
        
        Args:
            file_path: Local path to file
            object_key: S3 object key (e.g., 'podcasts/npr/episode-123.mp3')
            
        Returns:
            Public S3 URL to the uploaded file
        """
        try:
            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs={'ContentType': self._guess_content_type(file_path)}
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_key}"
            
            logger.info(f"Uploaded {file_path} to S3: {object_key}")
            return url
            
        except self.ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            raise
    
    def get_download_url(self, object_key: str, expiry_hours: int = 24) -> str:
        """
        Generate a presigned URL for downloading from S3.
        
        Args:
            object_key: S3 object key
            expiry_hours: Hours until URL expires
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                },
                ExpiresIn=expiry_hours * 3600,  # Convert to seconds
            )
            
            return url
            
        except self.ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def _guess_content_type(self, file_path: str) -> str:
        """Guess content type from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.m4a': 'audio/mp4',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.pdf': 'application/pdf',
            '.html': 'text/html',
        }
        
        return content_types.get(ext, 'application/octet-stream')


class SupabaseStorageService(StorageService):
    """Supabase Storage implementation."""
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        bucket_name: str = 'media',
    ):
        """
        Initialize Supabase storage service.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key (anon or service role)
            bucket_name: Storage bucket name
        """
        try:
            from supabase import create_client, Client
            
            self.bucket_name = bucket_name
            self.supabase: Client = create_client(supabase_url, supabase_key)
            
            logger.info(f"Initialized SupabaseStorageService for bucket: {bucket_name}")
            
        except ImportError:
            logger.error("supabase not installed. Install with: pip install supabase")
            raise
    
    def upload_file(self, file_path: str, object_key: str) -> str:
        """
        Upload a file to Supabase Storage.
        
        Args:
            file_path: Local path to file
            object_key: Object path in bucket (e.g., 'podcasts/npr/episode-123.mp3')
            
        Returns:
            Public URL to the uploaded file
        """
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=object_key,
                file=file_data,
                file_options={
                    "content-type": self._guess_content_type(file_path),
                    "upsert": "true",  # Overwrite if exists
                }
            )
            
            # Generate public URL
            url = self.supabase.storage.from_(self.bucket_name).get_public_url(object_key)
            
            logger.info(f"Uploaded {file_path} to Supabase: {object_key}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload to Supabase: {e}")
            raise
    
    def get_download_url(self, object_key: str, expiry_hours: int = 24) -> str:
        """
        Get a signed URL for downloading from Supabase.
        
        Args:
            object_key: Object path in bucket
            expiry_hours: Hours until URL expires
            
        Returns:
            Signed download URL
        """
        try:
            # Create signed URL
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                path=object_key,
                expires_in=expiry_hours * 3600,  # Convert to seconds
            )
            
            if isinstance(response, dict) and 'signedURL' in response:
                return response['signedURL']
            else:
                # Fallback to public URL if signed URL fails
                return self.supabase.storage.from_(self.bucket_name).get_public_url(object_key)
                
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            # Fallback to public URL
            return self.supabase.storage.from_(self.bucket_name).get_public_url(object_key)
    
    def _guess_content_type(self, file_path: str) -> str:
        """Guess content type from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.m4a': 'audio/mp4',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.pdf': 'application/pdf',
            '.html': 'text/html',
        }
        
        return content_types.get(ext, 'application/octet-stream')


def get_storage_service(
    provider: str = 'aws_s3',
    **kwargs
) -> StorageService:
    """
    Factory function to get the appropriate storage service.
    
    Args:
        provider: Storage provider ('aws_s3' or 'supabase')
        **kwargs: Provider-specific configuration
        
    Returns:
        StorageService instance
        
    Example:
        # AWS S3
        storage = get_storage_service(
            provider='aws_s3',
            bucket_name='my-bucket',
            region='us-east-1'
        )
        
        # Supabase
        storage = get_storage_service(
            provider='supabase',
            supabase_url='https://xxx.supabase.co',
            supabase_key='xxx',
            bucket_name='media'
        )
    """
    if provider == 'aws_s3':
        return S3StorageService(
            bucket_name=kwargs.get('bucket_name', 'smartcache-media'),
            aws_access_key_id=kwargs.get('aws_access_key_id'),
            aws_secret_access_key=kwargs.get('aws_secret_access_key'),
            region=kwargs.get('region', 'us-east-1'),
        )
    
    elif provider == 'supabase':
        return SupabaseStorageService(
            supabase_url=kwargs['supabase_url'],
            supabase_key=kwargs['supabase_key'],
            bucket_name=kwargs.get('bucket_name', 'media'),
        )
    
    else:
        raise ValueError(f"Unsupported storage provider: {provider}")

