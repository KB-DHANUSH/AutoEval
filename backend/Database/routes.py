from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from Database.db_utils import get_db, insert_questions
import traceback
from Agent import ExtractionAgent
from PyPDF2 import PdfReader
from flask_cors import CORS
# Create a Blueprint for database-related routes
db_bp = Blueprint("db_bp", __name__, url_prefix="/db")
CORS(db_bp)
class ExamView(MethodView):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            exam_name = data.get("exam_name")
            user_id = ObjectId(get_jwt_identity())

            db = get_db()
            teacher = db.Users.find_one({"_id": user_id})
            if not teacher:
                return jsonify({"message": "Teacher not found"}), 404

            result = db.Exams.insert_one({
                "exam_name": exam_name,
                "teacher_id": user_id,
                "teacher_name": teacher.get("username"),
            })

            return jsonify({
                "message": "Exam created successfully",
                "exam_id": str(result.inserted_id)
            }), 201

        except Exception:
            return jsonify({
                "message": "Error: " + traceback.format_exc()
            }), 500

    @jwt_required()
    def get(self):
        try:
            user_id = ObjectId(get_jwt_identity())
            db = get_db()
            exams = db.Exams.find({"teacher_id": user_id})
            exam_list = []
            for exam in exams:
                exam_list.append({
                    "exam_id": str(exam["_id"]),
                    "exam_name": exam.get("exam_name"),
                    "teacher_name": exam.get("teacher_name")
                })
            return jsonify({"exams": exam_list}), 200
        except Exception:
            return jsonify({
                "message": "Error: " + traceback.format_exc()
            }), 500

class QuestionView(MethodView):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            exam_id = data.get("exam_id")
            rubric = data.get("rubric")
            student_answers = data.get("student_answers")

            if not all([exam_id, rubric, student_answers]):
                return jsonify({"message": "Missing required fields"}), 400

            # Initialize the ExtractionAgent
            extractor = ExtractionAgent()
            extracted_data = extractor.extract(rubric)

            # Save the extracted data to the database
            db = get_db()
            extracted_data_entry = {
                "exam_id": ObjectId(exam_id),
                "extracted_data": extracted_data
            }
            db.ExtractedData.insert_one(extracted_data_entry)

            return jsonify({
                "message": "Data extracted successfully",
                "extracted_data": extracted_data
            }), 200

        except Exception as e:
            return jsonify({
                "message": f"Error: {str(e)}"
            }), 500

    @jwt_required()
    def get(self):
        try:
            exam_id = request.args.get("exam_id")
            if not exam_id:
                return jsonify({"message": "Missing exam_id parameter"}), 400

            # Retrieve the exam document from the database
            db = get_db()
            exam = db.Exams.find_one({"_id": ObjectId(exam_id)})
            if not exam:
                return jsonify({"message": "Exam not found"}), 404

            # Extract text from the exam's PDF
            pdf_path = exam.get("pdf_path")
            if not pdf_path:
                return jsonify({"message": "PDF path not found in exam document"}), 404

            with open(pdf_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

            # Process the extracted text to identify questions
            questions = self.extract_questions_from_text(text)

            # Insert the questions into the database
            question_entries = [
                {"exam_id": ObjectId(exam_id), "question": question['text'], 'marks': question['marks']}
                for question in questions
            ]
            db.Questions.insert_many(question_entries)

            return jsonify({
                "message": "Questions extracted and saved successfully",
                "questions": questions
            }), 200

        except Exception as e:
            return jsonify({
                "message": f"Error: {str(e)}"
            }), 500

    def extract_questions_from_text(self, text):
        # Implement your logic to extract questions from the text
        lines = text.split("\n")
        questions = []
        current_question = None
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.')):  # Adjust this condition based on your question numbering
                if current_question:
                    questions.append(current_question)
                current_question = {'text': line, 'marks': 0}  # Default marks
            elif line.startswith(('a)', 'b)', 'c)')):  # Adjust this condition based on your answer options
                if current_question:
                    current_question['text'] += ' ' + line
            elif line.lower().startswith('marks:'):
                if current_question:
                    try:
                        current_question['marks'] = int(line.split(':')[1].strip())
                    except ValueError:
                        pass
        if current_question:
            questions.append(current_question)
        return questions


db_bp.add_url_rule("/exam", view_func=ExamView.as_view("exam"))
db_bp.add_url_rule("/questions", view_func=QuestionView.as_view("question"))
