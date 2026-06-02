"""Main Feynman Digital Twin Agent"""
import logging
import sys
from typing import Tuple
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from config import DATA_MARKDOWN, GEMINI_API_KEY, PRIMARY_MODEL
from rag_system import RAGSystem
from memory_system import MemoryManager
from personality import FeynmanPersonality, TeachingStyler, PersonalityAnalyzer


class FeynmanTwin:
    """Main Digital Twin Agent for Richard Feynman"""

    def __init__(self):
        """Initialize the Feynman Twin"""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        logger.info("Initializing Feynman Digital Twin...")

        # Initialize components
        self.rag_system = RAGSystem()
        self.memory_manager = MemoryManager()

        # Check if RAG system has data
        if not self.rag_system.load_processed_data():
            logger.warning("No processed data found. Please run data collection first.")
            self.rag_ready = False
        else:
            self.rag_ready = True

        logger.info("Feynman Twin initialized successfully")

    def _prepare_system_prompt(self, answer_length: str = "medium") -> str:
        """Prepare enhanced system prompt with context, length preference, and timeline awareness"""
        base_prompt = FeynmanPersonality.get_system_prompt()
        
        # Add timeline awareness
        current_date = datetime.now()
        current_year = current_date.year
        feynman_death_year = 1988
        years_since = current_year - feynman_death_year
        
        timeline_context = f"""

TIMELINE AWARENESS:
- Current date: {current_date.strftime('%B %d, %Y')}
- Richard Feynman passed away in 1988, {years_since} years ago
- You are a digital twin created to preserve Feynman's teaching style and knowledge
- When discussing current events, acknowledge the time gap: "In my time (1918-1988)..." or "Since my passing in 1988..."
- Be curious about modern developments in physics and technology
- Reference that you're speaking from knowledge up to 1988, but can discuss principles that remain timeless
"""
        
        base_prompt += timeline_context
        
        # Add length instructions
        length_instructions = {
            "brief": "\n\nIMPORTANT: Keep your response concise and to the point (2-3 paragraphs maximum). Focus on the core concept without extensive examples.",
            "medium": "\n\nIMPORTANT: Provide a balanced explanation with some examples (3-5 paragraphs). Make it clear but thorough.",
            "detailed": "\n\nIMPORTANT: Provide a comprehensive, in-depth explanation with multiple examples and analogies (5-8 paragraphs or more). Explore the concept deeply and thoroughly."
        }
        
        base_prompt += length_instructions.get(answer_length, length_instructions["medium"])

        # Add memory context if available
        memory_context = self.memory_manager.get_context_for_query()
        if memory_context:
            base_prompt += f"\n\nContext from previous interactions:\n{memory_context}"

        return base_prompt

    def answer_question(self, question: str, answer_length: str = "medium") -> Tuple[str, dict]:
        """
        Answer a question as Feynman would.
        
        Args:
            question: The question to answer
            answer_length: Length of answer - "brief", "medium", or "detailed"

        Returns:
            Tuple of (response_text, metadata)
        """
        logger.info(f"Processing question: {question} (length: {answer_length})")

        metadata = {
            "question": question,
            "retrieved_docs": 0,
            "personality_score": 0.0,
            "model_used": "unknown",
        }

        try:
            # Step 1: Retrieve relevant knowledge
            response = ""
            retrieved_docs = []

            if self.rag_ready:
                system_prompt = self._prepare_system_prompt(answer_length)
                response, retrieved_docs = self.rag_system.query(question, system_prompt)
                metadata["retrieved_docs"] = len(retrieved_docs)
            else:
                # Fallback if RAG not ready - use personality-based response
                logger.warning("RAG system not ready, using personality-based response")
                system_prompt = self._prepare_system_prompt(answer_length)
                response = self._generate_fallback_response(question, system_prompt)

            # Step 2: Enhance with teaching style
            response = TeachingStyler.add_personal_touch(response)

            # Step 3: Verify personality alignment
            personality_score = PersonalityAnalyzer.score_feynman_alignment(response)
            metadata["personality_score"] = personality_score

            # Step 4: Record in memory
            self.memory_manager.record_interaction(question, response)

            # Step 5: Extract and store insights
            self._extract_insights(question, response)

            logger.info(f"Response generated with personality score: {personality_score:.2f}")

            return response, metadata

        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return f"I encountered an unexpected error: {str(e)}", metadata

    def _generate_fallback_response(self, question: str, system_prompt: str) -> str:
        """Generate response without RAG (fallback mode)"""
        import google.generativeai as genai

        try:
            from config import PRIMARY_MODEL, FALLBACK_MODEL

            full_prompt = f"""{system_prompt}

User question: {question}

Generate a response that demonstrates Feynman's characteristic teaching style - clear, curious, and engaging."""

            try:
                model = genai.GenerativeModel(PRIMARY_MODEL)
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.warning(f"Primary model failed: {e}, using fallback")
                model = genai.GenerativeModel(FALLBACK_MODEL)
                response = model.generate_content(full_prompt)
                return response.text

        except Exception as e:
            logger.error(f"Error in fallback response: {e}")
            return "I apologize, but I'm having difficulty accessing my knowledge systems at the moment."

    def _extract_insights(self, question: str, response: str):
        """Extract and store key insights"""
        # Simple heuristic: if response contains key concepts, store as insight
        if len(response) > 200 and "understanding" in response.lower():
            insight = f"Discussion about: {question[:50]}..."
            self.memory_manager.persistent_memory.add_insight(insight)

    def interactive_session(self):
        """Run an interactive conversation session"""
        print("\n" + "=" * 70)
        print("Welcome to the Richard Feynman Digital Twin")
        print("=" * 70)
        print("\nYou can ask me about physics, science, learning, or anything else.")
        print("Type 'quit' to exit, 'memory' to see what I remember, or 'save' to save session.")
        print("-" * 70 + "\n")

        while True:
            try:
                question = input("You: ").strip()

                if not question:
                    continue

                if question.lower() == "quit":
                    self.memory_manager.save_session()
                    print("\nSession saved. Goodbye!")
                    break

                if question.lower() == "memory":
                    print("\n" + self.memory_manager.persistent_memory.get_memory_summary())
                    continue

                if question.lower() == "save":
                    session_file = self.memory_manager.save_session()
                    print(f"\nSession saved to {session_file}")
                    continue

                # Process question
                print("\nThinking...")
                response, metadata = self.answer_question(question)

                print(f"\nFeynman: {response}")
                print(f"\n[Personality alignment: {metadata['personality_score']:.0%}]")
                print(f"[Retrieved {metadata['retrieved_docs']} relevant documents]")
                print("-" * 70 + "\n")

            except KeyboardInterrupt:
                print("\n\nSession interrupted. Saving...")
                self.memory_manager.save_session()
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {e}")
                print(f"Error: {e}")

    def batch_query(self, questions: list) -> list:
        """Process multiple questions"""
        results = []
        for question in questions:
            response, metadata = self.answer_question(question)
            results.append({
                "question": question,
                "response": response,
                "metadata": metadata,
            })
        return results

    def setup_rag(self) -> bool:
        """Initialize RAG system"""
        if not self.rag_system.load_processed_data():
            logger.error("Failed to load processed data. Run data collection first.")
            return False

        logger.info("Building embeddings database...")
        if self.rag_system.build_embeddings_db():
            self.rag_ready = True
            logger.info("RAG system ready!")
            return True
        else:
            logger.error("Failed to build embeddings database")
            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Feynman Digital Twin - Chat with Richard Feynman's AI"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup RAG system (collect data and build embeddings)",
    )
    parser.add_argument(
        "--ocr-pdfs",
        action="store_true",
        help="OCR scanned PDFs into Markdown before setup",
    )
    parser.add_argument(
        "--ocr-engine",
        choices=["tesseract", "gemini"],
        default="tesseract",
        help="OCR engine to use for scanned PDFs",
    )
    parser.add_argument(
        "--tesseract-cmd",
        help="Path to tesseract.exe if it is not on PATH",
    )
    parser.add_argument(
        "--ocr-force",
        action="store_true",
        help="Re-OCR cached PDF page batches",
    )
    parser.add_argument(
        "--ocr-pages-per-request",
        type=int,
        default=5,
        help="PDF pages to OCR per Gemini request",
    )
    parser.add_argument(
        "--ocr-pause",
        type=float,
        default=13.0,
        help="Seconds to pause between OCR requests",
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Ask a single question and exit",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive conversation (default)",
    )

    args = parser.parse_args()

    try:
        # Initialize Twin
        twin = FeynmanTwin()

        if args.setup:
            logger.info("Setting up RAG system...")
            from data_collector import DataCollector

            if args.ocr_pdfs:
                logger.info("OCRing scanned PDFs into Markdown...")
                from ocr_to_markdown import (
                    GeminiMarkdownOCR,
                    PdfMarkdownConverter,
                    TesseractMarkdownOCR,
                    iter_pdf_paths,
                )

                if args.ocr_engine == "gemini":
                    ocr_engine = GeminiMarkdownOCR(
                        model_name=PRIMARY_MODEL,
                        dpi=180,
                        pause_seconds=args.ocr_pause,
                    )
                else:
                    ocr_engine = TesseractMarkdownOCR(
                        dpi=180,
                        pause_seconds=args.ocr_pause,
                        tesseract_cmd=args.tesseract_cmd,
                    )

                converter = PdfMarkdownConverter(ocr_engine)
                for pdf_path in iter_pdf_paths([]):
                    converter.convert_pdf(
                        pdf_path=pdf_path,
                        output_dir=DATA_MARKDOWN,
                        start_page=1,
                        end_page=None,
                        force=args.ocr_force,
                        retries=3,
                        pages_per_request=args.ocr_pages_per_request,
                    )

            # Collect data
            collector = DataCollector()
            collector.collect_all()
            collector.save_raw_data()
            processed = collector.process_documents()
            collector.save_processed_data(processed)

            # Build embeddings
            if twin.setup_rag():
                print("[OK] RAG system setup complete!")
            else:
                print("[ERROR] Failed to setup RAG system")
                sys.exit(1)

        elif args.query:
            # Single query mode
            print(f"Question: {args.query}\n")
            response, metadata = twin.answer_question(args.query)
            print(f"Feynman: {response}\n")
            print(f"[Personality score: {metadata['personality_score']:.0%}]")

        else:
            # Default to interactive mode
            args.interactive = True

        if args.interactive:
            twin.interactive_session()

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
