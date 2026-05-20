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
    dates = sorted(set(re.findall(r'\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b', normalized)))
    structured_entities = _extract_structured_entities(normalized)
    topic_entities = _extract_topics(normalized)
    entities = sorted({entity['name'] for entity in structured_entities} | set(topic_entities))
    events = [{'title': 'Найденная дата из документа', 'starts_at': date, 'description': normalized[:240] or None} for date in dates]
    return {
        'summary': '. '.join(sentences[:2]) or normalized[:320],
        'entities': entities,
        'structured_entities': structured_entities + [{'kind': 'topic', 'name': topic} for topic in topic_entities],
        'dates': dates,
        'events': events,
    }


def _extract_structured_entities(text: str) -> list[dict[str, str]]:
    entities: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(kind: str, name: str) -> None:
        clean = _clean_name(name)
        if len(clean) < 3:
            return
        key = (kind, clean.lower())
        if key not in seen:
            seen.add(key)
            entities.append({'kind': kind, 'name': clean})

    for match in re.finditer(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\b', text):
        add('person', match.group(0))
    for match in re.finditer(r'\b(?:ООО|АО|ПАО|ЗАО|ИП|ОАО)\s+[«"]?[^,.;:\n]{2,80}', text):
        add('company', match.group(0))
    for match in re.finditer(r'\b(?:проект|Project)\s+[«"]?[^,.;:\n]{2,70}', text, re.IGNORECASE):
        add('project', match.group(0))
    for match in re.finditer(r'\b\d[\d\s.,]{1,18}\s*(?:₽|руб\.?|евро|eur|€|usd|\$)\b', text, re.IGNORECASE):
        add('finance', match.group(0))
    for match in re.finditer(r'\b(?:сумма|залог|депозит|штраф|оплата|сч[её]т|налог)[^,.;:\n]{0,60}', text, re.IGNORECASE):
        add('finance', match.group(0))
    return entities


def _extract_topics(text: str) -> list[str]:
    topics = []
    rules = {
        'Договор': r'\bдоговор\b',
        'Недвижимость': r'\b(?:квартир|аренд|недвижим|помещени)\w*',
        'Медицина': r'\b(?:медицин|клиник|врач|анализ|при[её]м)\w*',
        'Налоги': r'\b(?:налог|деклараци|фнс)\w*',
        'Страхование': r'\b(?:страхов|полис)\w*',
        'Финансы': r'\b(?:сч[её]т|оплат|банк|выписк|плат[её]ж)\w*',
    }
    for name, pattern in rules.items():
        if re.search(pattern, text, re.IGNORECASE):
            topics.append(name)
    return topics


def _clean_name(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip(' «"”.,;:()[]')).strip()
