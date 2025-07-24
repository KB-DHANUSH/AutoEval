"""
Utility functions for processing exam files, extracting questions and answers,
and handling RAG material indexing for the AutoCorrector backend.

Includes PDF and text file handling, OCR integration, and database operations.
"""

import os
from FileProcessor import OcrAPI, FileContentType, Engine
from pypdf import PdfReader
from io import BytesIO
from models import ExamForm
from Agents.extraction_agent import ExtractionAgent
from pymongo.database import Database
from Agents.rag_pipeline import *
from sklearn.pipeline import Pipeline
from pypdf import PdfReader
from io import BytesIO
import faiss
from helpers import *


async def extract_and_save_questions(form: ExamForm, db: Database, user_id: ObjectId):
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
    questions_filename = form.exam_questions.filename
    questions_file = BytesIO(form.exam_questions.read())
    if questions_filename.endswith(".txt"):
        questions = questions_file.getvalue().decode("utf-8")
        extraction_agent = ExtractionAgent()
        extracted_questions = extraction_agent.extract_questions(questions)
        await save_questions_in_db(
            user_id=user_id, questions=extracted_questions, db=db
        )
    elif questions_filename.endswith(".pdf"):
        reader = PdfReader(questions_file)
        questions = ""
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
        extracted_questions = extraction_agent.extract_questions(questions)
        await save_questions_in_db(
            user_id=user_id, questions=extracted_questions, db=db
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


def process_rag_material(form: ExamForm, index_name: str = "rag-materials"):
    """
    Processes RAG material from the uploaded file, splits and embeds text,
    and creates a FAISS index for semantic search.

    Args:
        form (ExamForm): The form containing the RAG material file.
        index_name (str, optional): The name for the FAISS index file.

    Returns:
        None
    """
    data = BytesIO(form.rag_material.read())
    fname = form.rag_material.filename.lower()
    if fname.endswith(".pdf"):
        content = extract_text_from_pdf(data)
    elif fname.endswith(".txt"):
        content = data.getvalue().decode("utf-8")
    else:
        raise ValueError("Unsupported file type; use .txt or .pdf")

    pipeline = Pipeline(
        [
            ("splitter", SentenceSplitter(chunk_size=256, chunk_overlap=20)),
            (
                "embedder",
                TransformerEmbedder(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    device="cpu",
                    batch_size=16,
                ),
            ),
        ]
    )
    chunks = [content]
    embeddings = pipeline.fit_transform(chunks)  # shape (num_chunks, dim)
    chunk_texts = pipeline.named_steps["splitter"].transform(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    embeddings = np.array(embeddings, dtype="float32")
    index.add(embeddings)
    total = index.ntotal

    os.makedirs("faiss_indexes", exist_ok=True)
    path = os.path.join("faiss_indexes", index_name)
    faiss.write_index(index, path)


async def extract_and_save_answers(form: ExamForm, db: Database, user_id: ObjectId):
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
    data = BytesIO(form.rag_material.read())
    filename = form.rag_material.filename.lower()
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
    extracted_questions = extraction_agent.extract_answers(answers)
    await save_answers_in_db(user_id=user_id, answers=extracted_questions, db=db)
