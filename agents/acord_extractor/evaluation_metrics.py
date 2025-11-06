"""
Evaluation metrics for ACORD form extraction validation.

This module provides functions to calculate accuracy, precision, recall, and F1 scores
for comparing extracted data against ground truth.
"""
import json
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher


def normalize_value(value: Any) -> str:
    """Normalize a value for comparison (remove extra spaces, convert to lowercase)."""
    if value is None:
        return ""
    
    # Convert to string and normalize
    str_value = str(value).strip().lower()
    
    # Remove dollar signs and commas for currency comparison
    str_value = str_value.replace("$", "").replace(",", "")
    
    return str_value


def string_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity between two strings using sequence matching.
    
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    if not str1 and not str2:
        return 1.0  # Both empty = perfect match
    if not str1 or not str2:
        return 0.0  # One empty, one not = no match
    
    norm1 = normalize_value(str1)
    norm2 = normalize_value(str2)
    
    return SequenceMatcher(None, norm1, norm2).ratio()


def compare_field(extracted: Any, ground_truth: Any, threshold: float = 0.9) -> Tuple[bool, float]:
    """
    Compare a single field between extracted and ground truth data.
    
    Args:
        extracted: Extracted field value
        ground_truth: Expected field value
        threshold: Similarity threshold for considering a match (default 0.9)
    
    Returns:
        Tuple of (is_match: bool, similarity_score: float)
    """
    # Handle None/empty cases
    if extracted is None and ground_truth is None:
        return True, 1.0
    if extracted is None or ground_truth is None:
        return False, 0.0
    
    # Handle lists (like blanket_summary)
    if isinstance(extracted, list) and isinstance(ground_truth, list):
        if len(extracted) == 0 and len(ground_truth) == 0:
            return True, 1.0
        if len(extracted) != len(ground_truth):
            return False, 0.0
        # For now, consider empty lists as matching
        return True, 1.0
    
    # Handle dictionaries
    if isinstance(extracted, dict) and isinstance(ground_truth, dict):
        total_fields = len(ground_truth)
        if total_fields == 0:
            return True, 1.0
        
        matching_fields = 0
        total_similarity = 0.0
        
        for key, gt_value in ground_truth.items():
            if key in extracted:
                is_match, similarity = compare_field(extracted[key], gt_value, threshold)
                if is_match:
                    matching_fields += 1
                total_similarity += similarity
        
        avg_similarity = total_similarity / total_fields
        is_match = avg_similarity >= threshold
        return is_match, avg_similarity
    
    # Handle strings and numbers
    similarity = string_similarity(str(extracted), str(ground_truth))
    is_match = similarity >= threshold
    
    return is_match, similarity


def calculate_field_metrics(extracted_data: Dict[str, Any], 
                           ground_truth: Dict[str, Any],
                           field_name: str) -> Dict[str, float]:
    """
    Calculate metrics for a specific field.
    
    Returns:
        Dictionary with accuracy, similarity, is_correct
    """
    extracted_value = extracted_data.get(field_name)
    ground_truth_value = ground_truth.get(field_name)
    
    is_correct, similarity = compare_field(extracted_value, ground_truth_value)
    
    return {
        "field": field_name,
        "is_correct": is_correct,
        "similarity": similarity,
        "extracted": extracted_value,
        "expected": ground_truth_value
    }


