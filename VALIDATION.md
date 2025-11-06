# Validation and Metrics Guide

## Overview

This document explains how to use the validation and metrics system to measure ACORD extraction quality.

## Quick Start

```powershell
# 1. Create ground truth for a sample
python create_ground_truth.py samples/140-Property-Acord-1.pdf

# 2. Validate the extraction
python run_validation.py samples/140-Property-Acord-1.pdf

# 3. Compare two extractions
python run_validation.py --compare samples/file1.pdf samples/file2.pdf
```

## Metrics Explained

### Accuracy
**Definition**: Percentage of fields that match the ground truth exactly (or within threshold).

**Formula**: `Correct Fields / Total Fields`

**Use Case**: Overall quality measure - how many fields are extracted correctly.

### Precision
**Definition**: Of all fields we extracted, how many are correct?

**Formula**: `True Positives / (True Positives + False Positives)`

**Use Case**: Measures false positive rate - if precision is low, we're extracting incorrect values.

### Recall
**Definition**: Of all fields that should be extracted, how many did we find?

**Formula**: `True Positives / (True Positives + False Negatives)`

**Use Case**: Measures missing data - if recall is low, we're missing fields.

### F1 Score
**Definition**: Harmonic mean of Precision and Recall.

**Formula**: `2 × (Precision × Recall) / (Precision + Recall)`

**Use Case**: Balanced metric that considers both false positives and false negatives.

### Similarity Score
**Definition**: Average string similarity across all fields (0.0 to 1.0).

**Formula**: Uses SequenceMatcher to compare strings after normalization.

**Use Case**: Measures "closeness" even when fields don't exactly match.

## Example Output

```
================================================================================
ACORD EXTRACTION EVALUATION REPORT
================================================================================

📊 Overall Metrics:
   Accuracy:    95.00%    ← 95% of fields are correct
   Precision:   95.00%    ← 95% of extracted values are correct
   Recall:      95.00%    ← We found 95% of all fields
   F1 Score:    95.00%    ← Balanced measure
   Similarity:  97.50%    ← Average similarity is 97.5%

📈 Field Statistics:
   Total Fields:     20
   Correct Fields:   19 ✓
   Incorrect Fields: 1 ✗

📋 Field-by-Field Results:
--------------------------------------------------------------------------------

✓ named_insured
   Similarity: 100.0%

✗ amount
   Similarity: 85.0%
   Expected:   $500000.00
   Extracted:  $50000.00    ← Missing a zero!
```

## Workflow

### 1. Create Ground Truth

#### Option A: From Extraction (Semi-Automated)
```powershell
# Extract data and save after manual review
python create_ground_truth.py samples/140-Property-Acord-1.pdf
```

This will:
1. Extract data from the PDF
2. Show you the extracted JSON
3. Ask for confirmation
4. Save to `ground_truth/` directory

#### Option B: Manual Creation
1. Create a JSON file in `ground_truth/`
2. Name it same as PDF: `140-Property-Acord-1.json`
3. Manually enter correct values

### 2. Run Validation

#### Single File
```powershell
python run_validation.py samples/140-Property-Acord-1.pdf
```

#### All Samples
```powershell
python run_validation.py --all
```

Output includes:
- Per-file accuracy, F1 score
- Average metrics across all files
- Summary table

### 3. Compare Extractions

```powershell
python run_validation.py --compare samples/file1.pdf samples/file2.pdf
```

Use cases:
- Compare before/after prompt changes
- Test consistency across similar forms
- Validate different extraction methods

## Programmatic Usage

### Calculate Metrics

```python
from agents.acord_extractor.evaluation_metrics import (
    calculate_extraction_metrics,
    print_evaluation_report
)

# Your extracted data
extracted_data = {
    "named_insured": "John Doe",
    # ... rest of fields
}

# Ground truth
ground_truth = {
    "named_insured": "John Doe",
    # ... rest of fields
}

# Calculate metrics
metrics = calculate_extraction_metrics(extracted_data, ground_truth)

# Print formatted report
print_evaluation_report(metrics, verbose=True)

# Access specific metrics
print(f"Accuracy: {metrics['accuracy']}")
print(f"F1 Score: {metrics['f1_score']}")
print(f"Correct: {metrics['correct_fields']}/{metrics['total_fields']}")
```

### Compare Two Extractions

