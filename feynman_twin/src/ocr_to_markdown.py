"""Convert scanned PDFs into Markdown using local OCR or Gemini vision OCR."""
import argparse
import logging
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Iterable, Optional

from dotenv import load_dotenv
import fitz
from google.api_core import exceptions as google_exceptions
import google.generativeai as genai


env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from config import DATA_MARKDOWN, GEMINI_API_KEY, PRIMARY_MODEL, PROJECT_ROOT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


OCR_PROMPT = """OCR these scanned book page images into clean Markdown.

Rules:
- Preserve the page's text, equations, section headings, problem numbers, captions, and lists.
- Do not summarize or explain.
- Do not invent missing words.
- Keep mathematical notation readable in Markdown or LaTeX-style text.
- For each image, start with a Markdown heading exactly like: ## Page N
- If a page has no readable text, include its heading and leave the content empty.
- Return only Markdown content for these pages."""


def safe_stem(filename: str) -> str:
    """Create a filesystem-friendly stem while preserving readability."""
    stem = Path(filename).stem
    stem = re.sub(r"[^\w.-]+", "_", stem)
    return stem.strip("_") or "document"


def normalize_tesseract_text(text: str, page_number: int) -> str:
    """Format raw Tesseract OCR text as page Markdown."""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return f"## Page {page_number}\n\n{cleaned}".strip()


def iter_pdf_paths(pdf_args: Iterable[str]) -> list[Path]:
    """Resolve requested PDFs or default to all project-root PDFs."""
    if pdf_args:
        return [Path(pdf_arg).resolve() for pdf_arg in pdf_args]
    return sorted(PROJECT_ROOT.glob("*.pdf"))


