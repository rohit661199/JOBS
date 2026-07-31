"""Parser module for reading master resumes in PDF or DOCX formats."""
import hashlib
from pathlib import Path
import fitz  # PyMuPDF
import docx
from utils.logger import logger


class ResumeParser:
    """Parses raw text and generates SHA256 fingerprints from resume files."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extracts full text content from PDF or DOCX file.

        Args:
            file_path: Path to resume file.

        Returns:
            Extracted text content.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found at: {file_path}")

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return ResumeParser._parse_pdf(path)
        elif suffix in [".docx", ".doc"]:
            return ResumeParser._parse_docx(path)
        elif suffix == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported resume file extension: {suffix}")

    @staticmethod
    def _parse_pdf(path: Path) -> str:
        text_chunks = []
        try:
            doc = fitz.open(str(path))
            for page in doc:
                text_chunks.append(page.get_text())
            doc.close()
            full_text = "\n".join(text_chunks).strip()
            logger.info(f"Extracted {len(full_text)} chars from PDF resume: {path.name}")
            return full_text
        except Exception as e:
            logger.error(f"Error parsing PDF resume {path}: {e}")
            raise

    @staticmethod
    def _parse_docx(path: Path) -> str:
        try:
            doc = docx.Document(str(path))
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            logger.info(f"Extracted {len(full_text)} chars from DOCX resume: {path.name}")
            return full_text
        except Exception as e:
            logger.error(f"Error parsing DOCX resume {path}: {e}")
            raise

    @staticmethod
    def get_text_hash(text: str) -> str:
        """Computes SHA256 hex digest of raw resume text for deduplication caching."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
