from pydantic import BaseModel, Field
from typing import List

class QuestionEvaluation(BaseModel):
    question_number: int = Field(..., description="The question number.")
    student_answer: str = Field(..., description="The student's answer.")
    marks_awarded: int = Field(..., description="Marks awarded for the answer.")
    reference: str = Field(..., description="Reference URL for the correct answer.")


class GradingResult(BaseModel):
    evaluations: List[QuestionEvaluation] = Field(..., description="List of evaluated questions.")
    total_marks: int = Field(..., description="Total marks awarded.")
    
class Question(BaseModel):
    text: str = Field(..., description="The question text.")
    marks: int = Field(..., description="Marks allocated for the question.")

class Rubric(BaseModel):
    questions: List[Question] = Field(..., description="List of questions with their marks.")