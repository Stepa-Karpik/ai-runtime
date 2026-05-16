from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analysis_job_can_be_created():
    response = client.post('/api/v1/jobs', json={'document_id': 'doc_1', 'content_ref': 'asset_1'})
    assert response.status_code == 201
    assert response.json()['status'] == 'queued'
