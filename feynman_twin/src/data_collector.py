"""Automated data collection for Feynman materials"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import DATA_MARKDOWN, DATA_RAW, DATA_PROCESSED, FEYNMAN_SOURCES


class DataCollector:
    """Collects Feynman-related materials from various sources"""

    def __init__(self):
        self.raw_data = []
        self.metadata = {
            "collected_at": datetime.now().isoformat(),
            "sources": [],
            "total_documents": 0,
        }

    def collect_pdfs(self, pdf_folder: Path = None) -> List[Dict]:
        """Collect and extract text from PDF files"""
        if pdf_folder is None:
            pdf_folder = Path(__file__).parent.parent  # Project root

        logger.info(f"Searching for PDFs in: {pdf_folder}")
        pdf_data = []

        try:
            pdf_files = list(pdf_folder.glob("*.pdf"))
            logger.info(f"Found {len(pdf_files)} PDF files")

            for pdf_path in pdf_files:
                try:
                    logger.info(f"Extracting text from: {pdf_path.name}")
                    reader = PdfReader(pdf_path)
                    
                    # Extract text from all pages
                    text_content = ""
                    for page_num, page in enumerate(reader.pages):
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += page.extract_text()
                    
                    pdf_data.append({
                        "source": "pdf",
                        "title": pdf_path.stem,
                        "filename": pdf_path.name,
                        "content": text_content,
                        "page_count": len(reader.pages),
                        "file_path": str(pdf_path),
                    })
                    logger.info(f"Successfully extracted {len(reader.pages)} pages from {pdf_path.name}")
                except Exception as e:
                    logger.error(f"Error extracting text from {pdf_path.name}: {e}")

        except Exception as e:
            logger.error(f"Error accessing PDF folder: {e}")

        return pdf_data

    def create_feynman_knowledge_base(self) -> List[Dict]:
        """Create a curated knowledge base of Feynman's key ideas"""
        logger.info("Creating curated Feynman knowledge base")

        knowledge = [
            {
                "source": "feynman_principles",
                "topic": "The Feynman Technique",
                "content": """The Feynman Technique is a method of learning and understanding concepts by:
1. Choose a concept and study it
2. Explain it in simple terms as if teaching a child
3. Identify gaps in your understanding
4. Simplify and use analogies to fill gaps
5. Refine your explanation

Feynman believed that true understanding means being able to explain something simply without jargon.""",
            },
            {
                "source": "feynman_principles",
                "topic": "Nature of Science",
                "content": """According to Feynman, science is based on:
- Careful observation and experimentation
- Hypothesis testing, not just theory
- Willingness to be wrong and learn from mistakes
- Healthy skepticism even of established ideas
- The principle that nature, not human authority, is the ultimate judge

Feynman emphasized: "The first principle is that you must not fool yourself, and you are the easiest person to fool." """,
            },
            {
                "source": "feynman_principles",
                "topic": "Teaching Philosophy",
                "content": """Feynman's approach to teaching emphasized:
- Starting with fundamentals and building up
- Using everyday examples to explain complex concepts
- Encouraging questions and curiosity
- Avoiding memorization in favor of understanding
- Making learning enjoyable and playful
- Connecting abstract concepts to real-world phenomena

He famously said: "If you can't explain it simply, you don't understand it well enough." """,
            },
            {
                "source": "feynman_principles",
                "topic": "Quantum Mechanics Insights",
                "content": """Feynman's contributions to quantum mechanics include:
- Feynman diagrams: pictorial representations of particle interactions
- Path integral formulation: alternative way to formulate quantum mechanics
- QED (Quantum Electrodynamics): refined understanding of electromagnetic interactions
- Emphasized that quantum mechanics works perfectly but is counterintuitive
- "If you think you understand quantum mechanics, you don't understand quantum mechanics." """,
            },
            {
                "source": "feynman_principles",
                "topic": "Curiosity and Wonder",
                "content": """Feynman maintained childlike curiosity throughout his life:
- Believed in the joy of finding things out
- Would explore problems across many disciplines
- Valued questions over answers
- Approached problems with playfulness and humor
- Encouraged others to maintain sense of wonder about nature

He said: "The principle of science is that all knowledge is uncertain." """,
            },
        ]

        logger.info(f"Created {len(knowledge)} curated knowledge items")
        return knowledge

    def collect_markdown(self, markdown_folder: Path = None) -> List[Dict]:
        """Collect OCR Markdown files generated from scanned PDFs"""
        if markdown_folder is None:
            markdown_folder = DATA_MARKDOWN

        logger.info(f"Searching for Markdown files in: {markdown_folder}")
        markdown_data = []

        try:
            markdown_files = sorted(markdown_folder.glob("*.md"))
            logger.info(f"Found {len(markdown_files)} Markdown files")

            for markdown_path in markdown_files:
                try:
                    content = markdown_path.read_text(encoding="utf-8")
                    if not content.strip():
                        logger.warning(f"Skipping empty Markdown file: {markdown_path.name}")
                        continue

                    markdown_data.append({
                        "source": "markdown",
                        "title": markdown_path.stem,
                        "filename": markdown_path.name,
                        "content": content,
                        "file_path": str(markdown_path),
                    })
                    logger.info(f"Loaded Markdown file: {markdown_path.name}")
                except Exception as e:
                    logger.error(f"Error loading Markdown file {markdown_path.name}: {e}")

        except Exception as e:
            logger.error(f"Error accessing Markdown folder: {e}")

        return markdown_data

    def collect_pdfs(self, pdf_folder: Path = None) -> List[Dict]:
        """Collect and extract text from PDF files"""
        if pdf_folder is None:
            pdf_folder = Path(__file__).parent.parent  # Project root

        logger.info(f"Searching for PDFs in: {pdf_folder}")
        pdf_data = []

        try:
            pdf_files = list(pdf_folder.glob("*.pdf"))
            logger.info(f"Found {len(pdf_files)} PDF files")

            for pdf_path in pdf_files:
                try:
                    logger.info(f"Extracting text from: {pdf_path.name}")
                    reader = PdfReader(pdf_path)
                    
                    # Extract text from all pages
                    text_content = ""
                    for page_num, page in enumerate(reader.pages):
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += page.extract_text()
                    
                    pdf_data.append({
                        "source": "pdf",
                        "title": pdf_path.stem,
                        "filename": pdf_path.name,
                        "content": text_content,
                        "page_count": len(reader.pages),
                        "file_path": str(pdf_path),
                    })
                    logger.info(f"Successfully extracted {len(reader.pages)} pages from {pdf_path.name}")
                except Exception as e:
                    logger.error(f"Error extracting text from {pdf_path.name}: {e}")

        except Exception as e:
            logger.error(f"Error accessing PDF folder: {e}")

        return pdf_data

    def collect_all(self) -> Dict:
        """Collect data from all sources"""
        logger.info("Starting comprehensive data collection")

        all_data = []

        # PDF files
        pdf_data = self.collect_pdfs()
        all_data.extend(pdf_data)
        self.metadata["sources"].append({"type": "pdf", "count": len(pdf_data)})

        # OCR Markdown files
        markdown_data = self.collect_markdown()
        all_data.extend(markdown_data)
        self.metadata["sources"].append({"type": "markdown", "count": len(markdown_data)})

        # Curated knowledge
        knowledge = self.create_feynman_knowledge_base()
        all_data.extend(knowledge)
        self.metadata["sources"].append({"type": "curated", "count": len(knowledge)})

        self.metadata["total_documents"] = len(all_data)
        self.raw_data = all_data

        logger.info(f"Total documents collected: {len(all_data)}")
        return {"documents": all_data, "metadata": self.metadata}

    def save_raw_data(self) -> Path:
        """Save collected raw data"""
        output_file = DATA_RAW / "feynman_raw_data.json"
        data = {"documents": self.raw_data, "metadata": self.metadata}

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Raw data saved to {output_file}")
        return output_file

    def process_documents(self) -> List[Dict]:
        """Process raw documents into chunks for RAG"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )

        processed_docs = []

        for doc in self.raw_data:
            text = ""

            # Extract text based on source
            if doc.get("source") == "arxiv":
                text = f"{doc.get('title', '')}\n{doc.get('summary', '')}"
            elif doc.get("source") == "wikipedia":
                text = doc.get("content", "")
            elif doc.get("source") == "markdown":
                text = doc.get("content", "")
            elif doc.get("source") == "feynman_principles":
                text = f"{doc.get('topic', '')}\n{doc.get('content', '')}"

            if not text:
                continue

            # Split into chunks
            chunks = splitter.split_text(text)

            for i, chunk in enumerate(chunks):
                processed_docs.append({
                    "text": chunk,
                    "source": doc.get("source"),
                    "title": doc.get("title", doc.get("topic", "Unknown")),
                    "chunk_id": i,
                    "metadata": {
                        "url": doc.get("url"),
                        "authors": doc.get("authors"),
                        "published": doc.get("published"),
                    },
                })

        logger.info(f"Processed into {len(processed_docs)} chunks")
        return processed_docs

    def save_processed_data(self, processed_docs: List[Dict]) -> Path:
        """Save processed documents"""
        output_file = DATA_PROCESSED / "feynman_processed_chunks.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(processed_docs, f, indent=2, ensure_ascii=False)

        logger.info(f"Processed data saved to {output_file}")
        return output_file


def main():
    """Run data collection"""
    collector = DataCollector()
    collector.collect_all()
    collector.save_raw_data()

    processed = collector.process_documents()
    collector.save_processed_data(processed)

    print("\n[OK] Data collection complete!")
    print(f"  - Raw documents: {len(collector.raw_data)}")
    print(f"  - Processed chunks: {len(processed)}")
    print(f"  - Sources: {collector.metadata['sources']}")


if __name__ == "__main__":
    main()
