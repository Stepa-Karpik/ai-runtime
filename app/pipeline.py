from __future__ import annotations
import base64
import io
import re
from pathlib import Path


def extract_text(*, filename: str, content_base64: str) -> tuple[str, str]:
    data = base64.b64decode(content_base64)
    suffix = Path(filename).suffix.lower()
    if suffix in {'.txt', '.md', '.csv'}:
        return data.decode(errors='ignore'), 'text'
    if suffix == '.pdf':
        try:
            from pypdf import PdfReader
            text = '\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(data)).pages)
            return text, 'pdf'
        except Exception:
            return '', 'ocr_pending'
    if suffix == '.docx':
        from docx import Document
        return '\n'.join(paragraph.text for paragraph in Document(io.BytesIO(data)).paragraphs), 'docx'
    if suffix == '.xlsx':
        from openpyxl import load_workbook
        workbook = load_workbook(io.BytesIO(data), data_only=True)
        cells = [str(value) for sheet in workbook for row in sheet.iter_rows(values_only=True) for value in row if value is not None]
        return '\n'.join(cells), 'xlsx'
    if suffix == '.pptx':
        from pptx import Presentation
        texts = [shape.text for slide in Presentation(io.BytesIO(data)).slides for shape in slide.shapes if hasattr(shape, 'text')]
        return '\n'.join(texts), 'pptx'
    if suffix in {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp'}:
        return _ocr_image_bytes(data), 'ocr'
    return data.decode(errors='ignore'), 'binary-fallback'


def _ocr_image_bytes(data: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
        return pytesseract.image_to_string(Image.open(io.BytesIO(data)), lang='rus+eng')
    except Exception:
        return ''


def analyze_document_text(text: str) -> dict:
    normalized = ' '.join(text.split())
    sentences = [part.strip() for part in re.split(r'[.!?]', normalized) if part.strip()]
    dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', normalized)
    entities = re.findall(r'\b\d+(?:[.,]\d+)?\b', normalized)
    events = [
        {'title': 'Найденная дата из документа', 'starts_at': date, 'description': normalized[:240] or None}
        for date in dates
    ]
    return {'summary': '. '.join(sentences[:2]), 'entities': entities, 'dates': dates, 'events': events}
