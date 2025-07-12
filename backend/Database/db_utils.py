from flask import current_app, g
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.errors import InvalidId
from bson import ObjectId
from passlib.context import CryptContext
from pymongo import MongoClient, ASCENDING
import os
import traceback
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def get_db():
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    MONGO_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster0.bfi26pi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DB_CLIENT = MongoClient(MONGO_URI)
    return DB_CLIENT.InkGrader


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def authenticate_user(email: str, password: str) -> dict:
    db = get_db()
    result = db.Users.find_one({"email": email})
    if result is None:
        return {"message": "User not found."}
    if not verify_password(password, result.get("password")):
        return {"message": "Incorrect password."}
    else:
        return {"message": "User authenticated successfully.", "id": str(result["_id"])}


def create_teacher_user(
    username: str, password: str, email: str, teacher_id: str
) -> dict:
    try:
        db = get_db()
        db.Users.create_index([("email", ASCENDING)], unique=True)
        result = db.Users.insert_one(
            {
                "teacher_id": teacher_id,
                "username": username,
                "email": email,
                "password": password_context.hash(password),
            }
        )
        return {
            "message": "User created successfully.",
            "id": str(result.inserted_id),
        }
    except DuplicateKeyError:
        return {"message": "DuplicateKeyError: The email already exists."}
    except OperationFailure:
        return {
            "message": "OperationFailure: An error occurred while creating the user. Operation failed."
        }


def create_student_user(
    username: str, password: str, email: str, student_id: str
) -> dict:
    try:
        db = get_db()
        db.Users.create_index([("email", ASCENDING)], unique=True)
        user = db.Users.insert_one(
            {
                "student_id": student_id,
                "username": username,
                "email": email,
                "password": password_context.hash(password),
            }
        )
        return {"message": "User created successfully.", "id": str(user["_id"])}
    except DuplicateKeyError:
        return {"message": "DuplicateKeyError: The username already exists."}
    except OperationFailure:
        return {
            "message": "OperationFailure: An error occurred while creating the user. Operation failed."
        }


def get_user_by_email(email: str) -> dict:
    try:
        db = get_db()
        user = db.Users.find_one({"email": email})
        return user
    except InvalidId:
        return {"message": "Invalid email."}
    except OperationFailure:
        return {
            "message": "An error occurred while retrieving the user. Operation failed."
        }
        
def insert_questions(questions):
    try:
        db = get_db()
        response = db.Questions.insert_many(questions)
        return {
            "message":"Succesfully entered all questions"
        }
    except Exception as e:
        return {
            "message":"Failed: "+traceback.format_exc()
        }
