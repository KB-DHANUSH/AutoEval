from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from bson import ObjectId
from pydantic.dataclasses import dataclass

class QuestionExtractionModel(BaseModel):
    question_id: int = Field(...,description="id that reprsents the question order")
    question: str
    marks: int = Field(default=5)
    topic: Optional[str]
    question_type: str
    
    @field_validator("marks",mode="after")
    @classmethod
    def default_marks(cls, value, info):
        return value if value is not None else cls.model_fields["marks"].get_default()

class AnswerExtractionModel(BaseModel):
    question_id: int = Field(...,description="id that represents the question order")
    answers: str


@dataclass
class ExtractionAgentDeps:
    """Dependencies for the grading agent."""

    api_key: str
    http_client: Any

    class Config:
        arbitrary_types_allowed = True

@dataclass
class GradingAgentDeps:
    """Dependencies for the grading agent."""
    api_key: str
    http_client: Any
    user_id: Any
    exam_name: str
    db: Any

    class Config:
        arbitrary_types_allowed = True

class GradingAgentOutput(BaseModel):
    question: str
    answer: str
    marks: int
