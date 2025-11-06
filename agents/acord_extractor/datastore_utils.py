"""
Vertex AI Search (Data Store) utility functions for searching and retrieving documents.
"""
import os
from typing import List, Dict, Any, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine


def search_datastore(
    project_id: str,
    location: str,
    data_store_id: str,
    search_query: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for documents in Vertex AI Search Data Store.
    
    Args:
        project_id: GCP project ID
        location: Location of the data store (e.g., 'global', 'us', 'eu')
        data_store_id: ID of the data store
        search_query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with document content and metadata
    """
    # Create a client
    client = discoveryengine.SearchServiceClient()
    
    # The full resource name of the search app serving config
    serving_config = (
        f"projects/{project_id}/locations/{location}"
        f"/collections/default_collection/dataStores/{data_store_id}"
        f"/servingConfigs/default_config"
    )
    
    # Prepare the search request
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=max_results,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True
            ),
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=3,
                max_extractive_segment_count=3,
            ),
        ),
    )
    
    # Execute the search
    response = client.search(request)
    
    # Parse results
    results = []
    for result in response.results:
        document = result.document
        
        # Extract document content
        doc_data = {
            "id": document.id,
            "name": document.name,
            "uri": getattr(document.derived_struct_data, 'link', '') if hasattr(document, 'derived_struct_data') else '',
            "content": "",
            "snippets": [],
            "extractive_answers": [],
            "metadata": {}
        }
        
        # Get document content
        if hasattr(document, 'derived_struct_data') and document.derived_struct_data:
            struct_data = dict(document.derived_struct_data)
            doc_data["content"] = struct_data.get('extractive_answers', [{}])[0].get('content', '') if 'extractive_answers' in struct_data else ''
            doc_data["metadata"] = {k: v for k, v in struct_data.items() if k not in ['extractive_answers', 'snippets']}
        
        # Get snippets
        if hasattr(result, 'document') and hasattr(result.document, 'derived_struct_data'):
            snippets_data = dict(result.document.derived_struct_data).get('snippets', [])
            doc_data["snippets"] = [s.get('snippet', '') for s in snippets_data if isinstance(s, dict)]
        
        # Get extractive answers
        if hasattr(result, 'document') and hasattr(result.document, 'derived_struct_data'):
            answers_data = dict(result.document.derived_struct_data).get('extractive_answers', [])
            doc_data["extractive_answers"] = [a.get('content', '') for a in answers_data if isinstance(a, dict)]
        
        results.append(doc_data)
    
    return results


def get_document_content(
    project_id: str,
    location: str,
    data_store_id: str,
    document_id: str
) -> Dict[str, Any]:
    """
    Retrieve full content of a specific document from Data Store.
    
    Args:
        project_id: GCP project ID
        location: Location of the data store
        data_store_id: ID of the data store
        document_id: ID of the document to retrieve
        
    Returns:
        Document content and metadata
    """
    client = discoveryengine.DocumentServiceClient()
    
    # Construct the document name
    document_name = (
        f"projects/{project_id}/locations/{location}"
        f"/collections/default_collection/dataStores/{data_store_id}"
        f"/branches/default_branch/documents/{document_id}"
    )
    
    # Get the document
    request = discoveryengine.GetDocumentRequest(name=document_name)
    document = client.get_document(request=request)
    
    # Extract content
    doc_data = {
        "id": document.id,
        "name": document.name,
        "content": "",
        "metadata": {}
    }
    
    # Get structured data
    if hasattr(document, 'struct_data') and document.struct_data:
        struct_data = dict(document.struct_data)
        doc_data["content"] = struct_data.get('content', '')
        doc_data["metadata"] = {k: v for k, v in struct_data.items() if k != 'content'}
    
    # Get JSON data if available
    if hasattr(document, 'json_data') and document.json_data:
        doc_data["json_content"] = document.json_data
    
    return doc_data


def search_acord_forms(
    project_id: str,
    location: str,
    data_store_id: str,
    form_number: Optional[str] = None,
    policy_number: Optional[str] = None,
    insured_name: Optional[str] = None,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for ACORD forms with specific criteria.
    
    Args:
        project_id: GCP project ID
        location: Location of the data store
        data_store_id: ID of the data store
        form_number: ACORD form number (e.g., "140", "125")
        policy_number: Insurance policy number
        insured_name: Name of the insured
        max_results: Maximum number of results
        
    Returns:
        List of matching ACORD forms
    """
    # Build search query
    query_parts = []
    if form_number:
        query_parts.append(f"ACORD {form_number}")
    if policy_number:
        query_parts.append(f"policy {policy_number}")
    if insured_name:
        query_parts.append(insured_name)
    
    search_query = " ".join(query_parts) if query_parts else "ACORD form"
    
    return search_datastore(
        project_id=project_id,
        location=location,
        data_store_id=data_store_id,
        search_query=search_query,
        max_results=max_results
    )


def create_datastore_tool_declaration():
    """
    Create a function declaration for Gemini to use Data Store search.
    
    Returns:
        Function declaration dict for Gemini API
    """
    return {
        "name": "search_acord_datastore",
        "description": "Search for ACORD insurance forms in the Vertex AI Search Data Store. Use this to find relevant ACORD documents based on form number, policy number, or insured name.",
        "parameters": {
            "type": "object",
            "properties": {
                "form_number": {
                    "type": "string",
                    "description": "ACORD form number (e.g., '140', '125', '126')"
                },
                "policy_number": {
                    "type": "string",
                    "description": "Insurance policy number"
                },
                "insured_name": {
                    "type": "string",
                    "description": "Name of the insured party"
                },
                "search_query": {
                    "type": "string",
                    "description": "Free-form search query for finding ACORD forms"
                }
            }
        }
    }
