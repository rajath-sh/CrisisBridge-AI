from ai_core.agents.base_agent import BaseAgent
from ai_core.config import ai_config

class QueryRewriterAgent(BaseAgent):
    """
    Takes a raw user query and rewrites it into a clear, specific question
    optimized for vector search against the safety documents.
    """

    async def execute(self, raw_query: str, session_history: list = None) -> str:
        """
        Rewrites the query, using conversation history to understand follow-up questions.
        """
        history_text = ""
        if session_history:
            history_text = "Previous conversation history:\n"
            for item in session_history[-3:]: # Just look at the last 3 interactions to save tokens
                history_text += f"User: {item.get('query', '')}\nAI: {item.get('answer', '')}\n"
                
        prompt = f"{history_text}\nRaw user query: '{raw_query}'\n\nRewrite this into a clear, standalone question for a safety manual. If it is a follow-up, use the history to understand the context."
        
        rewritten_query = self._generate_content(
            prompt=prompt,
            system_instruction=ai_config.QUERY_REWRITER_PROMPT
        )
        
        return rewritten_query.strip()

    def _get_mock_response(self) -> str:
        return "What is the emergency procedure for a fire in a hotel room?"