class GeminiMarkdownOCR:
    """OCR scanned PDF pages and write Markdown output."""

    def __init__(self, model_name: str, dpi: int, pause_seconds: float):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.dpi = dpi
        self.pause_seconds = pause_seconds

    def render_page_png(self, page: fitz.Page) -> bytes:
        """Render a PDF page to PNG bytes for OCR."""
        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        return pixmap.tobytes("png")

    def extract_response_text(self, response) -> str:
        """Read response text without failing on empty or blocked candidates."""
        try:
            return (response.text or "").strip()
        except Exception:
            pass

        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            return ""

        parts = getattr(getattr(candidates[0], "content", None), "parts", None) or []
        text_parts = [getattr(part, "text", "") for part in parts if getattr(part, "text", "")]
        return "\n".join(text_parts).strip()

    def ocr_pages(self, pages: list[tuple[int, fitz.Page]], retries: int) -> str:
        """OCR rendered pages with retry handling."""
        page_numbers = [str(page_number) for page_number, _ in pages]
        prompt = f"{OCR_PROMPT}\n\nThe images are pages: {', '.join(page_numbers)}."
        parts = [prompt]
        parts.extend(
            {"mime_type": "image/png", "data": self.render_page_png(page)}
            for _, page in pages
        )

        attempt = 1
        while attempt <= retries:
            try:
                response = self.model.generate_content(parts)
                return self.extract_response_text(response)
            except google_exceptions.ResourceExhausted as e:
                wait_seconds = self.extract_retry_delay(e) or 60
                logger.warning(
                    "OCR quota reached on pages %s; waiting %ss before retrying",
                    ", ".join(page_numbers),
                    wait_seconds,
                )
                time.sleep(wait_seconds)
            except Exception as e:
                if attempt >= retries:
                    raise
                wait_seconds = min(60, attempt * 5)
                logger.warning(
                    "OCR failed for pages %s on attempt %s/%s: %s; retrying in %ss",
                    ", ".join(page_numbers),
                    attempt,
                    retries,
                    e,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                attempt += 1

        return ""

    def extract_retry_delay(self, error: Exception) -> Optional[int]:
        """Extract retry delay seconds from a Gemini quota exception when present."""
        for detail in getattr(error, "details", []) or []:
            retry_delay = getattr(detail, "retry_delay", None)
            seconds = getattr(retry_delay, "seconds", None)
            if seconds:
                return int(seconds) + 2

        match = re.search(r"retry in ([0-9.]+)s", str(error), re.IGNORECASE)
        if match:
            return int(float(match.group(1))) + 2
        return None


class TesseractMarkdownOCR:
    """OCR scanned PDF pages locally with Tesseract."""

    @staticmethod
    def resolve_tesseract_cmd(user_supplied_cmd: Optional[str]) -> str:
        """Resolve a usable Tesseract executable path."""
        env_candidates = [
            os.getenv("TESSERACT_CMD"),
            os.getenv("TESSERACT_PATH"),
        ]
        candidates = [user_supplied_cmd, *env_candidates]

        which_cmd = shutil.which("tesseract")
        if which_cmd:
            candidates.append(which_cmd)

        if os.name == "nt":
            candidates.extend([
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                rf"{os.getenv('LOCALAPPDATA', '')}\Programs\Tesseract-OCR\tesseract.exe",
                rf"{os.getenv('USERPROFILE', '')}\scoop\apps\tesseract\current\tesseract.exe",
            ])

        for candidate in candidates:
            if not candidate:
                continue
            candidate_path = Path(candidate).expanduser()
            if candidate_path.is_file():
                return str(candidate_path)

        raise FileNotFoundError(
            "Tesseract executable not found. Install it and add to PATH, "
            "set TESSERACT_CMD/TESSERACT_PATH, or pass --tesseract-cmd."
        )

    def __init__(self, dpi: int, pause_seconds: float, tesseract_cmd: Optional[str] = None):
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = self.resolve_tesseract_cmd(tesseract_cmd)

        self.pytesseract = pytesseract
        self.dpi = dpi
        self.pause_seconds = pause_seconds

    def render_page_png(self, page: fitz.Page) -> bytes:
        """Render a PDF page to PNG bytes for OCR."""
        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        return pixmap.tobytes("png")

    def ocr_pages(self, pages: list[tuple[int, fitz.Page]], retries: int) -> str:
        """OCR pages locally and return Markdown."""
        page_markdown = []
        for page_number, page in pages:
            image_bytes = self.render_page_png(page)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
                image_file.write(image_bytes)
                image_file.flush()
                image_path = image_file.name
            try:
                text = self.pytesseract.image_to_string(image_path, lang="eng")
            finally:
                Path(image_path).unlink(missing_ok=True)
            page_markdown.append(normalize_tesseract_text(text, page_number))
        return "\n\n".join(page_markdown)


class RapidOCRMarkdownOCR:
    """OCR scanned PDF pages locally with RapidOCR."""

    def __init__(self, dpi: int, pause_seconds: float):
        from rapidocr_onnxruntime import RapidOCR

        self.ocr = RapidOCR()
        self.dpi = dpi
        self.pause_seconds = pause_seconds

    def render_page_png(self, page: fitz.Page) -> bytes:
        """Render a PDF page to PNG bytes for OCR."""
        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        return pixmap.tobytes("png")

    def extract_text(self, ocr_result) -> str:
        """Flatten RapidOCR output into plain text."""
        if not ocr_result:
            return ""

        if isinstance(ocr_result, tuple) and ocr_result:
            ocr_result = ocr_result[0]

        lines = []
        for item in ocr_result or []:
            candidate = None
            if isinstance(item, (list, tuple)):
                if len(item) >= 2 and isinstance(item[1], str):
                    candidate = item[1]
                elif len(item) >= 2 and isinstance(item[1], (list, tuple)) and item[1]:
                    first = item[1][0]
                    if isinstance(first, str):
                        candidate = first
                elif len(item) >= 1 and isinstance(item[0], str):
                    candidate = item[0]
            elif isinstance(item, str):
                candidate = item

            if candidate:
                lines.append(candidate.strip())

        return "\n".join(lines).strip()

    def ocr_pages(self, pages: list[tuple[int, fitz.Page]], retries: int) -> str:
        """OCR pages locally and return Markdown."""
        page_markdown = []
        for page_number, page in pages:
            image_bytes = self.render_page_png(page)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
                image_file.write(image_bytes)
                image_file.flush()
                image_path = image_file.name
            try:
                ocr_result = self.ocr(image_path)
            finally:
                Path(image_path).unlink(missing_ok=True)
            page_markdown.append(normalize_tesseract_text(self.extract_text(ocr_result), page_number))
        return "\n\n".join(page_markdown)


class PdfMarkdownConverter:
    """Convert PDFs into Markdown with a selected OCR engine."""

    def __init__(self, ocr_engine):
        self.ocr_engine = ocr_engine

    def convert_pdf(
        self,
        pdf_path: Path,
        output_dir: Path,
        start_page: int,
        end_page: Optional[int],
        force: bool,
        retries: int,
        pages_per_request: int,
    ) -> Path:
        """OCR one PDF and combine page Markdown files into a book Markdown file."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        pages_dir = output_dir / ".pages" / safe_stem(pdf_path.name)
        pages_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir = output_dir / ".chunks" / safe_stem(pdf_path.name)
        chunks_dir.mkdir(parents=True, exist_ok=True)

        document = fitz.open(pdf_path)
        page_count = document.page_count
        last_page = min(end_page or page_count, page_count)

        if start_page < 1 or start_page > page_count:
            raise ValueError(f"start_page must be between 1 and {page_count}")
        if last_page < start_page:
            raise ValueError("end_page must be greater than or equal to start_page")

        logger.info(
            "OCR converting %s pages %s-%s of %s",
            pdf_path.name,
            start_page,
            last_page,
            page_count,
        )

        for batch_start in range(start_page, last_page + 1, pages_per_request):
            batch_end = min(batch_start + pages_per_request - 1, last_page)
            chunk_file = chunks_dir / f"pages_{batch_start:04d}_{batch_end:04d}.md"
            if chunk_file.exists() and not force:
                logger.info("Skipping existing pages %s-%s", batch_start, batch_end)
                continue

            pages = [
                (page_number, document.load_page(page_number - 1))
                for page_number in range(batch_start, batch_end + 1)
            ]
            logger.info(
                "OCR pages %s-%s/%s: %s",
                batch_start,
                batch_end,
                page_count,
                pdf_path.name,
            )
            text = self.ocr_engine.ocr_pages(pages, retries)
            chunk_file.write_text(text + "\n", encoding="utf-8")

            if self.ocr_engine.pause_seconds:
                time.sleep(self.ocr_engine.pause_seconds)

        output_file = output_dir / f"{safe_stem(pdf_path.name)}.md"
        self.write_combined_markdown(pdf_path, output_file, pages_dir, chunks_dir, page_count)
        logger.info("Markdown written to %s", output_file)
        return output_file

    def write_combined_markdown(
        self,
        pdf_path: Path,
        output_file: Path,
        pages_dir: Path,
        chunks_dir: Path,
        page_count: int,
    ) -> None:
        """Combine per-page Markdown into one document."""
        lines = [
            f"# {pdf_path.stem}",
            "",
            f"Source PDF: `{pdf_path.name}`",
            f"Total PDF pages: {page_count}",
            "",
        ]

        chunk_files = sorted(chunks_dir.glob("pages_*.md"))
        if chunk_files:
            for chunk_file in chunk_files:
                chunk_text = chunk_file.read_text(encoding="utf-8").strip()
                if chunk_text:
                    lines.extend([chunk_text, ""])
        else:
            page_files = sorted(pages_dir.glob("page_*.md"))
            for page_file in page_files:
                page_number = int(page_file.stem.split("_")[1])
                page_text = page_file.read_text(encoding="utf-8").strip()
                if not page_text:
                    continue

                lines.extend([
                    f"## Page {page_number}",
                    "",
                    page_text,
                    "",
                ])

        output_file.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OCR scanned PDFs into Markdown files for the RAG system."
    )
    parser.add_argument("pdfs", nargs="*", help="PDF files to OCR. Defaults to all PDFs in project root.")
    parser.add_argument("--engine", choices=["tesseract", "gemini"], default="tesseract")
    parser.add_argument("--output-dir", type=Path, default=DATA_MARKDOWN)
    parser.add_argument("--model", default=PRIMARY_MODEL)
    parser.add_argument("--tesseract-cmd", help="Path to tesseract.exe if it is not on PATH.")
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--end-page", type=int)
    parser.add_argument("--pages-per-request", type=int, default=5)
    parser.add_argument("--force", action="store_true", help="Re-OCR pages even if cached page Markdown exists.")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--pause", type=float, default=13.0, help="Seconds to wait between page OCR calls.")
    args = parser.parse_args()
    if args.pages_per_request < 1:
        parser.error("--pages-per-request must be at least 1")
    if args.retries < 1:
        parser.error("--retries must be at least 1")
    return args


def main() -> None:
    args = parse_args()
    if args.engine == "gemini":
        ocr_engine = GeminiMarkdownOCR(
            model_name=args.model,
            dpi=args.dpi,
            pause_seconds=args.pause,
        )
    else:
        ocr_engine = TesseractMarkdownOCR(
            dpi=args.dpi,
            pause_seconds=args.pause,
            tesseract_cmd=args.tesseract_cmd,
        )

    converter = PdfMarkdownConverter(ocr_engine)

    pdf_paths = iter_pdf_paths(args.pdfs)
    if not pdf_paths:
        raise FileNotFoundError("No PDFs found to OCR")

    for pdf_path in pdf_paths:
        converter.convert_pdf(
            pdf_path=pdf_path,
            output_dir=args.output_dir,
            start_page=args.start_page,
            end_page=args.end_page,
            force=args.force,
            retries=args.retries,
            pages_per_request=args.pages_per_request,
        )

    print("[OK] OCR Markdown conversion complete")


if __name__ == "__main__":
    main()
