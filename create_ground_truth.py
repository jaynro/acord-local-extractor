"""
Helper script to create ground truth files from extraction results.

This script:
1. Extracts data from a PDF
2. Displays the result for manual review
3. Allows you to save it as ground truth after verification
"""
import os
import json
from agents.acord_extractor.agent import create_agent


def create_ground_truth(pdf_path: str):
    """
    Extract data from PDF and save as ground truth after user confirmation.
    
    Args:
        pdf_path: Path to the PDF file
    """
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    print(f"\n{'='*80}")
    print(f"Creating Ground Truth for: {pdf_path}")
    print(f"{'='*80}")
    
    # Extract data
    print("\n🔄 Running extraction...")
    agent = create_agent()
    result_str = agent({"pdf_path": pdf_path})
    extracted_data = json.loads(result_str)
    
    # Display result
    print("\n📄 Extracted Data:")
    print("="*80)
    print(json.dumps(extracted_data, indent=2))
    print("="*80)
    
    # Get confirmation
    print("\n⚠️  Please review the extracted data carefully!")
    print("   This will be used as ground truth for validation.")
    
    confirm = input("\nIs this data correct? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n❌ Ground truth creation cancelled.")
        print("   You can manually edit the extraction and save it to ground_truth/")
        return
    
    # Save to ground truth
    pdf_name = os.path.basename(pdf_path)
    json_name = pdf_name.replace(".pdf", ".json")
    gt_dir = "ground_truth"
    
    if not os.path.exists(gt_dir):
        os.makedirs(gt_dir)
        print(f"\n📁 Created directory: {gt_dir}/")
    
    gt_path = os.path.join(gt_dir, json_name)
    
    # Check if file exists
    if os.path.exists(gt_path):
        overwrite = input(f"\n⚠️  Ground truth file already exists: {gt_path}\n   Overwrite? (yes/no): ").strip().lower()
        if overwrite not in ['yes', 'y']:
            print("\n❌ Ground truth creation cancelled.")
            return
    
    # Save file
    with open(gt_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Ground truth saved to: {gt_path}")
    print(f"\n💡 You can now validate this file with:")
    print(f"   python run_validation.py {pdf_path}")


def batch_create_ground_truth():
    """Create ground truth for all sample PDFs."""
    samples_dir = "samples"
    
    if not os.path.exists(samples_dir):
        print(f"❌ Error: Samples directory not found: {samples_dir}")
        return
    
    pdf_files = [f for f in os.listdir(samples_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ Error: No PDF files found in {samples_dir}/")
        return
    
    print(f"\n{'='*80}")
    print(f"BATCH GROUND TRUTH CREATION")
    print(f"{'='*80}")
    print(f"\nFound {len(pdf_files)} PDF files")
    print("You will be prompted to review each extraction.\n")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{'='*80}")
        print(f"File {i}/{len(pdf_files)}")
        print(f"{'='*80}")
        
        pdf_path = os.path.join(samples_dir, pdf_file)
        create_ground_truth(pdf_path)
        
        if i < len(pdf_files):
            continue_batch = input("\nContinue to next file? (yes/no): ").strip().lower()
            if continue_batch not in ['yes', 'y']:
                print("\n❌ Batch processing stopped.")
                break
    
    print(f"\n{'='*80}")
    print("Batch processing complete!")
    print(f"{'='*80}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch":
            # Batch create for all samples
            batch_create_ground_truth()
        else:
            # Create for specific file
            pdf_path = sys.argv[1]
            create_ground_truth(pdf_path)
    else:
        # Interactive menu
        print("\n" + "="*80)
        print("GROUND TRUTH CREATION TOOL")
        print("="*80)
        print("\nOptions:")
        print("1. Create ground truth for single file")
        print("2. Create ground truth for all samples")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            pdf_path = input("Enter PDF path: ").strip()
            create_ground_truth(pdf_path)
        elif choice == "2":
            batch_create_ground_truth()
        else:
            print("Exiting...")
