import base64
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)


def test_analyze_content_extracts_text_and_events_from_plain_text():
    response = client.post('/api/v1/analyze-content', json={
        'filename': 'invoice.txt',
        'content_base64': base64.b64encode('Счет. Оплатить до 2026-07-01. Сумма 2000 евро.'.encode()).decode(),
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload['extraction_method'] == 'text'
    assert '2000' in payload['entities']
    assert payload['events'][0]['starts_at'] == '2026-07-01'

def test_analyze_content_uses_ocr_fallback_for_images(monkeypatch):
    monkeypatch.setattr('app.pipeline._ocr_image_bytes', lambda data: 'Прием 2026-08-10')
    response = client.post('/api/v1/analyze-content', json={
        'filename': 'scan.png',
        'content_base64': base64.b64encode(b'fake-image').decode(),
    })
    assert response.json()['extraction_method'] == 'ocr'
    assert response.json()['events'][0]['starts_at'] == '2026-08-10'
