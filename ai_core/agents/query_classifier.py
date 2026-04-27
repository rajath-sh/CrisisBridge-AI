from ai_core.agents.base_agent import BaseAgent
import json

class QueryClassifierAgent(BaseAgent):
    """
    Analyzes the raw user query and classifies it.
    Returns JSON: {"category": "EMERGENCY|GENERAL|CASUAL", "rewritten_query": "..."}
    """

    async def execute(self, raw_query: str) -> dict:
        prompt = f"""
Analyze the following user query: "{raw_query}"

Classify it into one of three categories:
1. EMERGENCY: Life-threatening situations, immediate danger (fire, medical, security).
2. GENERAL: Routine questions about safety procedures or hotel protocols.
3. CASUAL: Greetings, small talk, or unrelated questions.

Also, rewrite the query to be optimized for a vector search engine (unless it's CASUAL).

Return ONLY valid JSON in this format:
{{
  "category": "EMERGENCY",
  "rewritten_query": "What is the fire evacuation procedure?"
}}
"""
        response_text = self._generate_content(
            prompt=prompt,
            system_instruction="You are a JSON-only query classification agent."
        )
        
        try:
            # Strip markdown formatting if the LLM adds it
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception:
            # Fallback
            return {"category": "GENERAL", "rewritten_query": raw_query}

    def _get_mock_response(self) -> str:
        return '{"category": "EMERGENCY", "rewritten_query": "What is the emergency procedure for a fire?"}'
