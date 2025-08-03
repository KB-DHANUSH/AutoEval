import asyncio
from bson import ObjectId
from pymongo import MongoClient
from grading_agent import GradingAgent
from dotenv import load_dotenv
import os

async def main():
    exam_id = "688f8bad4947fe3beb60bcb1"
    user_id = ObjectId("68767f6b8e62c0b8cc32805b")  # Replace with valid ObjectId if needed
    load_dotenv()
    user = os.getenv("MONGO_DB_USERNAME")
    pwd = os.getenv("MONGO_DB_PASSWORD")
    if not user or not pwd:
        raise RuntimeError("Missing MongoDB credentials")
    uri = f"mongodb+srv://{user}:{pwd}@cluster0.bfi26pi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri)
    db = client["InkGrader"]
    agent = GradingAgent(exam_id=exam_id, user_id=user_id, db=db)

    query = "Question\nExplain the different types of distributed system models used in cloud computing (5 marks).Answer\n"
    query += '''
Distributed systems can be categorized into several models based on their architecture and communication methods. The main types include:
1. **Client-Server Model**: In this model, clients request services from servers,
    '''
    result = await agent.grade(query)

    print("Grading Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
