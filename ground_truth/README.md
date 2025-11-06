# Ground Truth Data

This directory contains the expected/correct extraction results for sample ACORD PDF files.

## Purpose

Ground truth files are used to:
- Validate extraction accuracy
- Calculate precision, recall, and F1 scores
- Compare extraction results across different runs
- Ensure consistent extraction quality

## File Format

Each ground truth file should:
- Be named identically to its corresponding PDF (e.g., `140-Property-Acord-1.json` for `140-Property-Acord-1.pdf`)
- Contain the expected JSON structure with all fields populated correctly
- Use the same schema as the extraction output

## Example Structure

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

## Creating Ground Truth Files

1. Manually review the PDF and extract the correct information
2. Create a JSON file with the same name as the PDF (but with `.json` extension)
3. Ensure all fields match the expected schema
4. Verify currency formatting (`$X.00`) and string values

## Usage

See `run_validation.py` for how to validate extractions against ground truth data.
