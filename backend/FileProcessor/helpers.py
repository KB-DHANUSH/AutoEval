from FileProcessor import FileContentType
from pypdf import PdfReader
from pypdf._page import PageObject
from io import BytesIO
from bson import ObjectId
import base64
from Agents.models import QuestionExtractionModel,AnswerExtractionModel
from pymongo.database import Database
from pymongo import UpdateOne
from typing import List
from Agents.rag_pipeline import *
from pypdf import PdfReader
from io import BytesIO


def extract_text_from_pdf(pdf_bytes: BytesIO) -> str:
    reader = PdfReader(pdf_bytes)
    text = []
    for page in reader.pages:
        page_text = page.extract_text(extraction_mode="layout")
        if page_text:
            text.append(page_text)
    return "\n".join(text)

async def save_questions_in_db(
    user_id: ObjectId,exam_name: str, questions: List[QuestionExtractionModel], db: Database
):
    query = []

    for question in questions:
        query.append({
            "user_id": user_id,
            "question_id": question.question_id,
            "exam_name": exam_name,
            "question": question.question,
            "marks": question.marks,
            "topic": question.topic,
            "question_type": question.question_type,
        })
    await db["Questions"].insert_many(query)
    
async def save_answers_in_db(
    user_id: ObjectId, exam_name:str, answers: List[AnswerExtractionModel], db: Database,file_name: str
):
    query = []

    for answer in answers:
        query.append({
            "user_id": user_id,
            "question_id": answer.question_id,
            "exam_name": exam_name,
            "answer": answer.answers,
            "answer_id": file_name
        })
    await db["Answers"].insert_many(query)
    
def file_type(page: PageObject) -> FileContentType:
    text = page.extract_text()
    has_text = bool(text and text.strip())

    resources = page.get("/Resources")
    has_images = False
    if resources and "/XObject" in resources:
        xobject = resources["/XObject"]
        if isinstance(xobject, dict):
            for obj in xobject.values():
                if obj.get("/Subtype") == "/Image":
                    has_images = True
                    break

    if has_images and has_text:
        return FileContentType.IMG_OR_TEXT
    elif has_text:
        return FileContentType.TEXT
    elif has_images:
        return FileContentType.IMG
    else:
        return FileContentType.UNKNOWN

def extract_image_base64(page):

    xobjects = page["/Resources"]["/XObject"]

    for name in xobjects:
        xobj = xobjects[name].get_object()
        if xobj["/Subtype"] == "/Image":
            image_data = xobj.get_data()
            base64_str = base64.b64encode(image_data).decode("utf-8")
            return base64_str

    raise ValueError("No image found on the page.")