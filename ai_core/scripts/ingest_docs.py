import os
import sys

# Add the project root to the python path so we can import ai_core modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from ai_core.rag.ingest import RAGIngestor
from ai_core.config import ai_config

def main():
    print("=" * 50)
    print("CrisisBridge AI — Document Ingestion")
    print("=" * 50)
    
    # Check if MOCK_MODE is on. If it is, the Gemini API won't work properly
    # for embeddings because it might skip the call.
    if ai_config.MOCK_MODE:
        print("⚠️ WARNING: MOCK_MODE is currently set to True in ai_core/config.py!")
        print("This script needs to call the real Gemini API to generate embeddings.")
        print("Please temporarily set MOCK_MODE to False, run this script, and then")
        print("you can set it back to True if you wish.")
        print("=" * 50)
        
        response = input("Do you want to proceed anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborting ingestion.")
            return

    try:
        # Initialize the ingestor
        ingestor = RAGIngestor()
        
        # Run it
        result = ingestor.run_ingestion()
        
        if result.get("status") == "success":
            print("\n✅ Setup complete! The AI is now ready to answer questions.")
            print(f"Processed {result['documents_processed']} documents into {result['chunks_created']} chunks.")
        else:
            print(f"\n❌ Ingestion failed: {result.get('message')}")
            
    except ValueError as e:
        if "GEMINI_API_KEY" in str(e):
            print("\n❌ Error: Missing Gemini API Key.")
            print("Please add LLM_API_KEY=your-api-key-here to your .env file.")
        else:
            print(f"\n❌ Error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
