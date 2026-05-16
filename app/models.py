from datetime import UTC, datetime
from uuid import uuid4
from sqlalchemy import DateTime,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
class Base(DeclarativeBase): pass
class AiJobModel(Base):
    __tablename__='ai_jobs'
    id:Mapped[str]=mapped_column(String(64),primary_key=True,default=lambda:f'job_{uuid4().hex}')
    document_id:Mapped[str]=mapped_column(String(64),index=True)
    content_ref:Mapped[str]=mapped_column(String(128))
    status:Mapped[str]=mapped_column(String(32),default='queued')
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC))
