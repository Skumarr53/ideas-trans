"""
Robust block-wise PDF text extraction for complex layouts
Author: ChatGPT
Date: 2025-06-26
Description: Modularized Python code for block-wise extraction from PDFs with complex layouts (columns, tables, etc.).
"""
import os
from typing import List, Dict
import pandas as pd
from pathlib import Path

# Core libraries for PDF extraction
import fitz  # PyMuPDF
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer, LTTextBoxHorizontal

def extract_blocks_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extracts text blocks from the PDF using PyMuPDF.
    Returns a list of blocks with their bounding box and text content.
    """
    blocks = []
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, 1):
            for b in page.get_text("blocks"):
                x0, y0, x1, y1, text, block_no, block_type = (
                    b[0], b[1], b[2], b[3], b[4], b[5], b[6] if len(b) > 6 else None
                )
                if text.strip():  # Skip empty
                    blocks.append({
                        "page": page_num,
                        "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                        "text": text.strip(),
                        "block_no": block_no,
                        "block_type": block_type
                    })
    return blocks

def extract_blocks_pdfminer(pdf_path: str) -> List[Dict]:
    """
    Alternative: Extract block-wise text using pdfminer for richer layout info.
    Returns a list of blocks per page.
    """
    laparams = LAParams(detect_vertical=True, all_texts=True)
    blocks = []
    for page_num, page_layout in enumerate(extract_pages(pdf_path, laparams=laparams), 1):
        for element in page_layout:
            if isinstance(element, (LTTextContainer, LTTextBoxHorizontal)):
                bbox = element.bbox  # (x0, y0, x1, y1)
                text = element.get_text().strip()
                if text:
                    blocks.append({
                        "page": page_num,
                        "x0": bbox[0], "y0": bbox[1], "x1": bbox[2], "y1": bbox[3],
                        "text": text,
                        "type": type(element).__name__
                    })
    return blocks

def pdf_blocks_to_dataframe(blocks: List[Dict], filename: str) -> pd.DataFrame:
    """
    Convert list of block dicts to a Pandas DataFrame for easier downstream processing.
    Adds the source filename and block id for traceability.
    """
    df = pd.DataFrame(blocks)
    df["filename"] = Path(filename).name
    df["block_id"] = [f"{Path(filename).stem}_p{row['page']}_b{i}" for i, row in enumerate(blocks)]
    cols = ["filename", "block_id", "page", "x0", "y0", "x1", "y1", "text"]
    df = df[[c for c in cols if c in df.columns]]
    return df

def process_pdfs(pdf_files: List[str], engine: str = "pymupdf") -> pd.DataFrame:
    """
    Batch process a list of PDF files, extracting block-wise text.
    engine: "pymupdf" (fast, robust) or "pdfminer" (more structure info).
    Returns: concatenated DataFrame for all PDFs.
    """
    all_dfs = []
    for pdf_path in pdf_files:
        if engine == "pdfminer":
            blocks = extract_blocks_pdfminer(pdf_path)
        else:
            blocks = extract_blocks_from_pdf(pdf_path)
        df = pdf_blocks_to_dataframe(blocks, pdf_path)
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)

def demo_blockwise_extraction():
    # Place sample file paths here
    pdfs = [
        "/mnt/data/20250114229408.pdf",
        "/mnt/data/20250616878217.pdf",
        "/mnt/data/20250616915293.pdf",
    ]
    df = process_pdfs(pdfs, engine="pymupdf")
    # Show sample output
    print(df.head(10).to_string())
    return df

if __name__ == "__main__":
    # Demo: run on sample files
    demo_blockwise_extraction()
