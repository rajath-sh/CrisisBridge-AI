from ai_core.agents.base_agent import BaseAgent
from ai_core.config import ai_config

class ExplainerAgent(BaseAgent):
    """
    Generates a brief 1-2 sentence explanation of how the AI arrived at its answer.
    """

    async def execute(self, query: str, rewritten: str, sources: list[str], answer: str) -> str:
        """
        Synthesizes the pipeline trace into a human-readable explanation.
        """
        prompt = (
            f"Original Query: '{query}'\n"
            f"Rewritten Query used for search: '{rewritten}'\n"
            f"Sources retrieved: {sources}\n"
            f"Final Answer provided: '{answer[:100]}...'\n\n"
            "Write a 1-sentence explanation of how this answer was derived for the user."
        )
        
        explanation = self._generate_content(
            prompt=prompt,
            system_instruction=ai_config.EXPLAINER_PROMPT
        )
        
        return explanation.strip()

    def _get_mock_response(self) -> str:
        return "I retrieved fire safety protocols from the database and provided standard evacuation steps."
