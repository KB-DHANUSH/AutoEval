import os
from pydantic_ai import Agent,Tool
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from Agents.models import GradingAgentDeps,GradingAgentOutput
from httpx import AsyncClient
from bson import ObjectId
from typing import List
from pymongo.database import Database
from Agents.tools import rag_tool
from Agents.prompts import GRADING_AGENT_PROMPT



class GradingAgent(Agent):
    def __init__(self, exam_name: str, user_id: ObjectId,db: Database):
        self._agent_settings = {"temperature": 0.2}
        self._API_KEY = os.getenv("GROQ_API_KEY")
        self._deps = GradingAgentDeps(
            api_key=self._API_KEY,
            http_client=AsyncClient,
            exam_name=exam_name,
            user_id=str(user_id),
            db=db
        )
        self._agent = Agent(
            model='groq:moonshotai/kimi-k2-instruct',
            system_prompt=GRADING_AGENT_PROMPT,
            model_settings=self._agent_settings,
            deps_type=self._deps,
            output_type=List[GradingAgentOutput],
            tools=[
                duckduckgo_search_tool(),
                Tool(rag_tool,takes_ctx=True)
            ]
        )
    
    async def grade(self,query: str):
        response = await self._agent.run(query)
        return response.output
