from fastapi import File, UploadFile,Form
from typing import List

class ExamForm:
    def __init__(
        self,
        exam_name: str = Form(...),
        exam_questions: UploadFile = File(...),
        rag_material: UploadFile = File(...),
        student_answers: List[UploadFile] = File(...)
    ):
        self.exam_name = exam_name
        self.exam_questions = exam_questions
        self.rag_material = rag_material
        self.student_answers = student_answers
    