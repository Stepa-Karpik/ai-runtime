from typing import Annotated
from fastapi import Depends,FastAPI,status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_session
from app.pipeline import analyze_document_text, extract_text
from app.repositories import AiRepository
app=FastAPI(title='ai-runtime'); SessionDep=Annotated[Session,Depends(get_session)]
class JobCreate(BaseModel): document_id:str; content_ref:str
class AnalyzeTextRequest(BaseModel): text:str
class AnalyzeContentRequest(BaseModel): filename:str; content_base64:str
@app.get('/healthz')
def healthz(): return {'status':'ok','service':'ai-runtime'}
@app.post('/api/v1/jobs',status_code=status.HTTP_201_CREATED)
def create_job(payload:JobCreate,session:SessionDep):
    job=AiRepository(session).create_job(**payload.model_dump()); return {'job_id':job.id,'status':job.status,'document_id':job.document_id,'content_ref':job.content_ref}
@app.post('/api/v1/analyze-text')
def analyze_text(payload:AnalyzeTextRequest):
    return analyze_document_text(payload.text)
@app.post('/api/v1/analyze-content')
def analyze_content(payload:AnalyzeContentRequest):
    text, extraction_method = extract_text(filename=payload.filename, content_base64=payload.content_base64)
    return {'extraction_method': extraction_method, **analyze_document_text(text)}
