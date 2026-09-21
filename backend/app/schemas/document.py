# backend/app/schemas/document.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime


class ScoreReport(BaseModel):
    overall_score: float = Field(..., ge=0, le=10)
    dimensions: Dict[str, Any]
    suggestions: List[str]

class DocumentCreate(BaseModel):
    topic: str
    education_level: Literal["high_school", "university"] = "high_school"
    language: Literal["zh", "en"] = "zh"
    title: str = ""

class DocumentUpdate(BaseModel):
    user_text: str
    title: Optional[str] = None

class Document(BaseModel):
    id: int
    topic: str
    education_level: str
    language: str
    title: str = ""
    user_text: Optional[str] = None
    outline: Optional[Dict[str, Any]] = None
    score_report: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("outline", "score_report", mode="before")
    @classmethod
    def normalize_json_fields(cls, value):
        if isinstance(value, dict):
            return value
        if value is None or value == "":
            return None
        return None

    class Config:
        from_attributes = True # 新版 Pydantic v2 写法
