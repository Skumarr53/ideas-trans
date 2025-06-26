import pymupdf  # PyMuPDF
def extract_text_with_mupdf(pdf_path):
    """
    Extract text from a PDF using PyMuPDF by processing text blocks.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        str: Combined extracted text from all pages.
    """
    doc = pymupdf.open(pdf_path)
    all_pages_text = []
    
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        # Obtain detailed layout information as a dictionary.
        text_dict = page.get_text("dict")
        page_blocks = []
        
        for block in text_dict["blocks"]:
            # Some blocks might be images (without 'lines') so check for 'lines' attribute.
            if "lines" in block:
                # Collect all spans of text inside the block.
                block_lines = []
                for line in block["lines"]:
                    spans = [span["text"] for span in line["spans"]]
                    line_text = " ".join(spans)
                    block_lines.append(line_text)
                block_text = "\n".join(block_lines)
                print(block_text)
                if block_text.strip():
                    page_blocks.append(block_text.strip())
        
        # Optionally, join all blocks with a separator (e.g., newline, space, or custom delimiter)
        page_text = "\n\n".join(page_blocks)
        all_pages_text.append(page_text)
    
    doc.close()
    return "\n\n".join(all_pages_text)


if __name__ == "__main__":
    pdf_file = "/home/skumar/OneTime/2023_APHL-poster.pdf"  # Replace with your PDF file path
    extracted_text = extract_text_with_mupdf(pdf_file)
    print(extracted_text)