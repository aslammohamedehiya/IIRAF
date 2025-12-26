import PyPDF2
import sys

# Extract Revised Abstract
try:
    with open(r'Reports\Revised_Abstract_2023AC05247.pdf', 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        print(f"=== REVISED ABSTRACT PDF ===")
        print(f"Total pages: {len(reader.pages)}\n")
        
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text()
        
        # Write to file to avoid encoding issues
        with open('abstract_content.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Abstract content saved to abstract_content.txt")
except Exception as e:
    print(f"Error reading abstract: {e}")

# Extract Style Template info
try:
    with open(r'Reports\Sumithra_midsem_viva.pdf', 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        print(f"\n=== STYLE TEMPLATE PDF ===")
        print(f"Total pages: {len(reader.pages)}\n")
        
        text = ""
        for i, page in enumerate(reader.pages[:3]):  # First 3 pages for structure
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text()
        
        with open('template_structure.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Template structure saved to template_structure.txt")
except Exception as e:
    print(f"Error reading template: {e}")

print("\nDone! Check the .txt files for content.")
