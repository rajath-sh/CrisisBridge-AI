import asyncio
import json
from ai_core.main import process_query
from shared.schemas import AIProcessRequest

async def test_pipeline():
    print("--- Testing CrisisBridge AI Multi-Agent Pipeline (MOCK MODE) ---")
    print("-" * 60)
    
    # Create a dummy request
    request = AIProcessRequest(
        query="Help! there is a plane crash on the hotel? i am a guest in the room 302",
        session_id="test-session-123"
    )
    
    # Run the pipeline
    try:
        response = await process_query(request)
        
        # Print the beautiful results
        print(f"SUCCESS: PIPELINE EXECUTED!")
        print(f"\nUser Query: {request.query}")
        print(f"AI Answer: \n{response.answer}")
        print(f"\nConfidence Score: {response.confidence}")
        print(f"Sources: {response.sources}")
        print(f"Explanation: {response.explanation}")
        
        print(f"\nAgent Trace (How the AI thought):")
        for agent_name, step_info in response.agent_trace.items():
            print(f"  - {agent_name}: {step_info['output']} ({step_info['time_ms']}ms)")
            
    except Exception as e:
        print(f"FAILED: PIPELINE ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
