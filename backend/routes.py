from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from redis_pubsub import PubSubManager
import asyncio
from pymongo.database import Database
from models import *
from Auth.utils import get_current_user
from FileProcessor.utils import (
    extract_and_save_questions,
    process_rag_material,
    extract_and_save_answers,
)
from Auth.utils import ALGORITHM, JWT_SECRET_KEY
from jwt import decode as jwt_decode, PyJWTError
from Agents.grading_agent import GradingAgent
from config import ConnectionManager, running_tasks, task_lock
from bson import ObjectId

exam_router = APIRouter()
conn_manager = ConnectionManager()


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
    find_result = await request.app.database["Questions"].find_one(
        {"exam_name": form.exam_name, "user_id": user["_id"]}
    )
    response.status_code = 201
    return {
        "message": "Done Submitting rag material",
        "exam_id": str(find_result["_id"]),
    }


async def grading_task(db: Database, exam_id: str, user_id: ObjectId):
    questions_list = await db["Questions"].find_one(
        {"user_id": user_id, "_id": ObjectId(exam_id)}
    )
    answer_paper_list =  db["Answers"].find(
        {"user_id": user_id, "exam_id": ObjectId(exam_id)}
    )
    answer_paper_list = await answer_paper_list.to_list(length=None)
    qa = ""
    pubsub = PubSubManager()
    print("Starting grading task")
    for answer_paper in answer_paper_list:
        paper_string = ""
        for question_info in questions_list["questions"]:
            qa += f"{question_info['question_id']}. {question_info['question']}\n"
            qa += f"Question Topic: {question_info['topic']}\n"
            qa += f"Question Type: {question_info['question_type']}\n"
            qa += f"Answer: {answer_paper['answers'][0]['answers']}\n\n"
        print(f"Grading paper for {answer_paper['file_name']}")
        paper_string += qa
        agent = GradingAgent(exam_id=exam_id, user_id=str(user_id), db=db)
        results = await agent.grade(paper_string)
        print(f"Grading completed for {answer_paper['file_name']}")
        for result in results:
            await db["Answers"].update_one(
                {
                    "user_id": user_id,
                    "exam_id": ObjectId(exam_id),
                    "file_name": result["file_name"],
                    "answers.question_id": result["question_id"],
                },
                {"$set": {"answers.marks": result["marks"]}},
            )
        print(f"Marks updated for {answer_paper['file_name']}")
        await pubsub.publish(
            channel=f"{user_id}:{exam_id}",
            message=f"marks updated for filename {result['file_name']}",
        )
        print(f"Published message to channel {user_id}:{exam_id}")


@exam_router.websocket_route("/{exam_id}")
async def exam_socket(websocket: WebSocket):
    await websocket.accept()
    exam_id = websocket.path_params.get("exam_id")
    if not exam_id:
        await websocket.close(code=1008, reason="Invalid exam ID")
        return
    pubsub = PubSubManager()
    await pubsub.connect()
    token = websocket.headers.get("Authorization", "").split(" ")[-1]
    try:
        subject = jwt_decode(token, key=JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = subject.get("sub")
        if not user_id:
            raise ValueError("Missing sub")
    except (PyJWTError, ValueError):
        await websocket.close(code=1008, reason="Invalid token")
        return
    task_key = f"{user_id}:{exam_id}"
    redis_channel = f"{user_id}:{exam_id}"
    redis_pubsub = await pubsub.subscribe(redis_channel)
    await conn_manager.connect(websocket, user_id)
    async with task_lock:
        if task_key not in running_tasks:
            task = asyncio.create_task(
                grading_task(
                    db=websocket.app.database,
                    exam_id=exam_id,
                    user_id=ObjectId(user_id),
                )
            )
            running_tasks[task_key] = task

    try:
        while True:
            data = await websocket.receive_text()
            async for message in redis_pubsub.listen():
                if message["type"] == "message":

                    answers_info_list = await websocket.app.database["Answers"].find(
                        {
                            "user_id": ObjectId(user_id),
                            "exam_id": ObjectId(exam_id),
                        }
                    )
                    data = []
                    for answer_info in answers_info_list:
                        total_marks = sum(
                            answer["marks"]
                            for answer in answer_info.get("answers", [])
                            if "marks" in answer
                        )
                        data.append(
                            {
                                "file_name": answer_info["file_name"],
                                "total_marks": total_marks,
                            }
                        )
                    await conn_manager.send_personal_message({"message": data}, user_id)
    except WebSocketDisconnect:
        await conn_manager.disconnect(websocket, user_id)
        task = running_tasks.pop(task_key, None)
        if task:
            task.cancel()
