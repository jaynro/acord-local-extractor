"""
Validation script to evaluate ACORD extraction accuracy against ground truth data.

This script:
1. Loads ground truth data for sample PDFs
2. Runs extraction on the same PDFs
3. Compares results and calculates metrics
4. Generates evaluation reports
"""
import os
import json
from dotenv import load_dotenv
from agents.acord_extractor.agent import create_agent
from agents.acord_extractor.evaluation_metrics import (
    calculate_extraction_metrics,
    compare_extractions,
    print_evaluation_report
)

load_dotenv()


def load_ground_truth(pdf_name: str) -> dict:
    """Load ground truth data for a specific PDF."""
    ground_truth_dir = "ground_truth"
    json_name = pdf_name.replace(".pdf", ".json")
    gt_path = os.path.join(ground_truth_dir, json_name)
    
    if not os.path.exists(gt_path):
        raise FileNotFoundError(f"Ground truth file not found: {gt_path}")
    
    with open(gt_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_single_extraction(pdf_path: str, ground_truth_path: str = None):
    """
    Validate extraction for a single PDF against ground truth.
    
    Args:
        pdf_path: Path to the PDF file
        ground_truth_path: Optional path to ground truth JSON. If None, will auto-detect.
    """
    print(f"\n{'='*80}")
    print(f"Validating: {pdf_path}")
    print(f"{'='*80}")
    
    # Extract data
    print("\n🔄 Running extraction...")
    agent = create_agent()
    result_str = agent({"pdf_path": pdf_path})
    extracted_data = json.loads(result_str)
    
    # Load ground truth
    if ground_truth_path is None:
        pdf_name = os.path.basename(pdf_path)
        try:
            ground_truth_data = load_ground_truth(pdf_name)
        except FileNotFoundError as e:
            print(f"\n⚠️  {e}")
            print("Cannot validate without ground truth data.")
            return None
    else:
        with open(ground_truth_path, 'r', encoding='utf-8') as f:
            ground_truth_data = json.load(f)
    
    # Calculate metrics
    print("\n📊 Calculating metrics...")
    metrics = calculate_extraction_metrics(extracted_data, ground_truth_data)
    
    # Print report
    print_evaluation_report(metrics, verbose=True)
    
    return metrics


def validate_all_samples():
    """Validate all sample PDFs that have ground truth data."""
    samples_dir = "samples"
    ground_truth_dir = "ground_truth"
    
    if not os.path.exists(ground_truth_dir):
        print(f"⚠️  Ground truth directory not found: {ground_truth_dir}")
        print("Please create ground truth JSON files first.")
        return
    
    # Get all PDFs with ground truth
    gt_files = [f for f in os.listdir(ground_truth_dir) if f.endswith('.json')]
    
    if not gt_files:
        print(f"⚠️  No ground truth files found in {ground_truth_dir}/")
        return
    
    print(f"\n{'='*80}")
    print(f"BATCH VALIDATION - {len(gt_files)} files")
    print(f"{'='*80}")
    
    all_metrics = []
    
    for gt_file in gt_files:
        pdf_name = gt_file.replace(".json", ".pdf")
        pdf_path = os.path.join(samples_dir, pdf_name)
        
        if not os.path.exists(pdf_path):
            print(f"\n⚠️  PDF not found: {pdf_path}")
            continue
        
        gt_path = os.path.join(ground_truth_dir, gt_file)
        metrics = validate_single_extraction(pdf_path, gt_path)
        
        if metrics:
            all_metrics.append({
                "file": pdf_name,
                "metrics": metrics
            })
    
    # Print summary
    if all_metrics:
        print(f"\n\n{'='*80}")
        print("BATCH VALIDATION SUMMARY")
        print(f"{'='*80}\n")
        
        avg_accuracy = sum(m["metrics"]["accuracy"] for m in all_metrics) / len(all_metrics)
        avg_f1 = sum(m["metrics"]["f1_score"] for m in all_metrics) / len(all_metrics)
        avg_similarity = sum(m["metrics"]["avg_similarity"] for m in all_metrics) / len(all_metrics)
        
        print(f"📊 Average Metrics Across {len(all_metrics)} Files:")
        print(f"   Accuracy:   {avg_accuracy * 100:.2f}%")
        print(f"   F1 Score:   {avg_f1 * 100:.2f}%")
        print(f"   Similarity: {avg_similarity * 100:.2f}%")
        
        print(f"\n📋 Per-File Results:")
        print("-" * 80)
        for result in all_metrics:
            acc = result["metrics"]["accuracy"] * 100
            f1 = result["metrics"]["f1_score"] * 100
            print(f"{result['file']:30} | Accuracy: {acc:6.2f}% | F1: {f1:6.2f}%")
        
        print(f"\n{'='*80}")


def compare_two_extractions(pdf_path1: str, pdf_path2: str):
    """
    Compare extraction results from two different PDFs.
    Useful for testing consistency or comparing similar forms.
    """
    print(f"\n{'='*80}")
    print(f"Comparing Extractions")
    print(f"{'='*80}")
    
    agent = create_agent()
    
    print(f"\n🔄 Extracting from: {pdf_path1}")
    result1 = json.loads(agent({"pdf_path": pdf_path1}))
    
    print(f"🔄 Extracting from: {pdf_path2}")
    result2 = json.loads(agent({"pdf_path": pdf_path2}))
    
    # Compare
    comparison = compare_extractions(
        result1, 
        result2,
        label1=os.path.basename(pdf_path1),
        label2=os.path.basename(pdf_path2)
    )
    
    print(f"\n📊 Comparison Results:")
    print(f"   Agreement:  {comparison['summary']['agreement_percentage']}")
    print(f"   Similarity: {comparison['summary']['similarity_percentage']}")
    print(f"   Matching Fields:   {comparison['matching_fields']}")
    print(f"   Differing Fields:  {comparison['differing_fields']}")
    
    print(f"\n📋 Field Differences:")
    print("-" * 80)
    for detail in comparison['details']:
        if not detail['is_correct']:
            print(f"\n✗ {detail['field']}")
            print(f"   {os.path.basename(pdf_path1)}: {detail['expected']}")
            print(f"   {os.path.basename(pdf_path2)}: {detail['extracted']}")
    
    print(f"\n{'='*80}")
    
    return comparison


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # Validate all samples
            validate_all_samples()
        elif sys.argv[1] == "--compare" and len(sys.argv) >= 4:
            # Compare two PDFs
            compare_two_extractions(sys.argv[2], sys.argv[3])
        else:
            # Validate single file
            pdf_path = sys.argv[1]
            gt_path = sys.argv[2] if len(sys.argv) > 2 else None
            validate_single_extraction(pdf_path, gt_path)
    else:
        # Interactive menu
        print("\n" + "="*80)
        print("ACORD EXTRACTION VALIDATION")
        print("="*80)
        print("\nOptions:")
        print("1. Validate single file")
        print("2. Validate all samples")
        print("3. Compare two extractions")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            pdf_path = input("Enter PDF path: ").strip()
            validate_single_extraction(pdf_path)
        elif choice == "2":
            validate_all_samples()
        elif choice == "3":
            pdf1 = input("Enter first PDF path: ").strip()
            pdf2 = input("Enter second PDF path: ").strip()
            compare_two_extractions(pdf1, pdf2)
        else:
            print("Exiting...")
