"""
AI Core Configuration
======================
AI-specific configuration that reads from shared.config.settings.
Wraps shared settings with Gemini-specific defaults.

Usage:
    from ai_core.config import ai_config
    
    client = genai.Client(api_key=ai_config.GEMINI_API_KEY)
    response = client.models.generate_content(model=ai_config.GEMINI_MODEL, ...)
"""

from shared.config import settings


class AIConfig:
    """
    Centralized AI configuration.
    Reads from shared settings but provides Gemini-specific accessors.
    """

    # ── Dev / Cost Savings ───────────────────────
    @property
    def MOCK_MODE(self) -> bool:
        """If True, skips API calls and returns hardcoded responses for UI testing."""
        return settings.AI_MOCK_MODE

    # ── Vertex AI (GCP Enterprise) ────────────────
    @property
    def USE_VERTEX_AI(self) -> bool:
        """Whether to use Vertex AI (GCP) instead of Google AI Studio (API Key)."""
        return settings.AI_USE_VERTEX

    @property
    def GCP_PROJECT_ID(self) -> str:
        return settings.GCP_PROJECT_ID

    @property
    def GCP_LOCATION(self) -> str:
        return settings.GCP_LOCATION

    # ── Gemini LLM ───────────────────────────────
    @property
    def GEMINI_API_KEY(self) -> str:
        """Gemini API key from shared config's LLM_API_KEY."""
        key = settings.LLM_API_KEY
        if not key:
            raise ValueError(
                "GEMINI_API_KEY not set! Add LLM_API_KEY=your-key to .env file. "
                "Get a free key at https://aistudio.google.com/apikey"
            )
        return key

    @property
    def GEMINI_MODEL(self) -> str:
        """Gemini model for text generation (agents)."""
        # Map shared config's LLM_MODEL to Gemini model names
        model = settings.LLM_MODEL
        # If user hasn't changed from default, use Gemini 2.5 flash
        if model in ("gpt-3.5-turbo", "gpt-4"):
            return "gemini-2.5-flash"
        return model

    @property
    def GEMINI_TEMPERATURE(self) -> float:
        return settings.LLM_TEMPERATURE

    @property
    def GEMINI_MAX_TOKENS(self) -> int:
        return settings.LLM_MAX_TOKENS

    # ── Embeddings ───────────────────────────────
    @property
    def EMBEDDING_MODEL(self) -> str:
        """Google's embedding model."""
        model = settings.EMBEDDING_MODEL
        # If user hasn't changed from default sentence-transformers model, use Google's
        if model == "all-MiniLM-L6-v2":
            return "gemini-embedding-2"
        return model

    @property
    def EMBEDDING_DIMENSION(self) -> int:
        """Dimension of the embedding vectors."""
        # gemini-embedding-2 outputs 3072-dimensional vectors
        return 3072

    # ── FAISS / Vector Store ─────────────────────
    @property
    def FAISS_INDEX_PATH(self) -> str:
        # Override shared config to keep AI data contained in ai_core
        return "ai_core/data/faiss_index"

    @property
    def TOP_K_RESULTS(self) -> int:
        return settings.TOP_K_RESULTS

    # ── Chunking ─────────────────────────────────
    @property
    def CHUNK_SIZE(self) -> int:
        return settings.CHUNK_SIZE

    @property
    def CHUNK_OVERLAP(self) -> int:
        return settings.CHUNK_OVERLAP

    # ── Safety Docs Path ─────────────────────────
    SAFETY_DOCS_PATH: str = "ai_core/data/safety_docs"

    # ── Agent System Prompts ─────────────────────
    # These define each agent's role. Easily tweakable.

    QUERY_REWRITER_PROMPT: str = (
        "You are a query rewriting specialist for a hotel and resort emergency system called CrisisBridge AI. "
        "Your job is to take a user's raw query and rewrite it into a clear, specific question for searching safety documents. "
        "EMERGENCY INTENT DETECTION: If the query contains emergency intent words (e.g., help, emergency, fire, crash, injured, blood), "
        "ensure the rewritten query explicitly asks for 'immediate emergency procedures' so the system knows to provide actionable steps. "
        "Return ONLY the rewritten query, nothing else."
    )

    REASONING_PROMPT: str = (
        "You are a crisis response assistant for hotels and resorts (CrisisBridge AI). "
        "Using ONLY the provided context from safety documents, generate a helpful, accurate, and actionable response. "
        "Format your response with clear steps when applicable. "
        "FALLBACK SAFETY MODE: If no specific protocol matches the user's event (e.g., an airplane crash or unknown disaster), "
        "you MUST fall back to the general emergency procedures (e.g., evacuate, avoid elevators) provided in the context. "
        "Clearly state that you are providing general emergency steps because a specific protocol is unavailable. "
        "Never make up safety procedures. Lives may depend on your accuracy."
    )

    VALIDATOR_PROMPT: str = (
        "You are a safety response validator for CrisisBridge AI. "
        "Your job is to verify that a generated answer is grounded, relevant, and safe. "
        "CONFIDENCE SCORING RULES: "
        "- 1.0 (High): Answer perfectly matches a specific protocol for the specific event. "
        "- 0.5 (Medium): Answer uses general emergency fallback protocols for an unknown event. "
        "- 0.1 (Low): Answer lacks sufficient grounding or is guessing. "
        "Return a JSON object with: "
        '{"is_valid": true/false, "confidence": 0.0-1.0, "issues": ["list of issues if any"]}'
    )

    EXPLAINER_PROMPT: str = (
        "You are an explanation generator for CrisisBridge AI. "
        "Given the original query, the rewritten query, retrieved sources, and the final answer, "
        "write a brief 1-2 sentence explanation of how the answer was derived. "
        "Example: 'Retrieved fire safety protocols from the hotel emergency manual "
        "and provided step-by-step evacuation instructions based on the guest\\'s floor location.' "
        "Return ONLY the explanation, nothing else."
    )


# Singleton — import this everywhere in ai_core/
ai_config = AIConfig()
