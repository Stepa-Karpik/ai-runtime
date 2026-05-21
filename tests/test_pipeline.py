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


def test_semantic_summary_rejects_uppercase_course_words_as_people():
    text = (
        'МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ '
        'ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ '
        'ВЫСШЕГО ОБРАЗОВАНИЯ «ДОНСКОЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ» (ДГТУ) '
        'ОТЧЕТНАЯ РАБОТА в рамках курса АЛГОРИТМЫ И СТРУКТУРЫ ДАННЫХ '
        'г. Ростов-на-Дону 2026 год Лабораторные работы'
    )
    response = client.post('/api/v1/analyze-content', json={
        'filename': 'algorithms.txt',
        'content_base64': base64.b64encode(text.encode()).decode(),
    })

    payload = response.json()
    assert payload['summary'] == 'Лабораторная работа; Ростов-на-Дону; 2026 год; Алгоритмы и структуры данных; ДГТУ; Лабораторные работы'
    assert {'kind': 'company', 'name': 'ДГТУ'} in payload['structured_entities']
    assert {'kind': 'city', 'name': 'Ростов-на-Дону'} in payload['structured_entities']
    assert not [entity for entity in payload['structured_entities'] if entity['kind'] == 'person']


def test_person_extraction_strips_roles_and_rejects_business_phrases():
    text = 'Арендатор Карпов Степан. Карпов Степан Викторович. Ср Маржа Минимальная. Арендодатель Тимурова Елена Игоревна.'
    response = client.post('/api/v1/analyze-content', json={
        'filename': 'lease.txt',
        'content_base64': base64.b64encode(text.encode()).decode(),
    })
    people = [entity['name'] for entity in response.json()['structured_entities'] if entity['kind'] == 'person']

    assert 'Ср Маржа Минимальная' not in people
    assert 'Карпов Степан' in people
    assert 'Карпов Степан Викторович' in people
    assert 'Тимурова Елена Игоревна' in people


def test_lab_report_summary_does_not_add_unrelated_topics_or_fake_people():
    text = 'Отчетная работа в рамках курса АЛГОРИТМЫ И СТРУКТУРЫ ДАННЫХ. Алгоритм Бойера. Сортировка Шелла. Счёт дополнительной памяти. Ростов-на-Дону 2026 год ДГТУ.'
    response = client.post('/api/v1/analyze-content', json={
        'filename': 'lab.txt',
        'content_base64': base64.b64encode(text.encode()).decode(),
    })
    payload = response.json()
    assert payload['summary'] == 'Лабораторная работа; Ростов-на-Дону; 2026 год; Алгоритмы и структуры данных; ДГТУ'
    assert not [entity for entity in payload['structured_entities'] if entity['kind'] == 'person']
    assert {'kind': 'topic', 'name': 'Финансы'} not in payload['structured_entities']
    assert {'kind': 'topic', 'name': 'Медицина'} not in payload['structured_entities']
