from pydantic_ai import Agent
from Agents.models import QuestionExtractionModel,AnswerExtractionModel,ExtractionAgentDeps
import os
from httpx import AsyncClient
from typing import List
from Agents.prompts import QUESTION_EXTRACTION_PROMPT,ANSWER_EXTRACTION_PROMPT

class ExtractionAgent:
    def __init__(self):
        self._agent: Agent[None,List[QuestionExtractionModel]|List[AnswerExtractionModel]]
        self._agent_settings = {
            "temperature": 0.2
        }
        self._API_KEY = os.getenv("GROQ_API_KEY")
        self._deps = ExtractionAgentDeps(api_key=self._API_KEY, http_client=AsyncClient)
    
    async def extract_questions(self,questions: str)->List[QuestionExtractionModel]:
        self._agent = Agent(
            model='groq:mistral-saba-24b',
            system_prompt=QUESTION_EXTRACTION_PROMPT,
            output_type=List[QuestionExtractionModel],
            deps_type=self._deps,
            model_settings=self._agent_settings,
        )
        result = await self._agent.run(questions,infer_name=False)
        return result.output
    
    async def extract_answers(self,answers: str)->List[AnswerExtractionModel]:
        self._agent = Agent(
            model='groq:mistral-saba-24b',
            system_prompt=ANSWER_EXTRACTION_PROMPT,
            output_type=List[AnswerExtractionModel],
            deps_type=self._deps,
            model_settings=self._agent_settings,
        )
        result = await self._agent.run(answers,infer_name=False)
        return result.output