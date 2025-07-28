# Adobe India Hackathon - Connecting the Dots Challenge

## Round 1A: Document Outline Extraction

A high-performance PDF outline extraction system that identifies document structure (titles and hierarchical headings H1, H2, H3) using advanced multi-heuristic analysis.

### 🚀 Features

- **Multi-Heuristic Detection**: Doesn't rely solely on font sizes
- **Pattern Recognition**: Identifies numbered sections (1., 1.1, 1.1.1)
- **Formatting Analysis**: Detects bold text, ALL CAPS, Title Case
- **Position Awareness**: Uses spatial layout information
- **Fast Processing**: Optimized for <10s on 50-page PDFs
- **Multilingual Support**: Handles various languages including Japanese
- **Robust Error Handling**: Graceful failure modes

### 🏗️ Architecture

```
├── main.py                  # Entry point and batch processor
├── round1a/
│   └── outline_extractor.py # Core outline extraction logic
├── requirements.txt         # Python dependencies
└── Dockerfile               # Container setup
```

### 🔧 Technical Approach

Our solution uses a multi-layered approach for heading detection:

1. **Font Analysis**: Dynamic threshold calculation based on document font patterns
2. **Pattern Matching**: Regex-based detection of structured headings
3. **Spatial Analysis**: Position and layout-based heuristics
4. **Text Characteristics**: Case analysis, length validation, formatting flags
5. **Hierarchy Assignment**: Smart level assignment (H1, H2, H3) based on combined signals

### 📊 Performance Specifications

- **Execution Time**: ≤ 10 seconds for 50-page PDF
- **Model Size**: ≤ 200MB (uses lightweight PyMuPDF)
- **Memory Usage**: Optimized for 16GB RAM systems
- **CPU Architecture**: AMD64 (x86_64) compatible
- **Offline Operation**: No internet connectivity required

### 🐳 Docker Usage

Build the container:
```bash
docker build --platform linux/amd64 -t outline-extractor:latest .
```

Run the solution:
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  outline-extractor:latest
```

### 📝 Input/Output Format

**Input**: PDF files in `/app/input/` directory

**Output**: JSON files in `/app/output/` directory with structure:
```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 0 },
    { "level": "H2", "text": "Background", "page": 1 },
    { "level": "H3", "text": "Related Work", "page": 2 }
  ]
}
```

### 🧪 Testing

The solution handles various PDF types:
- Academic papers with numbered sections
- Reports with mixed formatting
- Presentations with title slides
- Technical documents with complex layouts
- Multilingual documents

### 🎯 Key Differentiators

1. **Beyond Font Size**: Uses 7 different heuristics for heading detection
2. **Pattern Intelligence**: Recognizes common academic/business document patterns
3. **Adaptive Thresholds**: Dynamically adjusts to document-specific font patterns
4. **Robust Hierarchy**: Smart H1/H2/H3 assignment based on multiple factors
5. **Performance Optimized**: Designed for hackathon time constraints

### 📚 Dependencies

- **PyMuPDF (fitz)**: Fast PDF processing and text extraction
- **NumPy**: Numerical operations for font analysis
- **Re**: Pattern matching and text analysis
- **JSON**: Output formatting
- **Pathlib**: Modern file path handling

### 🔍 Algorithm Details

The heading detection algorithm works in stages:

1. **Text Extraction**: Extract all text blocks with formatting metadata
2. **Font Analysis**: Calculate dynamic font size thresholds
3. **Multi-Heuristic Scoring**: Apply 6 different detection heuristics:
   - Font size relative to document average
   - Pattern matching (numbers, formatting)
   - Spatial position analysis
   - Text case analysis (CAPS, Title Case)
   - Text length validation
   - Bold/formatting flags
4. **Level Assignment**: Map detected headings to H1/H2/H3 hierarchy
5. **Output Formatting**: Generate clean JSON structure

### 🏆 Optimization Features

- **Early Exit**: Skip obviously non-heading text
- **Batch Processing**: Efficient multi-file handling
- **Memory Management**: Cleanup resources between documents
- **Caching**: Reuse analysis patterns across similar documents
- **Parallel Ready**: Architecture supports multi-threading

### 🌐 Multilingual Handling

The system supports various languages by:
- Unicode-aware text processing
- Pattern-agnostic font analysis
- Language-independent spatial heuristics
- Flexible regex patterns for different numbering systems

This solution balances accuracy with performance, ensuring reliable outline extraction across diverse PDF documents while meeting strict performance constraints.
