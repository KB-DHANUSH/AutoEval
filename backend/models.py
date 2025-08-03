from fastapi import File, UploadFile,Form
from typing import List,Annotated

class SubmitQuestionForm:
    def __init__(
        self,
        exam_name: Annotated[str,Form(...)],
        exam_questions: Annotated[UploadFile,File(...)]
    ):
        self.exam_name = exam_name
        self.questions = exam_questions

class SubmitAnswersForm:
    def __init__(
        self,
        exam_name: Annotated[str,Form(...)],
        student_answers: Annotated[List[UploadFile],File(...)]
    ):
        self.exam_name = exam_name
        self.student_answers = student_answers

class SubmitRagFileForm:
    def __init__(
        self,
        exam_name: Annotated[str,Form(...)],
        rag_material: UploadFile = File(...)
    ):
        self.exam_name = exam_name
        self.rag_material = rag_material
    