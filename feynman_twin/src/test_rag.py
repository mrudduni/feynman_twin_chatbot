"""Test RAG system retrieval"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_system import RAGSystem

# Initialize RAG
print("Initializing RAG system...")
rag = RAGSystem()

# Load data
print("Loading processed data...")
if not rag.load_processed_data():
    print("Failed to load data!")
    sys.exit(1)

print(f"Loaded {len(rag.processed_docs)} documents")

# Check collection
if rag.collection:
    count = rag.collection.count()
    print(f"ChromaDB collection has {count} documents")
else:
    print("ERROR: Collection is None!")
    sys.exit(1)

# Test retrieval
print("\nTesting retrieval...")
query = "What is quantum entanglement?"
print(f"Query: {query}")

# Get query embedding
print("Getting query embedding...")
query_embedding = rag.get_embedding(query, task_type="retrieval_query")
if query_embedding:
    print(f"Query embedding: {len(query_embedding)} dimensions")
else:
    print("ERROR: Failed to get query embedding!")
    sys.exit(1)

# Try direct ChromaDB query
print("\nDirect ChromaDB query...")
try:
    results = rag.collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["documents", "distances", "metadatas"]
    )
    
    print(f"Results found: {len(results['documents'][0]) if results['documents'] else 0}")
    
    if results['documents'] and len(results['documents'][0]) > 0:
        print("\nFirst result:")
        print(f"  Distance: {results['distances'][0][0]}")
        print(f"  Text preview: {results['documents'][0][0][:100]}...")
        print(f"  Metadata: {results['metadatas'][0][0]}")
    else:
        print("No results found!")
        
except Exception as e:
    print(f"ERROR during query: {e}")
    import traceback
    traceback.print_exc()

# Test retrieve method
print("\nTesting retrieve() method...")
retrieved = rag.retrieve(query, top_k=5)
print(f"Retrieved: {len(retrieved)} documents")

if retrieved:
    print("\nFirst retrieved doc:")
    print(f"  Relevance: {retrieved[0]['relevance']}")
    print(f"  Distance: {retrieved[0]['distance']}")
    print(f"  Text preview: {retrieved[0]['text'][:100]}...")
else:
    print("No documents retrieved!")

print("\nTest complete!")
