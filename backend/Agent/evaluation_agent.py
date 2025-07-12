from typing import List, Dict
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from duckduckgo_search import DDGS
from Agent.models import QuestionEvaluation,GradingResult


# Class-based wrapper for grading logic
class EvaluationAgent:
    def __init__(self):
        self.agent = Agent(model="groq:qwen-qwq-32b", result_type=GradingResult)
        self._rubric: str = ""
        self._student_answers: str = ""

    def set_rubric_and_answers(self, rubric: str, student_answers: str):
        """Sets the rubric and student answers."""
        self._rubric = rubric
        self._student_answers = student_answers

    @staticmethod
    def search_duckduckgo(query: str) -> str:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if results:
                return results[0]["href"]
            return "No reference found."

    def grade(self) -> Dict:
        if not self._rubric or not self._student_answers:
            raise ValueError("Rubric and student answers must be set before grading.")

        prompt = f"""
                    You are a strict grader. Evaluate the following student answers based on the provided rubric.
                    For each question, provide:
                    - question_number
                    - student_answer
                    - marks_awarded

                    Also, calculate the total_marks.

                    Rubric:
                    {self._rubric}

                    Student Answers:
                    {self._student_answers}
                """

        result = self.agent.run_sync(prompt)
        for evaluation in result.data.evaluations:
            rubric_line = self._rubric.splitlines()[evaluation.question_number - 1]
            query = f"Correct answer to: {rubric_line}"
            evaluation.reference = self.search_duckduckgo(query)

        return {
            "total_marks": result.data.total_marks,
            "evaluations": {
                e.question_number: e.marks_awarded for e in result.data.evaluations
            },
        }



