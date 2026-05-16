import re
from typing import Annotated
from fastapi import Depends,FastAPI,status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_session
from app.repositories import AiRepository
app=FastAPI(title='ai-runtime'); SessionDep=Annotated[Session,Depends(get_session)]
class JobCreate(BaseModel): document_id:str; content_ref:str
class AnalyzeTextRequest(BaseModel): text:str
@app.get('/healthz')
def healthz(): return {'status':'ok','service':'ai-runtime'}
@app.post('/api/v1/jobs',status_code=status.HTTP_201_CREATED)
def create_job(payload:JobCreate,session:SessionDep):
    job=AiRepository(session).create_job(**payload.model_dump()); return {'job_id':job.id,'status':job.status,'document_id':job.document_id,'content_ref':job.content_ref}
@app.post('/api/v1/analyze-text')
def analyze_text(payload:AnalyzeTextRequest):
    sentences=[p.strip() for p in re.split(r'[.!?]',payload.text) if p.strip()]; dates=re.findall(r'\b\d{4}-\d{2}-\d{2}\b',payload.text); entities=re.findall(r'\b\d+(?:[.,]\d+)?\b',payload.text); return {'summary':'. '.join(sentences[:2]),'entities':entities,'dates':dates}
