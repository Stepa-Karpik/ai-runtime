from sqlalchemy.orm import Session
from app.models import AiJobModel
class AiRepository:
    def __init__(self,session:Session): self.session=session
    def create_job(self,*,document_id:str,content_ref:str)->AiJobModel:
        job=AiJobModel(document_id=document_id,content_ref=content_ref); self.session.add(job); self.session.commit(); self.session.refresh(job); return job
    def get_job(self,job_id:str)->AiJobModel|None: return self.session.get(AiJobModel,job_id)
