
import os
import json
import fitz  # PyMuPDF
import re
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class HeadingInfo:
    level: str
    text: str
    page: int
    font_size: float = 0.0
    font_name: str = ""
    bbox: Tuple[float, float, float, float] = None

class PDFOutlineExtractor:
    """
    Advanced PDF outline extractor that uses multiple heuristics
    to identify document structure without relying solely on font size.
    """

    def __init__(self):
        self.logger = self._setup_logger()

        # Font size thresholds (dynamic based on document analysis)
        self.font_size_thresholds = {}

        # Heading patterns (regex)
        self.heading_patterns = [
            r'^\d+\.\s+',  # 1. Chapter/Section
            r'^\d+\.\d+\.?\s+',  # 1.1 or 1.1. Subsection
            r'^\d+\.\d+\.\d+\.?\s+',  # 1.1.1 or 1.1.1. Sub-subsection
            r'^[A-Z][A-Za-z\s]{1,50}$',  # Title case headings
            r'^[A-Z\s]{3,50}$',  # ALL CAPS headings
            r'^Chapter\s+\d+',  # Chapter headings
            r'^Section\s+\d+',  # Section headings
        ]

    def _setup_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured outline from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with title and outline structure
        """
        try:
            doc = fitz.open(pdf_path)

            # Extract document title
            title = self._extract_title(doc)

            # Extract all text blocks with formatting information
            text_blocks = self._extract_text_blocks(doc)

            # Analyze font patterns to determine hierarchy
            font_analysis = self._analyze_fonts(text_blocks)

            # Identify headings using multiple heuristics
            headings = self._identify_headings(text_blocks, font_analysis)

            # Assign heading levels (H1, H2, H3)
            structured_headings = self._assign_heading_levels(headings)

            # Format output
            outline = [
                {
                    "level": h.level,
                    "text": h.text.strip(),
                    "page": h.page
                }
                for h in structured_headings
            ]

            doc.close()

            return {
                "title": title,
                "outline": outline
            }

        except Exception as e:
            self.logger.error(f"Error processing {pdf_path}: {str(e)}")
            raise

    def _extract_title(self, doc: fitz.Document) -> str:
        """Extract document title from metadata or first page."""
        # Try metadata first
        metadata = doc.metadata
        if metadata.get('title'):
            return metadata['title']

        # Try first page - look for largest font size text
        page = doc[0]
        blocks = page.get_text("dict")

        max_font_size = 0
        title_text = "Untitled Document"

        for block in blocks.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        font_size = span.get("size", 0)
                        text = span.get("text", "").strip()

                        if font_size > max_font_size and len(text) > 3:
                            max_font_size = font_size
                            title_text = text

        return title_text

    def _extract_text_blocks(self, doc: fitz.Document) -> List[Dict]:
        """Extract text blocks with detailed formatting information."""
        all_blocks = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")

            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                all_blocks.append({
                                    "text": text,
                                    "page": page_num,
                                    "font_size": span.get("size", 0),
                                    "font_name": span.get("font", ""),
                                    "bbox": span.get("bbox", (0, 0, 0, 0)),
                                    "flags": span.get("flags", 0)  # Bold, italic flags
                                })

        return all_blocks

    def _analyze_fonts(self, text_blocks: List[Dict]) -> Dict:
        """Analyze font patterns to understand document hierarchy."""
        font_sizes = [block["font_size"] for block in text_blocks if block["font_size"] > 0]
        font_names = [block["font_name"] for block in text_blocks]

        if not font_sizes:
            return {"font_thresholds": {}}

        # Calculate percentiles for font size thresholds
        import numpy as np
        font_sizes_sorted = sorted(set(font_sizes), reverse=True)

        thresholds = {}
        if len(font_sizes_sorted) >= 3:
            thresholds["H1"] = font_sizes_sorted[0]  # Largest
            thresholds["H2"] = font_sizes_sorted[1]  # Second largest
            thresholds["H3"] = font_sizes_sorted[2] if len(font_sizes_sorted) > 2 else font_sizes_sorted[1]
        elif len(font_sizes_sorted) == 2:
            thresholds["H1"] = font_sizes_sorted[0]
            thresholds["H2"] = font_sizes_sorted[1]
            thresholds["H3"] = font_sizes_sorted[1]
        else:
            # Single font size document
            base_size = font_sizes_sorted[0]
            thresholds["H1"] = base_size
            thresholds["H2"] = base_size
            thresholds["H3"] = base_size

        return {
            "font_thresholds": thresholds,
            "common_fonts": list(set(font_names)),
            "avg_font_size": np.mean(font_sizes)
        }

    def _identify_headings(self, text_blocks: List[Dict], font_analysis: Dict) -> List[HeadingInfo]:
        """Identify headings using multiple heuristics."""
        headings = []
        thresholds = font_analysis.get("font_thresholds", {})
        avg_font_size = font_analysis.get("avg_font_size", 12)

        for block in text_blocks:
            text = block["text"]
            font_size = block["font_size"]
            page = block["page"]

            # Skip very short text or common words
            if len(text) < 3 or text.lower() in ["the", "and", "or", "but", "in", "on", "at"]:
                continue

            is_heading = False
            heading_score = 0

            # Heuristic 1: Font size analysis
            if font_size > avg_font_size * 1.2:  # 20% larger than average
                heading_score += 3
                is_heading = True

            # Heuristic 2: Pattern matching
            for pattern in self.heading_patterns:
                if re.match(pattern, text):
                    heading_score += 2
                    is_heading = True
                    break

            # Heuristic 3: Position analysis (beginning of line/block)
            bbox = block["bbox"]
            if bbox[0] < 100:  # Left margin (assuming typical document)
                heading_score += 1

            # Heuristic 4: Text characteristics
            if text.isupper() and len(text) > 5:  # ALL CAPS
                heading_score += 2
                is_heading = True
            elif text.istitle():  # Title Case
                heading_score += 1

            # Heuristic 5: Length check (headings are usually concise)
            if len(text) < 80:  # Reasonable heading length
                heading_score += 1

            # Heuristic 6: Bold text (flags analysis)
            flags = block.get("flags", 0)
            if flags & 2**4:  # Bold flag
                heading_score += 2
                is_heading = True

            # Decision threshold based on combined score
            if is_heading and heading_score >= 3:
                headings.append(HeadingInfo(
                    level="",  # Will be assigned later
                    text=text,
                    page=page,
                    font_size=font_size,
                    font_name=block["font_name"],
                    bbox=bbox
                ))

        return headings

    def _assign_heading_levels(self, headings: List[HeadingInfo]) -> List[HeadingInfo]:
        """Assign H1, H2, H3 levels to identified headings."""
        if not headings:
            return headings

        # Sort by font size (descending) to understand hierarchy
        font_sizes = sorted(set([h.font_size for h in headings]), reverse=True)

        # Create level mapping based on font sizes
        level_mapping = {}
        if len(font_sizes) >= 3:
            level_mapping[font_sizes[0]] = "H1"
            level_mapping[font_sizes[1]] = "H2"
            level_mapping[font_sizes[2]] = "H3"
            # Map remaining sizes to H3
            for size in font_sizes[3:]:
                level_mapping[size] = "H3"
        elif len(font_sizes) == 2:
            level_mapping[font_sizes[0]] = "H1"
            level_mapping[font_sizes[1]] = "H2"
        else:
            # All same size - use pattern analysis
            level_mapping[font_sizes[0]] = "H1"

        # Assign levels with additional pattern-based refinement
        for heading in headings:
            base_level = level_mapping.get(heading.font_size, "H3")

            # Refine based on patterns
            text = heading.text
            if re.match(r'^\d+\.\s+', text):  # 1. Main section
                heading.level = "H1"
            elif re.match(r'^\d+\.\d+\.?\s+', text):  # 1.1 Subsection
                heading.level = "H2"
            elif re.match(r'^\d+\.\d+\.\d+\.?\s+', text):  # 1.1.1 Sub-subsection
                heading.level = "H3"
            else:
                heading.level = base_level

        # Sort by page and position for final output
        headings.sort(key=lambda h: (h.page, h.bbox[1] if h.bbox else 0))

        return headings

def process_single_pdf(input_path: str, output_path: str):
    """Process a single PDF file."""
    extractor = PDFOutlineExtractor()
    result = extractor.extract_outline(input_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def main():
    """Main function for Round 1A processing."""
    input_dir = "/app/input"
    output_dir = "/app/output"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process all PDF files in input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.pdf', '.json')
            output_path = os.path.join(output_dir, output_filename)

            print(f"Processing: {filename}")
            start_time = time.time()

            try:
                process_single_pdf(input_path, output_path)
                elapsed_time = time.time() - start_time
                print(f"Completed: {filename} in {elapsed_time:.2f}s")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()
