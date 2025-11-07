import os
import json
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from .gcs_utils import download_from_gcs


def create_agent():
    """Create and return the ACORD extraction agent"""
    
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={'api_version': 'v1alpha'}
    )
    
    def agent(inputs):
        pdf_path = inputs.get("pdf_path")
        gcs_bucket = inputs.get("gcs_bucket", os.getenv("GCS_BUCKET_NAME"))
        gcs_blob = inputs.get("gcs_blob")
        
        # Download from GCS if blob name is provided
        temp_file = None
        if gcs_blob:
            if not gcs_bucket:
                raise ValueError("GCS bucket name must be provided via 'gcs_bucket' parameter or GCS_BUCKET_NAME environment variable")
            
            print(f"Downloading from GCS: gs://{gcs_bucket}/{gcs_blob}")
            pdf_path = download_from_gcs(gcs_bucket, gcs_blob)
            temp_file = pdf_path  # Mark for cleanup
        elif not pdf_path:
            raise ValueError("Either 'pdf_path' (local file) or 'gcs_blob' (GCS file) must be provided")
        
        try:
            # Upload the PDF file to Gemini
            with open(pdf_path, 'rb') as f:
                pdf_file = client.files.upload(file=f, config={'mime_type': 'application/pdf'})
            
            # Define your prompt with specific JSON structure
            prompt = """
            Extract the following information from this ACORD insurance form and return it as valid JSON.
            
            Required JSON structure:
            {
                "named_insured": "string - First Named Insured name",
                "premises_information": [
                    {
                        "street_address": "string - full address",
                        "coverage_information": [
                            {
                                "Subject_of_insurance": "string - e.g., 'Building' or 'Business Personal property'",
                                "amount": "string - formatted as currency with $ symbol and decimals (e.g., '$500000.00')"
                            }
                        ]
                    }
                ]
            }
            
            Important:
            - Return ONLY valid JSON, no additional text or markdown
            - Format all amounts as currency strings with $ symbol and .00 decimals
            - If a field is not found, use empty string "" for strings and empty array [] for arrays
            - Include all premises and coverage information found in the form
            """
            
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
            
            model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
            resp = client.models.generate_content(
                model=model_name,
                contents=[prompt, pdf_file],
                config=config,
            )
            
            # Parse and validate JSON
            try:
                result = json.loads(resp.text)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError:
                return resp.text
        
        finally:
            # Clean up temporary file if downloaded from GCS
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up temporary file: {temp_file}")
    
    return agent