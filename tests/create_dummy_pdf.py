
import fitz
import os

def create_simple_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    # Add a title
    page.insert_text((100, 50), "RAG System User Manual", fontsize=24)
    page.insert_text((100, 100), "This is a test document for RAG filtering.")
    page.insert_text((100, 120), "It contains some sample text about HPPF-12 model torque values.")
    page.insert_text((100, 140), "The HPPF-12 torque value is 0.63 N.m.")
    page.insert_text((100, 160), "End of document.")
    doc.save(path)
    print(f"Created PDF at {path}")

if __name__ == "__main__":
    os.makedirs("tests/assets", exist_ok=True)
    create_simple_pdf("tests/assets/test_document.pdf")
