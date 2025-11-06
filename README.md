# acord-local-extractor

A Python application that extracts structured data from ACORD insurance forms using Google's Gemini AI. Supports local file processing, Google Cloud Storage integration, and Vertex AI Search Data Store retrieval.

---

## Architecture Overview

### System Architecture

```mermaid
graph TB
    subgraph "Entry Points"
        A[run_local.py]
        B[run_gcs.py]
        C[run_datastore.py]
    end
    
    subgraph "Agent Layer"
        D[create_agent]
        E[create_datastore_agent]
    end
    
    subgraph "Utility Layer"
        F[gcs_utils.py]
        G[datastore_utils.py]
    end
    
    subgraph "External Services"
        H[Google Gemini AI]
        I[Google Cloud Storage]
        J[Vertex AI Search]
    end
    
    A --> D
    B --> D
    C --> E
    
    D --> F
    D --> H
    
    E --> F
    E --> G
    E --> H
    
    F --> I
    G --> J
```

### Data Flow: Local File Processing

```mermaid
sequenceDiagram
    participant User
    participant run_local
    participant create_agent
    participant Gemini
    
    User->>run_local: Execute script
    run_local->>create_agent: agent({"pdf_path": "..."})
    create_agent->>create_agent: Open local PDF file
    create_agent->>Gemini: Upload PDF + extraction prompt
    Gemini->>create_agent: Return JSON structure
    create_agent->>run_local: Return formatted JSON
    run_local->>User: Save to output.json
```

### Data Flow: GCS Processing

```mermaid
sequenceDiagram
    participant User
    participant run_gcs
    participant create_agent
    participant GCS
    participant Gemini
    
    User->>run_gcs: Execute script
    run_gcs->>create_agent: agent({"gcs_bucket": "...", "gcs_blob": "..."})
    create_agent->>GCS: download_from_gcs()
    GCS->>create_agent: Return temp file path
    create_agent->>Gemini: Upload PDF + extraction prompt
    Gemini->>create_agent: Return JSON structure
    create_agent->>create_agent: Cleanup temp file
    create_agent->>run_gcs: Return formatted JSON
    run_gcs->>User: Save to output_gcs.json
```

### Data Flow: Data Store Processing

```mermaid
sequenceDiagram
    participant User
    participant run_datastore
    participant Agent
    participant VertexSearch
    participant GCS
    participant Gemini
    
    User->>run_datastore: Execute script
    run_datastore->>Agent: agent({"form_number": "140"})
    Agent->>VertexSearch: search_acord_forms()
    VertexSearch->>Agent: Return document metadata + GCS URI
    Agent->>GCS: download_from_gcs()
    GCS->>Agent: Return temp file path
    Agent->>Gemini: Upload PDF + extraction prompt
    Gemini->>Agent: Return JSON structure
    Agent->>Agent: Cleanup temp file
    Agent->>run_datastore: Return formatted JSON
    run_datastore->>User: Save output
```

### Component Structure

```mermaid
classDiagram
    class create_agent {
        +genai.Client client
        +agent(inputs) str
        -upload_pdf_to_gemini()
        -extract_json_structure()
    }
    
    class create_datastore_agent {
        +genai.Client client
        +agent(inputs) str
        -search_documents()
        -retrieve_document()
        -extract_json_structure()
    }
    
    class gcs_utils {
        +download_from_gcs(bucket, blob) str
        +list_files_in_gcs(bucket, prefix) list
        +upload_to_gcs(bucket, source, dest) str
    }
    
    class datastore_utils {
        +search_datastore(project, location, store_id, query) list
        +get_document_content(project, location, store_id, doc_id) dict
        +search_acord_forms(form_number, policy, insured) list
    }
    
    create_agent --> gcs_utils : uses
    create_datastore_agent --> gcs_utils : uses
    create_datastore_agent --> datastore_utils : uses
```

---

## Quick Start

