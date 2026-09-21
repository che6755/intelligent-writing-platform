# backend/app/models/document.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from backend.app.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    education_level = Column(String, nullable=False, default="high_school")
    language = Column(String, nullable=False, default="zh")
    title = Column(String, default="")
    user_text = Column(Text, default="")
    outline = Column(JSON) # 使用 JSON 类型存储大纲和素材
    score_report = Column(JSON, nullable=True) # 存储评分报告
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