```python
from agents.acord_extractor.evaluation_metrics import compare_extractions

comparison = compare_extractions(
    extraction1,
    extraction2,
    label1="Method A",
    label2="Method B"
)

print(f"Agreement: {comparison['summary']['agreement_percentage']}")
print(f"Matching fields: {comparison['matching_fields']}")
print(f"Differing fields: {comparison['differing_fields']}")
```

### Field-Level Validation

```python
from agents.acord_extractor.evaluation_metrics import compare_field

is_match, similarity = compare_field(
    extracted_value="$500000.00",
    ground_truth_value="$500000.00",
    threshold=0.9
)

print(f"Match: {is_match}, Similarity: {similarity}")
```

## Best Practices

### 1. Ground Truth Quality
- Manually verify all values before saving as ground truth
- Use consistent formatting (especially for currency)
- Review PDFs carefully - OCR can be ambiguous

### 2. Threshold Tuning
- Default threshold is 0.9 (90% similarity)
- Lower for fuzzy matching: `threshold=0.8`
- Higher for exact matching: `threshold=0.95`

### 3. Batch Validation
- Run validation after any prompt changes
- Track metrics over time
- Aim for consistent 95%+ accuracy

### 4. Debugging Low Scores

If accuracy is low:
1. Check field-by-field results in verbose output
2. Look for patterns (e.g., all currency fields wrong)
3. Review extraction prompt
4. Verify ground truth is correct

## Metric Thresholds

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Accuracy | ≥ 95% | 85-95% | 70-85% | < 70% |
| Precision | ≥ 95% | 85-95% | 70-85% | < 70% |
| Recall | ≥ 95% | 85-95% | 70-85% | < 70% |
| F1 Score | ≥ 95% | 85-95% | 70-85% | < 70% |
| Similarity | ≥ 95% | 90-95% | 80-90% | < 80% |

## Troubleshooting

### "Ground truth file not found"
Create ground truth first:
```powershell
python create_ground_truth.py samples/your-file.pdf
```

### "No matching documents found"
Check that:
- PDF file exists in `samples/` directory
- Ground truth exists in `ground_truth/` directory
- File names match (except .pdf vs .json extension)

### Low similarity on correct fields
- Check for formatting differences (spaces, case)
- Currency: ensure both use `$X.00` format
- The comparison normalizes strings, but exact format helps

## Advanced Usage

### Custom Metrics Calculation

```python
from agents.acord_extractor.evaluation_metrics import (
    calculate_field_metrics,
    string_similarity
)

# Calculate metrics for a specific field
field_metrics = calculate_field_metrics(
    extracted_data={"amount": "$500000.00"},
    ground_truth={"amount": "$500000.00"},
    field_name="amount"
)

# Calculate string similarity directly
similarity = string_similarity("John Doe", "john doe")
print(f"Similarity: {similarity}")  # 1.0 (normalized)
```

### Batch Processing with Custom Logic

```python
import os
import json
from agents.acord_extractor.agent import create_agent
from agents.acord_extractor.evaluation_metrics import calculate_extraction_metrics

agent = create_agent()
results = []

for pdf_file in os.listdir("samples"):
    if not pdf_file.endswith(".pdf"):
        continue
    
    # Extract
    pdf_path = os.path.join("samples", pdf_file)
    extracted = json.loads(agent({"pdf_path": pdf_path}))
    
    # Load ground truth
    gt_path = os.path.join("ground_truth", pdf_file.replace(".pdf", ".json"))
    if os.path.exists(gt_path):
        with open(gt_path) as f:
            ground_truth = json.load(f)
        
        # Calculate metrics
        metrics = calculate_extraction_metrics(extracted, ground_truth)
        results.append({
            "file": pdf_file,
            "accuracy": metrics["accuracy"],
            "f1_score": metrics["f1_score"]
        })

# Analyze results
avg_accuracy = sum(r["accuracy"] for r in results) / len(results)
print(f"Average accuracy: {avg_accuracy * 100:.2f}%")
```

## Summary

The validation system provides:
- ✅ Comprehensive metrics (accuracy, precision, recall, F1)
- ✅ Field-level error analysis
- ✅ Comparison between extractions
- ✅ Batch validation capabilities
- ✅ Programmatic API for custom workflows

Use these tools to ensure high-quality ACORD data extraction and catch regressions early.
