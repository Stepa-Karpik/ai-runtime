from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base
from app.repositories import AiRepository

def test_job_persists():
    engine=create_engine('sqlite+pysqlite:///:memory:'); Base.metadata.create_all(engine); repo=AiRepository(Session(engine))
    job=repo.create_job(document_id='doc_1',content_ref='asset_1')
    assert repo.get_job(job.id).document_id=='doc_1'