$env:GOOGLE_API_KEY=AIzaSyAt8n7knAZApNwEIG1JWfRFpsUEoIxxb-A

### Local Development

#### 1. Create and Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv adk_accord

# Activate the environment
.\adk_accord\Scripts\Activate.ps1
```

#### 2. Install Dependencies

```powershell
# Install main dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### 3. Configure Environment Variables

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env and add your Google API key and GCS bucket name
```

Required environment variables in `.env`:
```properties
GOOGLE_API_KEY=your-google-api-key
GCS_BUCKET_NAME=your-bucket-name
PROJECT_ID=your-project-id

# For Vertex AI Search (Data Store)
DATASTORE_ID=your-datastore-id
DATASTORE_LOCATION=global
```

#### 4. Set up Google Cloud Authentication

For Google Cloud Storage access, you need to authenticate:

**Option A: Application Default Credentials (Recommended for local development)**
```powershell
gcloud auth application-default login
```

**Option B: Service Account Key**
```powershell
# Download service account key from GCP Console
# Set environment variable
$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\service-account-key.json"
```

#### 5. Run the Application

**Process local PDF file:**
```powershell
python run_local.py
```

**Process PDF from Google Cloud Storage:**
```powershell
python run_gcs.py
```

**Process PDF from Vertex AI Search Data Store:**
```powershell
python run_datastore.py
```

### Vertex AI Search (Data Store) Setup

To use the Data Store retrieval feature, you need to set up Vertex AI Search:

#### 1. Create a Data Store

1. Go to [Vertex AI Search console](https://console.cloud.google.com/gen-app-builder/engines)
2. Click "Create Data Store"
3. Choose "Cloud Storage" as the data source
4. Select your GCS bucket with ACORD PDFs
5. Name your data store (use this as `DATASTORE_ID` in `.env`)
6. Wait for indexing to complete (can take 15-30 minutes)

#### 2. Upload ACORD PDFs to GCS

```powershell
# Upload PDFs to your GCS bucket
gcloud storage cp samples/*.pdf gs://your-bucket-name/acord-forms/
```

#### 3. Configure Data Store Settings

Update your `.env` file:
```properties
DATASTORE_ID=your-datastore-id-from-console
DATASTORE_LOCATION=global  # or your specific region
PROJECT_ID=your-project-id
```

#### 4. Test Data Store Integration

```powershell
python run_datastore.py
```

### Usage Examples

**Local File Processing:**
```python
from agents.acord_extractor.agent import create_agent

agent = create_agent()
result = agent({"pdf_path": "samples/140-Property-Acord-1.pdf"})
print(result)
```

**Google Cloud Storage Processing:**
```python
from agents.acord_extractor.agent import create_agent

agent = create_agent()
result = agent({
    "gcs_bucket": "your-bucket-name",
    "gcs_blob": "pdfs/acord-form.pdf"
})
print(result)
```

**Data Store Processing (Search by Form Number):**
```python
from agents.acord_extractor.datastore_agent import create_datastore_agent

agent = create_datastore_agent()
result = agent({
    "form_number": "140",
    "insured_name": "John Doe"
})
print(result)
```

**Data Store Processing (Direct GCS URI):**
```python
from agents.acord_extractor.datastore_agent import create_datastore_agent

agent = create_datastore_agent()
result = agent({
    "gcs_uri": "gs://your-bucket/path/to/acord.pdf"
})
print(result)
```

### Output Format

All processing methods return structured JSON with the following fields:

```json
{
    "named_insured": "John Doe",
    "secondary_insured": "",
    "alternate_name": "",
    "blanket_summary": [],
    "premises_information": [
        {
            "premises_number": "1",
            "street_address": "131 Any street, Columbus, OH, 43215",
            "building_number": "1",
            "coverage_information": [
                {
                    "Subject_of_insurance": "Building",
                    "amount": "$500000.00",
                    "deductible": "$1000.00"
                }
            ]
        }
    ]
}
```

#### 4. Run the Web Application