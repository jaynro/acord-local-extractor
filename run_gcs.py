import os
import json
from dotenv import load_dotenv
from agents.acord_extractor.agent import create_agent

if __name__ == "__main__":
    load_dotenv()  # load .env variables

    agent = create_agent()
    
    # Example 1: Process file from Google Cloud Storage
    gcs_bucket = os.getenv("GCS_BUCKET_NAME")
    gcs_blob = "sample_input_file/140-Property-Acord-1.pdf"  # Path in your GCS bucket
    
    print("Processing PDF from Google Cloud Storage...")
    print(f"Bucket: {gcs_bucket}")
    print(f"Blob: {gcs_blob}\n")
    
    result = agent({
        "gcs_bucket": gcs_bucket,
        "gcs_blob": gcs_blob
    })
    
    # Print to console
    print("\nExtracted Data:")
    print(result)
    
    # Save to JSON file
    output_file = "output_gcs.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\n✓ Output saved to {output_file}")
