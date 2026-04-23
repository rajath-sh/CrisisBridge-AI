from ai_core.agents.base_agent import BaseAgent
from ai_core.config import ai_config

class ReasoningAgent(BaseAgent):
    """
    Takes the rewritten query and retrieved context to generate a comprehensive,
    step-by-step emergency response.
    """

    async def execute(self, query: str, context: str) -> str:
        """
        Generates the final answer based ONLY on the context.
        """
        prompt = (
            f"User Question: {query}\n\n"
            f"Available Safety Context:\n{context}\n\n"
            "Based strictly on the provided context, answer the user's question. "
            "If the answer is not in the context, state that clearly."
        )
        
        answer = self._generate_content(
            prompt=prompt,
            system_instruction=ai_config.REASONING_PROMPT
        )
        
        return answer.strip()

    def _get_mock_response(self) -> str:
        return "1. Stay calm.\n2. Proceed to the nearest exit using stairs.\n3. Do not use elevators."
