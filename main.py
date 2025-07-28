#!/usr/bin/env python3
"""
Adobe India Hackathon - Round 1A: Document Outline Extraction
Main processing script that handles batch PDF processing
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from round1a.outline_extractor import PDFOutlineExtractor

def validate_environment():
    """Validate that required directories exist."""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        return False

    output_dir.mkdir(exist_ok=True, parents=True)
    return True

def process_all_pdfs():
    """Process all PDF files in the input directory."""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in input directory")
        return

    print(f"Found {len(pdf_files)} PDF file(s) to process")

    extractor = PDFOutlineExtractor()
    total_start_time = time.time()

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        start_time = time.time()

        try:
            # Extract outline
            result = extractor.extract_outline(str(pdf_file))

            # Save result
            output_file = output_dir / f"{pdf_file.stem}.json"

            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            elapsed_time = time.time() - start_time
            print(f"✓ Completed: {pdf_file.name} in {elapsed_time:.2f}s")
            print(f"  - Title: {result['title']}")
            print(f"  - Headings found: {len(result['outline'])}")

            # Performance check (should be under 10s for 50-page PDF)
            if elapsed_time > 10:
                print(f"⚠️  Warning: Processing took {elapsed_time:.2f}s (>10s threshold)")

        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {str(e)}")
            import traceback
            traceback.print_exc()

    total_elapsed = time.time() - total_start_time
    print(f"\n🎉 Batch processing completed in {total_elapsed:.2f}s")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PDF Outline Extractor - Round 1A")
    parser.add_argument("--input", help="Input directory path", default="/app/input")
    parser.add_argument("--output", help="Output directory path", default="/app/output")
    parser.add_argument("--single", help="Process single PDF file")

    args = parser.parse_args()

    print("Adobe India Hackathon - Round 1A: Document Outline Extraction")
    print("=" * 60)

    if not validate_environment():
        sys.exit(1)

    if args.single:
        # Process single file mode (for testing)
        extractor = PDFOutlineExtractor()
        result = extractor.extract_outline(args.single)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Batch processing mode
        process_all_pdfs()

if __name__ == "__main__":
    main()
