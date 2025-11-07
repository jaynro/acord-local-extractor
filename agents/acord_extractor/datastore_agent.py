"""
ACORD Data Store Agent - Retrieves documents from Vertex AI Search and extracts structured data.
"""
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from .datastore_utils import search_acord_forms, get_document_content
from .gcs_utils import download_from_gcs


def create_datastore_agent():
    """
    Create an agent that retrieves ACORD forms from Data Store and extracts structured data.
    
    This agent:
    1. Searches for ACORD forms in Vertex AI Search Data Store
    2. Retrieves the document content
    3. Extracts structured JSON fields using Gemini
    """
    
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={'api_version': 'v1alpha'}
    )
    
    # Data Store configuration
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("DATASTORE_LOCATION", "global")
    data_store_id = os.getenv("DATASTORE_ID")
    
    def agent(inputs: Dict[str, Any]) -> str:
        """
        Process ACORD forms from Data Store.
        
        Args:
            inputs: Dictionary with search parameters:
                - form_number: ACORD form number (e.g., "140")
                - policy_number: Policy number
                - insured_name: Insured party name
                - document_id: Direct document ID (bypasses search)
                - gcs_uri: Direct GCS URI (e.g., "gs://bucket/path/file.pdf")
        """
        
        # Option 1: Direct document ID
        document_id = inputs.get("document_id")
        
        # Option 2: GCS URI from search result
        gcs_uri = inputs.get("gcs_uri")
        
        # Option 3: Search parameters
        form_number = inputs.get("form_number")
        policy_number = inputs.get("policy_number")
        insured_name = inputs.get("insured_name")
        
        pdf_path = None
        temp_file = None
        document_content = None
        
        try:
            # Route 1: Direct GCS URI
            if gcs_uri:
                if gcs_uri.startswith("gs://"):
                    # Parse GCS URI
                    parts = gcs_uri.replace("gs://", "").split("/", 1)
                    bucket = parts[0]
                    blob = parts[1] if len(parts) > 1 else ""
                    
                    print(f"Downloading from GCS: {gcs_uri}")
                    pdf_path = download_from_gcs(bucket, blob)
                    temp_file = pdf_path
                else:
                    raise ValueError(f"Invalid GCS URI: {gcs_uri}")
            
            # Route 2: Direct document retrieval from Data Store
            elif document_id:
                if not all([project_id, data_store_id]):
                    raise ValueError("PROJECT_ID and DATASTORE_ID must be set in .env")
                
                print(f"Retrieving document from Data Store: {document_id}")
                doc_data = get_document_content(
                    project_id=project_id,
                    location=location,
                    data_store_id=data_store_id,
                    document_id=document_id
                )
                
                # Check if document has GCS link
                if doc_data.get("uri") and doc_data["uri"].startswith("gs://"):
                    gcs_uri = doc_data["uri"]
                    parts = gcs_uri.replace("gs://", "").split("/", 1)
                    bucket = parts[0]
                    blob = parts[1] if len(parts) > 1 else ""
                    
                    print(f"Downloading linked file from GCS: {gcs_uri}")
                    pdf_path = download_from_gcs(bucket, blob)
                    temp_file = pdf_path
                else:
                    document_content = doc_data.get("content", "")
            
            # Route 3: Search Data Store
            elif any([form_number, policy_number, insured_name]):
                if not all([project_id, data_store_id]):
                    raise ValueError("PROJECT_ID and DATASTORE_ID must be set in .env")
                
                print(f"Searching Data Store for ACORD forms...")
                results = search_acord_forms(
                    project_id=project_id,
                    location=location,
                    data_store_id=data_store_id,
                    form_number=form_number,
                    policy_number=policy_number,
                    insured_name=insured_name,
                    max_results=1
                )
                
                if not results:
                    return json.dumps({
                        "error": "No matching documents found in Data Store",
                        "search_params": {
                            "form_number": form_number,
                            "policy_number": policy_number,
                            "insured_name": insured_name
                        }
                    }, indent=2)
                
                # Use the first result
                top_result = results[0]
                print(f"Found document: {top_result['id']}")
                
                # Check for GCS URI
                if top_result.get("uri") and top_result["uri"].startswith("gs://"):
                    gcs_uri = top_result["uri"]
                    parts = gcs_uri.replace("gs://", "").split("/", 1)
                    bucket = parts[0]
                    blob = parts[1] if len(parts) > 1 else ""
                    
                    print(f"Downloading from GCS: {gcs_uri}")
                    pdf_path = download_from_gcs(bucket, blob)
                    temp_file = pdf_path
                else:
                    # Use extracted content from search
                    document_content = top_result.get("extractive_answers", [""])[0] or top_result.get("content", "")
            
            else:
                raise ValueError("Must provide either document_id, gcs_uri, or search parameters (form_number, policy_number, insured_name)")
            
            # Process the document with Gemini
            if pdf_path:
                # Upload PDF to Gemini
                with open(pdf_path, 'rb') as f:
                    pdf_file = client.files.upload(file=f, config={'mime_type': 'application/pdf'})
                contents = [_get_extraction_prompt(), pdf_file]
            
            elif document_content:
                # Use text content directly
                prompt = f"""{_get_extraction_prompt()}
                
                Document Content:
                {document_content}
                """
                contents = [prompt]
            
            else:
                raise ValueError("No document content available to process")
            
            # Extract structured data with Gemini
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
            
            model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
            resp = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            
            # Parse and return JSON
            try:
                result = json.loads(resp.text)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError:
                return resp.text
        
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up temporary file: {temp_file}")
    
    return agent


def _get_extraction_prompt() -> str:
    """Get the standard extraction prompt for ACORD forms."""
    return """
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
