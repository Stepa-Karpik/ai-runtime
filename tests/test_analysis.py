from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analyze_text_extracts_basic_summary_entities_and_dates():
    response = client.post('/api/v1/analyze-text', json={'text': 'Договор аренды. Депозит 2000 евро. Оплатить до 2026-07-01.'})
    assert response.status_code == 200
    payload = response.json()
    assert 'Договор аренды' in payload['summary']
    assert '2000' in payload['entities']
    assert payload['dates'] == ['2026-07-01']