def calculate_extraction_metrics(extracted_data: Dict[str, Any],
                                 ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate comprehensive metrics for the entire extraction.
    
    Args:
        extracted_data: The extracted JSON data
        ground_truth: The expected/correct JSON data
    
    Returns:
        Dictionary containing:
        - accuracy: Overall field accuracy
        - field_metrics: Per-field accuracy details
        - total_fields: Total number of fields evaluated
        - correct_fields: Number of correctly extracted fields
        - avg_similarity: Average similarity score across all fields
    """
    
    # Define the fields to evaluate
    top_level_fields = ["named_insured", "secondary_insured", "alternate_name"]
    
    field_results = []
    
    # Evaluate top-level fields
    for field in top_level_fields:
        result = calculate_field_metrics(extracted_data, ground_truth, field)
        field_results.append(result)
    
    # Evaluate premises information
    extracted_premises = extracted_data.get("premises_information", [])
    ground_truth_premises = ground_truth.get("premises_information", [])
    
    premises_correct = 0
    premises_total = 0
    premises_similarity_sum = 0.0
    
    if len(extracted_premises) == len(ground_truth_premises):
        for i, (ext_prem, gt_prem) in enumerate(zip(extracted_premises, ground_truth_premises)):
            # Check premises number
            prem_num_result = calculate_field_metrics(ext_prem, gt_prem, "premises_number")
            field_results.append(prem_num_result)
            if prem_num_result["is_correct"]:
                premises_correct += 1
            premises_total += 1
            premises_similarity_sum += prem_num_result["similarity"]
            
            # Check street address
            addr_result = calculate_field_metrics(ext_prem, gt_prem, "street_address")
            field_results.append(addr_result)
            if addr_result["is_correct"]:
                premises_correct += 1
            premises_total += 1
            premises_similarity_sum += addr_result["similarity"]
            
            # Check building number
            bldg_result = calculate_field_metrics(ext_prem, gt_prem, "building_number")
            field_results.append(bldg_result)
            if bldg_result["is_correct"]:
                premises_correct += 1
            premises_total += 1
            premises_similarity_sum += bldg_result["similarity"]
            
            # Check coverage information
            ext_coverage = ext_prem.get("coverage_information", [])
            gt_coverage = gt_prem.get("coverage_information", [])
            
            if len(ext_coverage) == len(gt_coverage):
                for j, (ext_cov, gt_cov) in enumerate(zip(ext_coverage, gt_coverage)):
                    for cov_field in ["Subject_of_insurance", "amount", "deductible"]:
                        cov_result = calculate_field_metrics(ext_cov, gt_cov, cov_field)
                        cov_result["field"] = f"premises[{i}].coverage[{j}].{cov_field}"
                        field_results.append(cov_result)
                        if cov_result["is_correct"]:
                            premises_correct += 1
                        premises_total += 1
                        premises_similarity_sum += cov_result["similarity"]
    
    # Calculate overall metrics
    total_fields = len(field_results)
    correct_fields = sum(1 for r in field_results if r["is_correct"])
    total_similarity = sum(r["similarity"] for r in field_results)
    
    accuracy = correct_fields / total_fields if total_fields > 0 else 0.0
    avg_similarity = total_similarity / total_fields if total_fields > 0 else 0.0
    
    # Calculate precision, recall, and F1
    # True Positives: Fields correctly extracted
    # False Positives: Fields extracted but incorrect
    # False Negatives: Fields not extracted or missing
    
    true_positives = correct_fields
    false_positives = total_fields - correct_fields
    false_negatives = 0  # Assuming all fields are present in extraction
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 1.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "avg_similarity": avg_similarity,
        "total_fields": total_fields,
        "correct_fields": correct_fields,
        "incorrect_fields": total_fields - correct_fields,
        "field_metrics": field_results,
        "summary": {
            "accuracy_percentage": f"{accuracy * 100:.2f}%",
            "precision_percentage": f"{precision * 100:.2f}%",
            "recall_percentage": f"{recall * 100:.2f}%",
            "f1_score_percentage": f"{f1_score * 100:.2f}%",
            "avg_similarity_percentage": f"{avg_similarity * 100:.2f}%"
        }
    }


def compare_extractions(extraction1: Dict[str, Any],
                       extraction2: Dict[str, Any],
                       label1: str = "Extraction 1",
                       label2: str = "Extraction 2") -> Dict[str, Any]:
    """
    Compare two extractions to see how similar they are.
    Useful for comparing different extraction runs or methods.
    
    Args:
        extraction1: First extraction result
        extraction2: Second extraction result
        label1: Label for first extraction
        label2: Label for second extraction
    
    Returns:
        Dictionary with comparison metrics
    """
    # Calculate how similar the two extractions are
    metrics = calculate_extraction_metrics(extraction1, extraction2)
    
    return {
        "comparison": f"{label1} vs {label2}",
        "agreement_score": metrics["accuracy"],
        "similarity_score": metrics["avg_similarity"],
        "matching_fields": metrics["correct_fields"],
        "differing_fields": metrics["incorrect_fields"],
        "total_fields": metrics["total_fields"],
        "details": metrics["field_metrics"],
        "summary": {
            "agreement_percentage": f"{metrics['accuracy'] * 100:.2f}%",
            "similarity_percentage": f"{metrics['avg_similarity'] * 100:.2f}%"
        }
    }


def print_evaluation_report(metrics: Dict[str, Any], verbose: bool = True):
    """
    Print a formatted evaluation report.
    
    Args:
        metrics: Metrics dictionary from calculate_extraction_metrics
        verbose: If True, show per-field details
    """
    print("\n" + "=" * 80)
    print("ACORD EXTRACTION EVALUATION REPORT")
    print("=" * 80)
    
    print("\n📊 Overall Metrics:")
    print(f"   Accuracy:    {metrics['summary']['accuracy_percentage']}")
    print(f"   Precision:   {metrics['summary']['precision_percentage']}")
    print(f"   Recall:      {metrics['summary']['recall_percentage']}")
    print(f"   F1 Score:    {metrics['summary']['f1_score_percentage']}")
    print(f"   Similarity:  {metrics['summary']['avg_similarity_percentage']}")
    
    print(f"\n📈 Field Statistics:")
    print(f"   Total Fields:     {metrics['total_fields']}")
    print(f"   Correct Fields:   {metrics['correct_fields']} ✓")
    print(f"   Incorrect Fields: {metrics['incorrect_fields']} ✗")
    
    if verbose and metrics.get('field_metrics'):
        print(f"\n📋 Field-by-Field Results:")
        print("-" * 80)
        
        for field_metric in metrics['field_metrics']:
            status = "✓" if field_metric['is_correct'] else "✗"
            similarity = field_metric['similarity'] * 100
            
            print(f"\n{status} {field_metric['field']}")
            print(f"   Similarity: {similarity:.1f}%")
            
            if not field_metric['is_correct']:
                print(f"   Expected:   {field_metric['expected']}")
                print(f"   Extracted:  {field_metric['extracted']}")
    
    print("\n" + "=" * 80)
