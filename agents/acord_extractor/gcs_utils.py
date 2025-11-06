"""
Google Cloud Storage utility functions for downloading files.
"""
import os
import tempfile
from google.cloud import storage


def download_from_gcs(bucket_name, blob_name, destination_path=None):
    """
    Download a file from Google Cloud Storage.
    
    Args:
        bucket_name: Name of the GCS bucket
        blob_name: Path to the file in the bucket (e.g., 'pdfs/acord-form.pdf')
        destination_path: Optional local path to save the file. If None, creates a temp file.
        
    Returns:
        Path to the downloaded file
    """
    # Initialize GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Create destination path if not provided
    if destination_path is None:
        # Create a temporary file
        suffix = os.path.splitext(blob_name)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        destination_path = temp_file.name
        temp_file.close()
    
    # Download the file
    blob.download_to_filename(destination_path)
    print(f"Downloaded gs://{bucket_name}/{blob_name} to {destination_path}")
    
    return destination_path


def list_files_in_gcs(bucket_name, prefix=''):
    """
    List files in a GCS bucket with optional prefix filter.
    
    Args:
        bucket_name: Name of the GCS bucket
        prefix: Optional prefix to filter files (e.g., 'pdfs/')
        
    Returns:
        List of blob names
    """
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    return [blob.name for blob in blobs]


def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    """
    Upload a file to Google Cloud Storage.
    
    Args:
        bucket_name: Name of the GCS bucket
        source_path: Local path to the file to upload
        destination_blob_name: Path in the bucket where the file will be stored
        
    Returns:
        Public URL of the uploaded file
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_path)
    print(f"Uploaded {source_path} to gs://{bucket_name}/{destination_blob_name}")
    
    return f"gs://{bucket_name}/{destination_blob_name}"
