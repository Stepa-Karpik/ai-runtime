import re
from uuid import uuid4
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="ai-runtime")
class JobCreate(BaseModel):
    document_id: str
    content_ref: str
class AnalyzeTextRequest(BaseModel):
    text: str
@app.get('/healthz')
def healthz(): return {'status': 'ok', 'service': 'ai-runtime'}
@app.post('/api/v1/jobs', status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate):
    return {'job_id': f'job_{uuid4().hex}', 'status': 'queued', **payload.model_dump()}
@app.post('/api/v1/analyze-text')
def analyze_text(payload: AnalyzeTextRequest):
    sentences = [part.strip() for part in re.split(r'[.!?]', payload.text) if part.strip()]
    dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', payload.text)
    entities = re.findall(r'\b\d+(?:[.,]\d+)?\b', payload.text)
    return {'summary': '. '.join(sentences[:2]), 'entities': entities, 'dates': dates}
