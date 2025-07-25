from pydantic import BaseModel, Field
from typing import List, Optional, Any
from pydantic.dataclasses import dataclass

class QuestionExtractionModel(BaseModel):
    question: str
    marks: Optional[int] = 5
    topic: Optional[str]
    question_type: str

class AnswerExtractionModel(BaseModel):
    answers: str


@dataclass
class AgentDeps:
    """Dependencies for the agent."""

    api_key: str
    http_client: Any

    class Config:
        arbitrary_types_allowed = True