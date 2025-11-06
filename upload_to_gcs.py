"""
Helper script to upload ACORD PDFs to Google Cloud Storage for Data Store indexing.
"""
import os
from dotenv import load_dotenv
from agents.acord_extractor.gcs_utils import upload_to_gcs

load_dotenv()

def upload_samples_to_gcs():
    """Upload all sample PDFs to GCS bucket."""
    
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        print("Error: GCS_BUCKET_NAME not set in .env")
        return
    
    samples_dir = "samples"
    destination_folder = "acord-forms"
    
    print(f"Uploading ACORD samples to gs://{bucket_name}/{destination_folder}/")
    print("=" * 80)
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(samples_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {samples_dir}/")
        return
    
    uploaded = []
    for pdf_file in pdf_files:
        source_path = os.path.join(samples_dir, pdf_file)
        destination_blob = f"{destination_folder}/{pdf_file}"
        
        try:
            gcs_uri = upload_to_gcs(bucket_name, source_path, destination_blob)
            uploaded.append(gcs_uri)
            print(f"✓ Uploaded: {pdf_file}")
        except Exception as e:
            print(f"✗ Failed to upload {pdf_file}: {e}")
    
    print("\n" + "=" * 80)
    print(f"Upload complete! {len(uploaded)}/{len(pdf_files)} files uploaded")
    print("\nUploaded files:")
    for uri in uploaded:
        print(f"  - {uri}")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("1. Go to: https://console.cloud.google.com/gen-app-builder/engines")
    print(f"2. Click 'Create Data Store'")
    print(f"3. Select 'Cloud Storage' as data source")
    print(f"4. Choose bucket: {bucket_name}")
    print(f"5. Set folder filter: {destination_folder}/")
    print(f"6. Name your data store (e.g., 'acord-forms-datastore')")
    print(f"7. Copy the Data Store ID to your .env file as DATASTORE_ID")
    print("=" * 80)

if __name__ == "__main__":
    upload_samples_to_gcs()
