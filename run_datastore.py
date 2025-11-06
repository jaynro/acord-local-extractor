"""
Example script demonstrating ACORD extraction using Vertex AI Search Data Store.

This script shows three ways to retrieve and process ACORD forms:
1. Search by form number, policy, or insured name
2. Direct document retrieval by document ID
3. Direct GCS URI processing
"""
import os
import json
from dotenv import load_dotenv
from agents.acord_extractor.datastore_agent import create_datastore_agent

if __name__ == "__main__":
    load_dotenv()
    
    agent = create_datastore_agent()
    
    print("=" * 80)
    print("ACORD Data Store Extraction Demo")
    print("=" * 80)
    
    # Example 1: Search by form number
    print("\n--- Example 1: Search by Form Number ---")
    try:
        result = agent({
            "form_number": "140",
            "insured_name": "John Doe"
        })
        print("\nExtracted Data:")
        print(result)
        
        # Save output
        with open("output_datastore_search.json", 'w', encoding='utf-8') as f:
            f.write(result)
        print("\n✓ Output saved to output_datastore_search.json")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Direct GCS URI (if you have the direct link from Data Store)
    print("\n\n--- Example 2: Direct GCS URI ---")
    try:
        # This would be a GCS URI returned from your Data Store search
        gcs_uri = "gs://smo_mvp_08242025-test/sample_input_file/140-Property-Acord-1.pdf"
        
        result = agent({
            "gcs_uri": gcs_uri
        })
        print("\nExtracted Data:")
        print(result)
        
        # Save output
        with open("output_datastore_gcs.json", 'w', encoding='utf-8') as f:
            f.write(result)
        print("\n✓ Output saved to output_datastore_gcs.json")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Direct document ID (if you know the document ID in Data Store)
    print("\n\n--- Example 3: Direct Document ID ---")
    print("(Requires document_id from your Data Store)")
    print("Example usage:")
    print("""
    result = agent({
        "document_id": "your-document-id-here"
    })
    """)
    
    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)
