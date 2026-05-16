from uuid import uuid4
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="ai-runtime")
class JobCreate(BaseModel):
    document_id: str
    content_ref: str
@app.get('/healthz')
def healthz(): return {'status': 'ok', 'service': 'ai-runtime'}
@app.post('/api/v1/jobs', status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate):
    return {'job_id': f'job_{uuid4().hex}', 'status': 'queued', **payload.model_dump()}
