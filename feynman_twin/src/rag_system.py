"""RAG System with ChromaDB and embeddings"""
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import (
    DATA_PROCESSED,
    EMBEDDINGS_DB,
    CHROMA_DB_NAME,
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
    EMBEDDING_MODEL_FALLBACK,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
)


class RAGSystem:
    """RAG (Retrieval-Augmented Generation) system for Feynman knowledge"""

    def __init__(self):
        """Initialize RAG system"""
        # API key verification will be handled by LangChain wrappers
        
        # Initialize ChromaDB with new client pattern
        self.client = chromadb.PersistentClient(
            path=str(EMBEDDINGS_DB),
            settings=Settings(anonymized_telemetry=False),
        )
        
        try:
            self.collection = self.client.get_or_create_collection(
                name=CHROMA_DB_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            self.collection = None

        self.processed_docs = []

    def load_processed_data(self) -> bool:
        """Load processed documents from file"""
        data_file = DATA_PROCESSED / "feynman_processed_chunks.json"
        
        if not data_file.exists():
            logger.error(f"Processed data not found at {data_file}")
            return False

        try:
            with open(data_file, "r", encoding="utf-8") as f:
                self.processed_docs = json.load(f)
            logger.info(f"Loaded {len(self.processed_docs)} documents")
            return True
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return False

    def reset_collection(self) -> bool:
        """Reset the ChromaDB collection before rebuilding embeddings"""
        try:
            self.client.delete_collection(name=CHROMA_DB_NAME)
        except Exception:
            pass

        try:
            self.collection = self.client.get_or_create_collection(
                name=CHROMA_DB_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            self.collection = None
            return False

    def get_embedding(self, text: str, task_type: str = "retrieval_document") -> Optional[List[float]]:
        """Get embedding for text using Gemini"""
        backend = os.getenv("EMBEDDING_BACKEND", "").strip().lower()
        if backend in {"local", "sentence-transformers", "st"}:
            return self.get_local_embedding(text)

        # Try primary model first
        models_to_try = [EMBEDDING_MODEL] + EMBEDDING_MODEL_FALLBACK
        
        max_attempts_per_model = int(os.getenv("EMBEDDING_MAX_ATTEMPTS_PER_MODEL", "4"))
        for model in models_to_try:
            attempt = 0
            while attempt < max_attempts_per_model:
                try:
                    embedder = GoogleGenerativeAIEmbeddings(
                        model=model,
                        google_api_key=GEMINI_API_KEY,
                        task_type=task_type,
                    )
                    embedding = embedder.embed_query(text)
                    logger.debug(f"Successfully used model {model} for embedding")
                    return embedding
                except Exception as e:
                    # Gemini can respond with 429 and a suggested retry delay.
                    delay_s = self.extract_retry_delay_seconds(e)
                    if delay_s is not None and attempt + 1 < max_attempts_per_model:
                        logger.warning(
                            "Embedding quota hit (%s). Waiting %ss then retrying (attempt %s/%s, model=%s)",
                            "429" if "429" in str(e) else "rate-limit",
                            delay_s,
                            attempt + 2,
                            max_attempts_per_model,
                            model,
                        )
                        time.sleep(delay_s)
                        attempt += 1
                        continue

                    logger.warning(f"Embedding model {model} failed: {e}")
                    break
        
        # If all models fail, log error and return None
        logger.error(f"All embedding models failed for text. Tried: {models_to_try}")
        return None

    def get_local_embedding(self, text: str) -> Optional[List[float]]:
        """Get an embedding locally using sentence-transformers (no API quota)."""
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            logger.error(
                "Local embedding requested but sentence-transformers is not installed: %s", e
            )
            return None

        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        if not hasattr(self, "_local_embedder"):
            self._local_embedder = SentenceTransformer(model_name)

        vector = self._local_embedder.encode(text, normalize_embeddings=True)
        return vector.tolist()

    @staticmethod
    def extract_retry_delay_seconds(error: Exception) -> Optional[int]:
        """Try to parse 'Please retry in Xs' from Gemini error messages."""
        message = str(error)
        # Example: "Please retry in 20.69608174s."
        match = re.search(r"retry in\s*([0-9.]+)s", message, flags=re.IGNORECASE)
        if not match:
            match = re.search(r"Please retry in\s*([0-9.]+)s", message, flags=re.IGNORECASE)
        if match:
            try:
                seconds = float(match.group(1))
                # Add a small buffer so we don't immediately hit the limit again.
                return max(1, int(seconds) + 2)
            except Exception:
                return None
        return None

    def build_embeddings_db(self, reset_collection: bool = False) -> bool:
        """Build vector embeddings database"""
        if not self.load_processed_data():
            return False

        logger.info("Building embeddings database...")

        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return False

            backend = os.getenv("EMBEDDING_BACKEND", "").strip().lower()
            if backend in {"local", "sentence-transformers", "st"}:
                # Local backend changes embedding space/dimensions, so rebuild cleanly.
                reset_collection = True

            # Resume mode by default: keep existing vectors and only add missing IDs.
            # If caller explicitly requests reset, wipe and rebuild.
            should_reset = reset_collection
            if not should_reset:
                try:
                    existing_count = self.collection.count()
                except Exception:
                    existing_count = 0
                should_reset = existing_count == 0

            if should_reset:
                if not self.reset_collection():
                    return False

            # Add documents in batches
            batch_size = 10
            total_added = 0
            for i in range(0, len(self.processed_docs), batch_size):
                batch = self.processed_docs[i : i + batch_size]
                
                ids = []
                texts = []
                embeddings = []
                metadatas = []

                # First compute IDs and determine which ones already exist in Chroma,
                # so we don't burn embedding quota on vectors we already have.
                batch_items = []
                batch_ids = []
                for doc in batch:
                    text = doc.get("text", "")
                    if not text:
                        continue
                    doc_id = f"{doc.get('source')}_{doc.get('title')}_{doc.get('chunk_id')}"
                    batch_items.append((doc, doc_id, text))
                    batch_ids.append(doc_id)

                existing_ids = set()
                if batch_ids:
                    try:
                        # Returns only ids that exist.
                        existing = self.collection.get(ids=batch_ids, include=[])
                        existing_ids = set(existing.get("ids", []) or [])
                    except Exception:
                        # If get(ids=...) isn't supported as expected, we fall back to
                        # embedding everything in the batch (slower, but robust).
                        existing_ids = set()

                for doc, doc_id, text in batch_items:
                    if doc_id in existing_ids:
                        continue

                    embedding = self.get_embedding(text)
                    if not embedding:
                        continue

                    ids.append(doc_id)
                    texts.append(text)
                    embeddings.append(embedding)
                    metadatas.append({
                        "source": doc.get("source", ""),
                        "title": doc.get("title", ""),
                        "chunk_id": str(doc.get("chunk_id", 0)),
                    })

                if ids:
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=texts,
                        metadatas=metadatas,
                    )
                    total_added += len(ids)
                    logger.info(f"Added batch {i // batch_size + 1}/{len(self.processed_docs) // batch_size + 1}")

            if total_added == 0:
                logger.error("No embeddings were created; embeddings database was not built")
                return False

            logger.info("Embeddings database built successfully")
            return True

        except Exception as e:
            logger.error(f"Error building embeddings database: {e}")
            return False

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        if not self.collection:
            logger.error("Collection not initialized")
            return []

        try:
            query_embedding = self.get_embedding(query, task_type="retrieval_query")
            if not query_embedding:
                return []

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "distances", "metadatas"],
            )

            # Format results
            retrieved = []
            for i, doc in enumerate(results["documents"][0]):
                retrieved.append({
                    "text": doc,
                    "distance": results["distances"][0][i],
                    "relevance": max(0, 1 - results["distances"][0][i]),
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })

            return retrieved

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def generate_response(
        self,
        query: str,
        retrieved_docs: List[Dict],
        system_prompt: str = "",
    ) -> str:
        """Generate response using Gemini with retrieved context"""
        try:
            # Build context from retrieved documents
            context = "\n\n".join([
                f"Source: {doc['metadata'].get('source', 'Unknown')}\n"
                f"Title: {doc['metadata'].get('title', 'Unknown')}\n"
                f"Content: {doc['text']}"
                for doc in retrieved_docs
            ])

            # Build full prompt
            full_prompt = f"""You are Richard Feynman, a brilliant physicist and educator.  
{system_prompt}

Here is relevant knowledge from Feynman's works and related materials:

{context}

User question: {query}

Please respond in Feynman's characteristic style - clear, thoughtful, often using analogies and everyday examples. 
Be willing to admit uncertainty and maintain his emphasis on understanding over memorization."""

            # Try primary model first
            try:
                llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
                response = llm.invoke(full_prompt)
                return response.content
            except Exception as e:
                logger.warning(f"Primary model ({PRIMARY_MODEL}) failed: {e}, trying fallback")
                # Use fallback model
                llm = ChatGoogleGenerativeAI(model=FALLBACK_MODEL, google_api_key=GEMINI_API_KEY)
                response = llm.invoke(full_prompt)
                return response.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {str(e)}"

    def query(self, question: str, system_prompt: str = "") -> Tuple[str, List[Dict]]:
        """Complete RAG pipeline: retrieve and generate"""
        logger.info(f"Processing query: {question}")

        # Retrieve relevant documents
        retrieved = self.retrieve(question, top_k=5)

        if not retrieved:
            logger.warning("No documents retrieved")
            response = "I couldn't find relevant information in my knowledge base to answer that."
        else:
            # Generate response with context
            response = self.generate_response(question, retrieved, system_prompt)

        return response, retrieved
    
    def get_stats(self):
        """Returns statistics about the loaded knowledge base."""
        return {
            "total_documents": len(self.documents) if hasattr(self, 'documents') else 0,
            "status": "ready"
        }  

def main():
    """Initialize RAG system"""
    rag = RAGSystem()
    
    # Build the embeddings database
    if rag.build_embeddings_db():
        print("[OK] RAG system initialized successfully!")
        
        # Test with a sample query
        response, docs = rag.query("What is the Feynman Technique?")
        print(f"\nTest Query Response:\n{response}")
    else:
        print("[ERROR] Failed to initialize RAG system")


if __name__ == "__main__":
    main()
