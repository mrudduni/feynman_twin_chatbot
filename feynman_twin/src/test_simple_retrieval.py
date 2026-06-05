"""Simple test to verify retrieval is working"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.absolute()))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from rag_system import RAGSystem

def test_direct_retrieval():
    """Test RAG system retrieval directly without agent"""
    print("Initializing RAG system...")
    rag = RAGSystem()
    rag.load_processed_data()
    
    # Get collection stats
    if rag.collection:
        count = rag.collection.count()
        print(f"Collection has {count} documents")
    else:
        print("ERROR: Collection not initialized")
        return
    
    # Test retrieval
    query = "What is quantum mechanics?"
    print(f"\nQuery: {query}")
    
    docs = rag.retrieve(query, top_k=5)
    print(f"Retrieved {len(docs)} documents")
    
    if docs:
        print("\n✓ SUCCESS: RAG retrieval is working!")
        print(f"\nFirst document preview:")
        print(f"  Source: {docs[0]['metadata'].get('source', 'Unknown')}")
        print(f"  Title: {docs[0]['metadata'].get('title', 'Unknown')}")
        print(f"  Relevance: {docs[0]['relevance']:.3f}")
        print(f"  Text preview: {docs[0]['text'][:200]}...")
    else:
        print("\n✗ FAILED: No documents retrieved")

if __name__ == "__main__":
    test_direct_retrieval()
