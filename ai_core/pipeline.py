import asyncio
import time
import logging
from typing import Dict, Any
from shared.schemas import AIProcessRequest, AIProcessResponse
from ai_core.agents.query_rewriter import QueryRewriterAgent
from ai_core.agents.retriever_agent import RetrieverAgent
from ai_core.agents.reasoning_agent import ReasoningAgent
from ai_core.agents.validator_agent import ValidatorAgent
from ai_core.agents.explainer_agent import ExplainerAgent

logger = logging.getLogger(__name__)

class MultiAgentPipeline:
    """
    Orchestrates the 5 AI agents.
    Executes sequential tasks (Rewrite -> Retrieve -> Reason)
    and parallel tasks (Validate + Explain).
    """

    def __init__(self):
        self.rewriter = QueryRewriterAgent()
        self.retriever = RetrieverAgent()
        self.reasoner = ReasoningAgent()
        self.validator = ValidatorAgent()
        self.explainer = ExplainerAgent()

    async def process(self, request: AIProcessRequest) -> AIProcessResponse:
        logger.info(f"Starting pipeline for query: '{request.query}'")
        agent_trace = {}
        
        try:
            # 1. Query Rewriter (Sequential)
            t0 = time.time()
            rewritten_query = await self.rewriter.execute(request.query, request.session_history)
            agent_trace["QueryRewriter"] = {
                "time_ms": int((time.time()-t0)*1000), 
                "output": rewritten_query
            }
            
            # 2. Retriever (Sequential)
            t0 = time.time()
            retrieval_result = await self.retriever.execute(rewritten_query)
            context = retrieval_result["context"]
            sources = retrieval_result["sources"]
            agent_trace["Retriever"] = {
                "time_ms": int((time.time()-t0)*1000), 
                "output": f"Retrieved {len(sources)} sources."
            }
            
            # 3. Reasoning (Sequential)
            t0 = time.time()
            answer = await self.reasoner.execute(rewritten_query, context)
            agent_trace["Reasoning"] = {
                "time_ms": int((time.time()-t0)*1000), 
                "output": answer[:100] + ("..." if len(answer) > 100 else "")
            }
            
            # 4. Validate & Explain (Parallel)
            t_parallel = time.time()
            val_task = asyncio.create_task(self.validator.execute(rewritten_query, context, answer))
            exp_task = asyncio.create_task(self.explainer.execute(request.query, rewritten_query, sources, answer))
            
            validation_result, explanation = await asyncio.gather(val_task, exp_task)
            
            p_time = int((time.time()-t_parallel)*1000)
            agent_trace["Validator"] = {"time_ms": p_time, "output": validation_result}
            agent_trace["Explainer"] = {"time_ms": p_time, "output": explanation}
            
            return AIProcessResponse(
                answer=answer,
                sources=sources,
                confidence=validation_result.get("confidence", 0.0),
                explanation=explanation,
                rewritten_query=rewritten_query,
                agent_trace=agent_trace
            )
            
        except Exception as e:
            logger.error(f"Pipeline failure: {str(e)}", exc_info=True)
            return AIProcessResponse(
                answer="I encountered an error processing your request. If this is a life-threatening emergency, please dial 911 or contact the front desk (0) immediately.",
                sources=[],
                confidence=0.0,
                explanation=f"Pipeline error: {str(e)}",
                agent_trace=agent_trace
            )
