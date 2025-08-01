from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from pymongo.database import Database
from models import *
from Auth.utils import get_current_user
from FileProcessor.utils import (
    extract_and_save_questions,
    process_rag_material,
    extract_and_save_answers,
)
from Auth.utils import ALGORITHM, JWT_SECRET_KEY
import jwt
from Agents.grading_agent import GradingAgent
from config import ConnectionManager
from bson import ObjectId

exam_router = APIRouter()


@exam_router.post("/form/submit/questions")
async def submit_questions(
    request: Request,
    response: Response,
    question_form: SubmitQuestionForm = Depends(),
    user=Depends(get_current_user),
):
    await extract_and_save_questions(
        db=request.app.database, form=question_form, user_id=user["_id"]
    )
    response.status_code = 201
    return {"message": "Done submitting questions"}


@exam_router.post("/form/submit/answers")
async def submit_answers(
    request: Request,
    response: Response,
    answer_form: SubmitAnswersForm = Depends(),
    user=Depends(get_current_user),
):
    for file in answer_form.student_answers:
        await extract_and_save_answers(
            db=request.app.database,
            exam_name=answer_form.exam_name,
            user_id=user["_id"],
            file=file,
        )
    response.status_code = 201
    return {"message": "Done submitting answers"}


@exam_router.post("/form/submit/rag_file")
async def submit_rag_file(
    request: Request,
    response: Response,
    form: SubmitRagFileForm = Depends(),
    user=Depends(get_current_user),
):
    await process_rag_material(db=request.app.database, form=form, user_id=user["_id"])
    response.status_code = 201
    return {"message": "Done Submitting rag material"}

async def grading_task(db: Database,exam_name:str, user_id: ObjectId): 
    questions_list = await db["Questions"].find({
        "user_id": user_id,
        "exam_name": exam_name
    })
    answer_paper_list = await db["Answers"].find({
        "user_id": user_id,
        "exam_name": exam_name
    })
    qa=''
    for answer_paper in answer_paper_list:
        paper_string = ''
        for question_info in questions_list["questions"]:
            if question_info['exam_name'] == exam_name:
                qa += f"{question_info['question_id']}. {question_info['question']}\n"
                qa += f"Question Topic: {question_info['topic']}\n"
                qa += f"Question Type: {question_info['question_type']}\n"
                qa += f"Answer: {answer_paper['answers'][0]['answer']}\n\n"
        paper_string += qa
        agent = GradingAgent(exam_name=exam_name, user_id=user_id, db=db)
        results = await agent.grade(paper_string)
        for result in results:
            await db["Answers"].update_one(
                {"user_id" :user_id, "exam_name": exam_name, "file_name": result["file_name"], "answers.question_id": result["question_id"]},
                {"$set": {"answers.marks": result["marks"]}}
            )


@exam_router.websocket_route("/{exam_name}")
async def exam_socket(websocket: WebSocket, exam_name: str):
    token = websocket.query_params.get("token")
    manager = ConnectionManager()
    db = websocket.app.database
    if not token:
        await WebSocket.close(code=1008)
        return
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = str(payload.get("sub"))
    except jwt.PyJWTError:
        await websocket.close(code=1080)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            agent = GradingAgent(exam_name=exam_name, user_id=ObjectId(user_id), db=db)
            results = await agent.grade()
            await manager.send_personal_message(
                {"reply": "You said", "data": results}, user_id
            )
    except WebSocketDisconnect:
        
        manager.disconnect(user_id)
