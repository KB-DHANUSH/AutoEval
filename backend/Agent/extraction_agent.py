from dotenv import load_dotenv
from pydantic_ai import Agent
from Agent.models import Rubric , Question

class ExtractionAgent:
    def __init__(self, model: str = "groq:qwen-qwq-32b"):
        """
        Initialize the agent with the specified Groq model.
        """
        self.agent = Agent(
            model=model,
            result_type=Rubric,
            system_prompt=(
                "You are an AI assistant that extracts questions and their corresponding marks "
                "from a given text. Return the data as a list of questions with their marks."
            )
        )

    def extract(self, input_text: str) -> dict:
        """
        Extract questions and marks from the input text.
        """
        result = self.agent.run_sync(input_text)
        return result.data.model_dump()
    

