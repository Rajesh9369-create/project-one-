"""Document extraction helpers.

This module intentionally separates extraction from carbon accounting. OCR/parser output
is only a suggestion and must be reviewed by the user before it reaches calculator.py.
"""
import io
import re
from pathlib import Path


def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()
    if name.endswith('.pdf'):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                return "\n".join((p.extract_text() or "") for p in pdf.pages)
        except Exception as exc:
            return f"PDF text extraction failed: {exc}"
    if name.endswith(('.txt', '.csv')):
        return data.decode('utf-8', errors='replace')
    if name.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        try:
            from PIL import Image
            import pytesseract
            return pytesseract.image_to_string(Image.open(io.BytesIO(data)))
        except Exception as exc:
            return f"Image OCR unavailable: {exc}"
    return "Unsupported file type"


def _number(patterns, text):
    for pattern in patterns:
        m = re.search(pattern, text, re.I | re.M)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except ValueError:
                pass
    return None


def suggest_fields(text: str, document_type: str) -> dict:
    """Best-effort extraction. Never silently treats a missing field as zero."""
    if document_type == 'Electricity bill':
        return {'electricity_kwh': _number([
            r'(?:units|consumption|energy consumption|kwh)\s*[:=]?\s*([\d,]+(?:\.\d+)?)',
            r'([\d,]+(?:\.\d+)?)\s*kwh\b'
        ], text)}
    if document_type == 'Diesel invoice':
        return {'diesel_litres': _number([
            r'(?:quantity|qty|litres|liters|volume)\s*[:=]?\s*([\d,]+(?:\.\d+)?)',
            r'([\d,]+(?:\.\d+)?)\s*l(?:itre|iter)s?\b'
        ], text)}
    if document_type == 'Feed invoice':
        return {'feed_kg': _number([
            r'(?:quantity|qty|weight|net weight)\s*[:=]?\s*([\d,]+(?:\.\d+)?)\s*(?:kg)?',
            r'([\d,]+(?:\.\d+)?)\s*kg\b'
        ], text)}
    if document_type == 'Production record':
        return {'production_kg': _number([
            r'(?:production|harvest|harvested|quantity)\s*[:=]?\s*([\d,]+(?:\.\d+)?)\s*(?:kg)?',
            r'([\d,]+(?:\.\d+)?)\s*kg\b'
        ], text)}
    return {}
