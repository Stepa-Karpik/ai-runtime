from collections.abc import Generator
import os
from sqlalchemy import create_engine
from app.models import Base
from sqlalchemy.orm import Session,sessionmaker
DATABASE_URL=os.getenv('AI_RUNTIME_DATABASE_URL','sqlite+pysqlite:///./ai-runtime.db')
engine=create_engine(DATABASE_URL); SessionLocal=sessionmaker(engine)
if DATABASE_URL.startswith('sqlite'):
    Base.metadata.create_all(engine)
def get_session()->Generator[Session,None,None]:
    with SessionLocal() as session: yield session
