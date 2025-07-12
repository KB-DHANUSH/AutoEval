from OCRSpace import API, Engine
import os
from typing import List
from Database.db_utils import get_db
from flask import Blueprint, request
import re
import traceback
import base64
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from Agent import EvaluationAgent
from flask_cors import CORS

ocr_bp = Blueprint("ocr_bp", __name__, url_prefix="/ocr")
CORS(ocr_bp)
OCR_API_KEY = os.getenv("OCR_API_KEY")
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # Define the upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists


def ocr_image(image) -> str:
    api = API(api_key=OCR_API_KEY, engine=Engine.ENGINE_2)
    return api.ocr_base64(image)


def ocr_image_from_file(file_path) -> str:
    """Process the image file using the OCR API."""
    api = API(api_key=OCR_API_KEY, engine=Engine.ENGINE_2)
    return api.ocr_file(file_path)


def clean_text(text):
    """Clean and normalize the input text."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.lower().strip()


@ocr_bp.route("/demo", methods=["POST"])
def test_ocr_agent():
    try:
        image = request.files.get("image")
        question = request.form.get("question")
        marks = request.form.get("marks")
        db = get_db()

        if image and question and marks:
            filename = secure_filename(image.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(file_path)

            # OCR + preprocessing
            text = ocr_image_from_file(file_path)
            processed_text = clean_text(text) + " marks: " + str(marks)
            os.remove(file_path)

            # Grade the answer
            grader = EvaluationAgent()
            grader.set_rubric_and_answers(question, processed_text)
            grading_result = grader.grade()

            # Convert eval keys to strings for MongoDB
            safe_grading_result = {
                "total_marks": grading_result["total_marks"],
                "evaluations": {
                    str(k): v for k, v in grading_result["evaluations"].items()
                },
            }

            # Store in DB
            db.test.insert_one(
                {
                    "question": question,
                    "student_answer": processed_text,
                    "grading_result": safe_grading_result,
                }
            )
            print(safe_grading_result)
            return {
                "message": "Graded and saved successfully",
                "grading_result": safe_grading_result,
                "extracted_text": processed_text,
            }, 200

        else:
            return {"message": "Wrong fields sent in request"}, 400

    except Exception:
        return {"message": "Error: " + traceback.format_exc()}, 500


@ocr_bp.route("/bulk", methods=["POST"])
def post_image_bulk(image_paths: List[str]) -> dict:
    pass
