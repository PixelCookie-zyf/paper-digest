import logging
import os
import tempfile
import requests

logger = logging.getLogger(__name__)


def download_pdf(pdf_url: str, save_dir: str | None = None) -> str | None:
    """Download a PDF from URL and return local file path."""
    if not pdf_url:
        return None
    try:
        logger.info(f"  Downloading PDF: {pdf_url}")
        resp = requests.get(pdf_url, timeout=120)
        resp.raise_for_status()

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        else:
            save_dir = tempfile.mkdtemp()

        filename = pdf_url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        path = os.path.join(save_dir, filename)

        with open(path, "wb") as f:
            f.write(resp.content)
        logger.info(f"  PDF saved to: {path}")
        return path
    except Exception as e:
        logger.warning(f"  PDF download failed: {e}")
        return None


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract full text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("  PyMuPDF not installed, skipping PDF text extraction")
        return ""

    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        total_pages = len(doc)
        doc.close()

        full_text = "\n".join(text_parts).strip()
        logger.info(f"  Extracted {len(full_text)} chars from {total_pages} pages")
        return full_text
    except Exception as e:
        logger.warning(f"  PDF text extraction failed: {e}")
        return ""


def fetch_paper_content(pdf_url: str | None) -> str:
    """Download PDF and extract full text. Returns empty string on any failure."""
    if not pdf_url:
        logger.info("  No PDF URL, skipping content fetch")
        return ""

    pdf_path = download_pdf(pdf_url)
    if not pdf_path:
        return ""

    text = extract_text_from_pdf(pdf_path)

    # Clean up temp file
    try:
        os.remove(pdf_path)
    except OSError:
        pass

    return text
