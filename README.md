# ACORD Local Extractor

A comprehensive Python application that extracts structured data from ACORD insurance forms using Google's Gemini AI. Features include local and cloud processing, intelligent search, and robust validation metrics.

## 🌟 Features

- 📄 **Local PDF Processing** - Extract from files on your machine
- ☁️ **Google Cloud Storage** - Process files directly from GCS buckets
- 🔍 **Vertex AI Search** - Search and retrieve documents from Data Store
- ✅ **Validation Metrics** - Measure accuracy, precision, recall, and F1 scores
- 📊 **Comparison Tools** - Compare extractions and track quality over time
- 🎯 **Structured Output** - Consistent JSON format with typed fields
- 🔄 **Batch Processing** - Validate multiple files at once
- 📈 **Quality Tracking** - Field-level error analysis and reporting

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Processing Methods](#processing-methods)
- [Validation & Metrics](#validation--quality-metrics)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

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
    
    class evaluation_metrics {
        +calculate_extraction_metrics(extracted, ground_truth) dict
        +compare_extractions(ext1, ext2) dict
        +calculate_field_metrics(data, field) dict
        +print_evaluation_report(metrics) void
    }
    
    create_agent --> gcs_utils : uses
    create_datastore_agent --> gcs_utils : uses
    create_datastore_agent --> datastore_utils : uses
```

### Module Structure

```
acord-local-extractor/
│
├── agents/                          # Agent modules
│   └── acord_extractor/
│       ├── agent.py                 # Main extraction agent (local + GCS)
│       ├── datastore_agent.py       # Data Store integration agent
│       ├── gcs_utils.py             # GCS helper functions
│       ├── datastore_utils.py       # Vertex AI Search helpers
│       └── evaluation_metrics.py    # Validation & metrics
│
├── run_local.py                     # Entry point: local file processing
├── run_gcs.py                       # Entry point: GCS file processing
├── run_datastore.py                 # Entry point: Data Store search + processing
├── run_validation.py                # Entry point: validation & metrics
├── create_ground_truth.py           # Utility: Create ground truth files
├── upload_to_gcs.py                 # Utility: Upload samples to GCS
│
├── .env                             # Environment configuration
├── requirements.txt                 # Python dependencies
├── samples/                         # Sample ACORD PDF files
└── ground_truth/                    # Ground truth data for validation
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Project with:
  - Gemini API enabled
  - Cloud Storage (optional)
  - Vertex AI Search (optional)

### Setup

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

**Validate extraction results:**
```powershell
python run_validation.py samples/140-Property-Acord-1.pdf
```

---

## Processing Methods

### 1. Local File Processing

Extract data from PDF files on your local filesystem.

**Script**: `run_local.py`

**Usage**:
```powershell
python run_local.py
```

**Features**:
- Direct PDF processing
- No cloud dependencies required
- Fastest method for single files

### 2. Google Cloud Storage Processing

Extract data from PDFs stored in GCS buckets.

**Script**: `run_gcs.py`

**Usage**:
```powershell
python run_gcs.py
```

**Features**:
- Automatic download from GCS
- Temporary file handling
- Automatic cleanup after processing
- Useful for processing files already in cloud storage

### 3. Vertex AI Search Data Store Processing

Search and extract data from PDFs indexed in Vertex AI Search.

**Script**: `run_datastore.py`

**Usage**:
```powershell
python run_datastore.py
```

**Features**:
- Search by form number, policy number, or insured name
- Direct document retrieval by ID
- Integration with enterprise search
- Supports GCS URI direct processing

---

## Vertex AI Search (Data Store) Setup

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

---

## Usage Examples

### Local File Processing

```python
from agents.acord_extractor.agent import create_agent

agent = create_agent()
result = agent({"pdf_path": "samples/140-Property-Acord-1.pdf"})
print(result)
```

### Google Cloud Storage Processing

```python
from agents.acord_extractor.agent import create_agent

agent = create_agent()
result = agent({
    "gcs_bucket": "your-bucket-name",
    "gcs_blob": "pdfs/acord-form.pdf"
})
print(result)
```

### Data Store Processing (Search by Form Number)

```python
from agents.acord_extractor.datastore_agent import create_datastore_agent

agent = create_datastore_agent()
result = agent({
    "form_number": "140",
    "insured_name": "John Doe"
})
print(result)
```

### Data Store Processing (Direct GCS URI)

```python
from agents.acord_extractor.datastore_agent import create_datastore_agent

agent = create_datastore_agent()
result = agent({
    "gcs_uri": "gs://your-bucket/path/to/acord.pdf"
})
print(result)
```

---

## Output Format

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

## Validation & Quality Metrics

### Overview

The application includes comprehensive validation capabilities to measure extraction accuracy, precision, recall, and F1 scores against ground truth data.

### Metrics Calculated

- **Accuracy**: Percentage of fields correctly extracted
- **Precision**: True Positives / (True Positives + False Positives)
- **Recall**: True Positives / (True Positives + False Negatives)
- **F1 Score**: Harmonic mean of Precision and Recall
- **Similarity Score**: String similarity between extracted and expected values

### Running Validation

#### Validate Single File

```powershell
python run_validation.py samples/140-Property-Acord-1.pdf
```

Output:
```
================================================================================
ACORD EXTRACTION EVALUATION REPORT
================================================================================

📊 Overall Metrics:
   Accuracy:    100.00%
   Precision:   100.00%
   Recall:      100.00%
   F1 Score:    100.00%
   Similarity:  100.00%

📈 Field Statistics:
   Total Fields:     12
   Correct Fields:   12 ✓
   Incorrect Fields: 0 ✗
```

#### Validate All Samples

```powershell
python run_validation.py --all
```

This will:
1. Find all ground truth files in `ground_truth/` directory
2. Extract data from corresponding PDFs
3. Calculate metrics for each file
4. Generate a summary report

#### Compare Two Extractions

Compare extraction results from two different PDFs:

```powershell
python run_validation.py --compare samples/file1.pdf samples/file2.pdf
```

This is useful for:
- Testing consistency across similar forms
- Comparing different extraction runs
- Validating changes to the extraction logic

### Creating Ground Truth Data

1. Create a JSON file in the `ground_truth/` directory
2. Name it identically to the PDF (e.g., `140-Property-Acord-1.json` for `140-Property-Acord-1.pdf`)
3. Manually verify and enter the correct extraction values

Example ground truth file:
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

### Programmatic Validation

Use the validation API in your own scripts:

```python
from agents.acord_extractor.evaluation_metrics import (
    calculate_extraction_metrics,
    compare_extractions,
    print_evaluation_report
)

# Validate against ground truth
metrics = calculate_extraction_metrics(extracted_data, ground_truth_data)
print_evaluation_report(metrics)

# Compare two extractions
comparison = compare_extractions(
    extraction1, 
    extraction2,
    label1="Method A",
    label2="Method B"
)
print(f"Agreement: {comparison['summary']['agreement_percentage']}")
```

### Metrics Interpretation

- **Accuracy ≥ 95%**: Excellent extraction quality
- **Accuracy 85-95%**: Good, minor issues
- **Accuracy 70-85%**: Acceptable, needs review
- **Accuracy < 70%**: Poor, requires investigation

**F1 Score** provides a balanced measure combining precision and recall, useful when you care about both false positives and false negatives.

For detailed documentation on validation and metrics, see [VALIDATION.md](VALIDATION.md).

---

## API Reference

### Agent Functions

#### `create_agent()`
Creates an agent for local and GCS file processing.

**Returns**: Agent function

**Parameters** (via agent call):
- `pdf_path` (str): Path to local PDF file
- `gcs_bucket` (str, optional): GCS bucket name (or from env `GCS_BUCKET_NAME`)
- `gcs_blob` (str): Path to file in GCS bucket

**Example**:
```python
from agents.acord_extractor.agent import create_agent

agent = create_agent()

# Local file
result = agent({"pdf_path": "samples/acord.pdf"})

# GCS file
result = agent({
    "gcs_bucket": "my-bucket",
    "gcs_blob": "pdfs/acord.pdf"
})
```

#### `create_datastore_agent()`
Creates an agent for Vertex AI Search Data Store processing.

**Returns**: Agent function

**Parameters** (via agent call):
- `form_number` (str, optional): ACORD form number (e.g., "140")
- `policy_number` (str, optional): Insurance policy number
- `insured_name` (str, optional): Name of insured party
- `document_id` (str, optional): Direct document ID in Data Store
- `gcs_uri` (str, optional): Direct GCS URI (e.g., "gs://bucket/file.pdf")

**Example**:
```python
from agents.acord_extractor.datastore_agent import create_datastore_agent

agent = create_datastore_agent()

# Search by form number
result = agent({"form_number": "140", "insured_name": "John Doe"})

# Direct GCS URI
result = agent({"gcs_uri": "gs://bucket/acord.pdf"})
```

### Utility Functions

#### GCS Utils (`agents/acord_extractor/gcs_utils.py`)

**`download_from_gcs(bucket_name, blob_name, destination_path=None)`**
- Downloads file from GCS to local temp file
- Returns: Local file path

**`list_files_in_gcs(bucket_name, prefix='')`**
- Lists files in GCS bucket with optional prefix filter
- Returns: List of blob names

**`upload_to_gcs(bucket_name, source_path, destination_blob_name)`**
- Uploads local file to GCS bucket
- Returns: GCS URI

#### Data Store Utils (`agents/acord_extractor/datastore_utils.py`)

**`search_datastore(project_id, location, data_store_id, search_query, max_results=5)`**
- Generic search function for Vertex AI Search
- Returns: List of search result dictionaries

**`get_document_content(project_id, location, data_store_id, document_id)`**
- Retrieves full document content by ID
- Returns: Document data dictionary

**`search_acord_forms(project_id, location, data_store_id, form_number=None, policy_number=None, insured_name=None, max_results=5)`**
- Specialized search for ACORD forms
- Returns: List of matching documents

#### Evaluation Metrics (`agents/acord_extractor/evaluation_metrics.py`)

**`calculate_extraction_metrics(extracted_data, ground_truth)`**
- Calculates comprehensive metrics for extraction
- Returns: Dictionary with accuracy, precision, recall, F1, field details

**`compare_extractions(extraction1, extraction2, label1="Extraction 1", label2="Extraction 2")`**
- Compares two extractions
- Returns: Dictionary with comparison metrics

**`print_evaluation_report(metrics, verbose=True)`**
- Prints formatted evaluation report
- Returns: None

---

## Troubleshooting

### Common Issues

**1. Authentication Error**
```
Error: API key not found
```
**Solution**: Ensure `GOOGLE_API_KEY` is set in `.env` file

**2. GCS Access Denied**
```
Error: 403 Forbidden
```
**Solution**: Run `gcloud auth application-default login`

**3. Data Store Not Found**
```
Error: 404 NOT_FOUND
```
**Solution**: Verify `DATASTORE_ID` and `PROJECT_ID` in `.env` file. Ensure data store indexing is complete.

**4. Import Errors**
```
ModuleNotFoundError: No module named 'google.genai'
```
**Solution**: 
- Activate virtual environment: `.\adk_accord\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`

**5. Model Not Found**
```
Error: 404 models/gemini-xxx is not found
```
**Solution**: The model name may have changed. Check Google's documentation for current model names.

**6. Low Validation Accuracy**
- Check field-by-field results in verbose output
- Review extraction prompt in agent.py
- Verify ground truth data is correct
- Check for formatting differences (currency, addresses)

### Getting Help

- Check [VALIDATION.md](VALIDATION.md) for metrics documentation
- Review ground truth examples in `ground_truth/` directory
- Ensure all environment variables are set correctly
- Check terminal output for specific error messages

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## License

[Add your license information here]

---

## Acknowledgments

- Powered by [Google Gemini AI](https://ai.google.dev/)
- Uses [Vertex AI Search](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction) for document retrieval
- Built with [Google Cloud Storage](https://cloud.google.com/storage)

#### 4. Run the Web Application