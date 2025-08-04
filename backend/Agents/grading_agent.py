import os
import logging
from pydantic_ai import Agent,Tool
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from Agents.models import GradingAgentDeps,GradingAgentOutput
from httpx import AsyncClient
from bson import ObjectId
from typing import List
from pymongo.database import Database
from Agents.tools import rag_tool
from Agents.prompts import GRADING_AGENT_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradingAgent:
    def __init__(self, exam_id: str, user_id: ObjectId, db: Database):
        logger.info(f"Initializing GradingAgent for exam_id={exam_id}, user_id={user_id}")
        self._agent_settings = {"temperature": 0.2}
        self._API_KEY = os.getenv("GROQ_API_KEY")
        self.deps = GradingAgentDeps(
            api_key=self._API_KEY,
            http_client=AsyncClient,
            exam_id=exam_id,
            user_id=str(user_id),
            db=db
        )
        self.agent = Agent(
            model='groq:moonshotai/kimi-k2-instruct',
            system_prompt=GRADING_AGENT_PROMPT,
            model_settings=self._agent_settings,
            deps_type=GradingAgentDeps,
            output_type=GradingAgentOutput,
            tools=[
                duckduckgo_search_tool(),
                Tool(rag_tool, takes_ctx=True)
            ]
        )
        logger.info("GradingAgent initialized successfully.")

    async def grade(self, query: str) -> GradingAgentOutput:
        logger.info(f"Grading started for query: {query[:100]}...")
        try:
            response = await self.agent.run(query, deps=self.deps, infer_name=False)
            logger.info("Grading completed successfully.")
            return response.output
        except Exception as e:
            logger.error(f"Error during grading: {e}")
