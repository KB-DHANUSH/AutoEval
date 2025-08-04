"""
This is the main entry point for the FastAPI application.

It sets up the database connection, middleware, and API routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import asyncio
from config import running_tasks, task_lock
from config import origins
from Auth.routes import auth_router
from routes import exam_router
from pymongo import AsyncMongoClient
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    user = os.getenv("MONGO_DB_USERNAME")
    pwd = os.getenv("MONGO_DB_PASSWORD")
    if not user or not pwd:
        raise RuntimeError("Missing MongoDB credentials")
    uri = f"mongodb+srv://{user}:{pwd}@cluster0.bfi26pi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    app.mongodb_client = AsyncMongoClient(uri)
    try:
        ping = await app.mongodb_client.admin.command("ping")
        if ping.get("ok") != 1:
            raise Exception("Ping failed")
        print("✅ Connected to MongoDB")
    except Exception:
        print("❌ Failed to connect to MongoDB")
        await app.mongodb_client.close()
        raise
    app.database = app.mongodb_client["InkGrader"]
    yield
    await app.mongodb_client.close()
    for task in running_tasks.values():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(exam_router, prefix="/api/exam")
app.include_router(auth_router, prefix="/api/auth")

@app.post("/api")
async def root():
    return {"message": "Welcome to the InkGrader API"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)