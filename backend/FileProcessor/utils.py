"""
Utility functions for processing exam files, extracting questions and answers,
and handling RAG material indexing for the AutoCorrector backend.

Includes PDF and text file handling, OCR integration, and database operations.
"""

import os
from FileProcessor import OcrAPI, FileContentType, Engine
from pypdf import PdfReader
from io import BytesIO
from models import *
from Agents.extraction_agent import ExtractionAgent
from pymongo.database import Database
from Agents.rag_pipeline import *
from sklearn.pipeline import Pipeline
from pypdf import PdfReader
from io import BytesIO
import faiss
from typing import Annotated
from fastapi import File, UploadFile
from FileProcessor.helpers import *


async def extract_and_save_questions(
    form: SubmitQuestionForm, db: Database, user_id: ObjectId
):
    """
    Extracts questions from the uploaded exam file (PDF or TXT), processes them,
    and saves the extracted questions to the database.

    Args:
        form (ExamForm): The form containing the exam questions file.
        db (Database): The MongoDB database instance.
        user_id (ObjectId): The user's unique identifier.

    Returns:
        None
    """
    questions_filename = form.questions.filename
    questions_file = BytesIO(await form.questions.read())
    questions = ""
    if questions_filename.endswith(".txt"):
        questions = questions_file.getvalue().decode("utf-8")
        extraction_agent = ExtractionAgent()
        extracted_questions = await extraction_agent.extract_questions(questions)
    elif questions_filename.endswith(".pdf"):
        reader = PdfReader(questions_file)
        for page in reader.pages:
            if file_type(page) == FileContentType.IMG:
                ocr_engine2 = OcrAPI(
                    engine=Engine.ENGINE_2, api_key=os.getenv("OCR_API_KEY")
                )
                image_b64 = extract_image_base64(page)
                questions += ocr_engine2.ocr_base64(image_b64)
            elif file_type(page) == FileContentType.TEXT:
                questions += page.extract_text()
    extraction_agent = ExtractionAgent()
    extracted_questions = await extraction_agent.extract_questions(questions)
    await save_questions_in_db(
        user_id=user_id,
        exam_name=form.exam_name,
        questions=extracted_questions,
        db=db,
    )


def extract_text_from_pdf(pdf_bytes: BytesIO) -> str:
    """
    Extracts text from all pages of a PDF file.

    Args:
        pdf_bytes (BytesIO): The PDF file as a BytesIO object.

    Returns:
        str: The extracted text from the PDF.
    """
    reader = PdfReader(pdf_bytes)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


async def process_rag_material(
    form: SubmitRagFileForm, db: Database, user_id: ObjectId
):
    """
    Processes RAG material from the uploaded file, splits and embeds text,
    and creates a FAISS index for semantic search.

    Args:
        form (ExamForm): The form containing the RAG material file.
        index_name (str, optional): The name for the FAISS index file.

    Returns:
        None
    """
    data = BytesIO(await form.rag_material.read())
    fname = form.rag_material.filename.lower()
    if fname.endswith(".pdf"):
        content = extract_text_from_pdf(data)
    elif fname.endswith(".txt"):
        content = data.getvalue().decode("utf-8")
    else:
        raise ValueError("Unsupported file type; use .txt or .pdf")

    embedder = TransformerEmbedder()
    splitter = SentenceSplitter()
    content = [content]
    chunks = splitter.transform(content)
    embeddings = embedder.transform(chunks)
    await db["Chunks"].insert_one(
        {"exam_name": form.exam_name, "user_id": user_id, "chunks": chunks}
    )
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    embeddings = np.array(embeddings, dtype="float32")
    index.add(embeddings)
    os.makedirs("faiss_indexes", exist_ok=True)
    index_name = f"{form.exam_name}_{str(user_id)}.faiss"
    path = os.path.join("faiss_indexes", index_name)
    faiss.write_index(index, path)


async def extract_and_save_answers(
    exam_name: str,
    file: Annotated[UploadFile, File(...)],
    db: Database,
    user_id: ObjectId,
):
    """
    Extracts answers from the uploaded RAG material file (PDF or TXT), processes them,
    and saves the extracted answers to the database.

    Args:
        form (ExamForm): The form containing the RAG material file.
        db (Database): The MongoDB database instance.
        user_id (ObjectId): The user's unique identifier.

    Returns:
        None
    """
    data = BytesIO(await file.read())
    filename = file.filename.lower()
    answers = ""
    if filename.endswith(".txt"):
        answers = data.getvalue().decode("utf-8")
    elif filename.endswith(".pdf"):
        reader = PdfReader(data)
        for page in reader.pages:
            if file_type(page) == FileContentType.IMG:
                ocr_engine2 = OcrAPI(
                    engine=Engine.ENGINE_2, api_key=os.getenv("OCR_API_KEY")
                )
                image_b64 = extract_image_base64(page)
                answers += ocr_engine2.ocr_base64(image_b64)
            elif file_type(page) == FileContentType.TEXT:
                answers += page.extract_text()
    extraction_agent = ExtractionAgent()
    questions = db["Questions"].find({"_id": user_id, "exam_name": exam_name})
    query = "Question Paper:\n"
    for question in questions:
        query += question["question_id"] + " " + question["question"] + "\n"
    query += "\nAnswer Body to be extracted\n\n" + answers
    extracted_answers = await extraction_agent.extract_answers(query)
    await save_answers_in_db(
        user_id=user_id, exam_name=exam_name, answers=extracted_answers, db=db,file_name=filename
    )
