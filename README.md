# PDF_TO_JSON_Convertor
A Python program that parses a PDF file and extracts its content into a well-structured JSON format. The extracted JSON preserves the hierarchical organization of the document 

# PDF Parsing and Structured JSON Extraction

This project extracts content from PDF files and converts it into a **well-structured JSON format**.  
The JSON output preserves **page-level hierarchy** and classifies content into:
- **paragraphs**
- **tables**
- **charts**
- **links**

The project uses:
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) → to extract text, headings, and links.
- [pdfplumber](https://github.com/jsvine/pdfplumber) → to extract tabular data.
- Python standard libraries (`json`, `os`, `re`) for processing.


# 1. Clone or download this repository
```bash```
git clone https://github.com/Sujal-Eda/PDF_TO_JSON_Convertor.git
cd PDF_TO_JSON_Convertor


# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # for Linux / macOS
venv\Scripts\activate      # for Windows


# 3. Install Dependencies
pip install pymupdf
pip install pdfplumber
pip install pandas
pip install PyMuPDF4LLM #incase you are using PyMuPDF4LLM


# 4.Run the Script 
python main.py --pdf "THE_PDF_WE_WISH_TO_EXTRACT" --out "output.json"


# 5.CHECK THE JSON OUTPUT.....


# References

While preparing this project, I reviewed:

YouTube tutorials (tool explanations only). there are plenty videos available

GitHub repositories (PDF extraction scripts)

Medium and StatsIO articles on PDF parsing strategies

