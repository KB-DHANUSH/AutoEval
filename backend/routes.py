from fastapi import APIRouter,Request,Response
from models import ExamForm
from Auth.utils import get_current_user
from FileProcessor.utils import extract_and_save_questions,process_rag_material,extract_and_save_answers

router = APIRouter(prefix='/api')

@router.get('/')
async def root():
    return{
        "message":"Welcome to AutoCorrector!"
    }

@router.post('/exam_submit')
async def exam_submit(request:Request,response: Response,exam_form:ExamForm):
    user = await get_current_user(request)
    extract_and_save_questions(exam_form,request.app.database,user._id)
    process_rag_material(exam_form,request.app.database)
    extract_and_save_answers(exam_form,request.app.database,user._id)
    response.status_code = 201
    results = [user._id]
    return {
        "message": "Exam submitted successfully!",
        "results": results
    }