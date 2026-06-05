"""Test script to verify agent metadata is being returned correctly"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.absolute()))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from agent_graph import run_agent
from rag_system import RAGSystem
from memory_system import MemoryManager

def test_agent_metadata():
    """Test that agent returns metadata with retrieved_docs"""
    print("Initializing RAG system...")
    rag_system = RAGSystem()
    rag_system.load_processed_data()
    
    print("Initializing Memory Manager...")
    memory_manager = MemoryManager()
    
    print("\nTesting agent with a physics question...")
    system_prompt = "You are Richard Feynman."
    
    # Test with a more technical question that should trigger retrieval
    response, metadata = run_agent(
        query="Explain the double slit experiment and wave-particle duality in detail",
        system_prompt=system_prompt,
        rag_system=rag_system,
        memory_manager=memory_manager,
        chat_history=None
    )
    
    print(f"\n{'='*60}")
    print("AGENT RESPONSE:")
    print(f"{'='*60}")
    print(response[:200] + "..." if len(response) > 200 else response)
    
    print(f"\n{'='*60}")
    print("METADATA:")
    print(f"{'='*60}")
    print(f"Full metadata object: {metadata}")
    print(f"Type: {type(metadata)}")
    print(f"Keys: {metadata.keys() if isinstance(metadata, dict) else 'Not a dict'}")
    
    if isinstance(metadata, dict):
        print(f"\nretrieved_docs: {metadata.get('retrieved_docs', 'NOT FOUND')}")
        print(f"personality_score: {metadata.get('personality_score', 'NOT FOUND')}")
        print(f"model_used: {metadata.get('model_used', 'NOT FOUND')}")
    
    print(f"\n{'='*60}")
    
    # Verify
    if metadata.get('retrieved_docs', 0) > 0:
        print("✓ SUCCESS: retrieved_docs is properly set in metadata!")
    else:
        print("✗ FAILED: retrieved_docs is 0 or missing from metadata")
        print("  This is the bug we need to fix.")

if __name__ == "__main__":
    test_agent_metadata()
